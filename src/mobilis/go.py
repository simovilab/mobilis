"""Textual TUI dashboard for ``mobilis go``.

This scaffold provides:
* feed discovery/load from Mobility Database metadata
* a "Trips by route" workflow
* a "Trips by stop" workflow
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Sequence
from difflib import SequenceMatcher
import shutil
import zipfile

import duckdb
import requests
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Select,
    TabbedContent,
    TabPane,
)

from .import_gtfs import import_gtfs
from .tabs import TransitSystemTabContent, TripsByRouteTabContent, TripsByStopTabContent

TODAY_ISO = date.today().isoformat()
PERSISTENT_NOTIFICATION_TIMEOUT = 3600.0


class MobilisGoApp(App):
    """Passenger-facing TUI scaffold backed by GTFS DuckDB feeds."""

    CSS_PATH = "styles/go.tcss"

    TITLE = "mobilis"
    SUB_TITLE = "Transit dashboard"
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "reload_all", "Reload"),
    ]

    db: duckdb.DuckDBPyConnection | None = None
    selected_feed: str | None = None
    selected_catalog_feed_id: str | None = None
    selected_downloaded_feed_id: str | None = None
    selected_feed_source: str | None = None
    selected_route_id_for_trips: str | None = None
    selected_route_id_for_stops: str | None = None
    selected_stop_id_for_arrivals: str | None = None
    feed_catalog_urls: dict[str, str] = {}
    feed_catalog_rows: list[tuple[str, str, str, str | None]] = []
    place_search_rows: list[tuple[str, str, float, float]] = []
    selected_place_row_id: str | None = None

    def _notify_warning(self, message: str) -> None:
        self.notify(
            message,
            severity="warning",
            timeout=PERSISTENT_NOTIFICATION_TIMEOUT,
        )

    def _notify_error(self, message: str) -> None:
        self.notify(
            message,
            severity="error",
            timeout=PERSISTENT_NOTIFICATION_TIMEOUT,
        )

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with TabbedContent(initial="transit-system", id="top-menu"):
            with TabPane("Transit System", id="transit-system"):
                yield TransitSystemTabContent(id="transit-layout")
            with TabPane("Trips by route", id="trips-by-route"):
                yield TripsByRouteTabContent(id="route-layout")
            with TabPane("Trips by stop", id="trips-by-stop"):
                yield TripsByStopTabContent(id="stop-layout")
        yield Footer()

    def on_mount(self) -> None:
        self.feed_catalog_urls = {}
        self.feed_catalog_rows = []
        self.place_search_rows = []
        self.selected_place_row_id = None
        self.selected_catalog_feed_id = None
        self.selected_downloaded_feed_id = None
        self.selected_feed_source = None
        self._setup_tables()
        self.query_one("#active-date-input", Input).value = TODAY_ISO
        self._load_downloaded_feeds()
        self._load_feed_catalog()

    def on_unmount(self) -> None:
        if self.db is not None:
            self.db.close()
            self.db = None

    def _setup_tables(self) -> None:
        for table in (
            self.query_one("#place-results-table", DataTable),
            self.query_one("#downloaded-feeds-table", DataTable),
            self.query_one("#feed-catalog-table", DataTable),
            self.query_one("#routes-table", DataTable),
            self.query_one("#trips-dir-0-table", DataTable),
            self.query_one("#trips-dir-1-table", DataTable),
            self.query_one("#stop-times-table", DataTable),
            self.query_one("#stops-table", DataTable),
            self.query_one("#arrivals-table", DataTable),
        ):
            table.cursor_type = "row"
            table.zebra_stripes = True

        self.query_one("#place-results-table", DataTable).add_columns(
            "Place", "Latitude", "Longitude"
        )
        self.query_one("#downloaded-feeds-table", DataTable).add_columns(
            "Feed ID", "DuckDB", "Files"
        )
        self.query_one("#feed-catalog-table", DataTable).add_columns(
            "Feed ID", "Provider", "Feed name"
        )
        self.query_one("#routes-table", DataTable).add_columns("Route ID", "Route name")
        self.query_one("#trips-dir-0-table", DataTable).add_columns(
            "Departure", "From", "To"
        )
        self.query_one("#trips-dir-1-table", DataTable).add_columns(
            "Departure", "From", "To"
        )
        self.query_one("#stop-times-table", DataTable).add_columns("Arrival", "Stop")
        self.query_one("#stops-table", DataTable).add_columns("Stop ID", "Stop name")
        self.query_one("#arrivals-table", DataTable).add_columns(
            "Route", "Arrival", "To"
        )

    def _use_loaded_feed(self, feed_id: str) -> None:
        self.selected_feed = feed_id
        self.sub_title = f"Feed: {feed_id}"
        if not self._connect_feed(feed_id):
            return
        self._load_agencies()
        self._load_route_select_options()
        self._refresh_routes_by_selected_agency()
        self._refresh_stops_by_selected_route()
        self.query_one("#selected-feed-label", Label).update(f"Loaded feed: {feed_id}")

    def _connect_feed(self, feed_id: str) -> bool:
        if self.db is not None:
            self.db.close()
            self.db = None

        db_path = Path.home() / ".mobilis" / "feeds" / feed_id / f"{feed_id}.duckdb"
        if not db_path.exists():
            self._notify_error(f"Database not found: {db_path}")
            return False

        try:
            self.db = duckdb.connect(str(db_path), read_only=True)
            table_names = {
                row[0] for row in self.db.execute("SHOW TABLES").fetchall()
            }
            if "calendar" not in table_names:
                self.db.execute(
                    """
                    CREATE TEMP TABLE calendar (
                        service_id VARCHAR,
                        monday INTEGER,
                        tuesday INTEGER,
                        wednesday INTEGER,
                        thursday INTEGER,
                        friday INTEGER,
                        saturday INTEGER,
                        sunday INTEGER,
                        start_date DATE,
                        end_date DATE
                    );
                    """
                )
            if "calendar_dates" not in table_names:
                self.db.execute(
                    """
                    CREATE TEMP TABLE calendar_dates (
                        service_id VARCHAR,
                        date DATE,
                        exception_type INTEGER
                    );
                    """
                )
            route_columns = {
                row[1] for row in self.db.execute("PRAGMA table_info('routes')").fetchall()
            }
            if "route_short_name" in route_columns:
                route_name_expression = "COALESCE(NULLIF(route_short_name, ''), route_id)"
            elif "route_long_name" in route_columns:
                route_name_expression = "COALESCE(NULLIF(route_long_name, ''), route_id)"
            else:
                route_name_expression = "route_id"
            if "agency_id" in route_columns:
                route_agency_expression = "CAST(agency_id AS VARCHAR)"
            else:
                agencies = self.db.execute(
                    "SELECT CAST(agency_id AS VARCHAR) FROM agency ORDER BY agency_id"
                ).fetchall()
                if len(agencies) != 1:
                    raise duckdb.InvalidInputException(
                        "routes table has no agency_id and agency table does not have exactly one agency"
                    )
                fallback_agency_id = agencies[0][0].replace("'", "''")
                route_agency_expression = f"'{fallback_agency_id}'"
            self.db.execute(
                f"""
                CREATE OR REPLACE TEMP VIEW routes_mobilis AS
                SELECT
                    CAST(route_id AS VARCHAR) AS route_id,
                    {route_agency_expression} AS agency_id,
                    {route_name_expression} AS route_name
                FROM routes;
                """
            )
            queries_path = Path(__file__).with_name("queries.sql")
            self.db.execute(queries_path.read_text(encoding="utf-8"))
        except duckdb.Error as exc:
            self._notify_error(f"Failed to open feed {feed_id}: {exc}")
            return False
        return True

    def _query(self, query: str, params: Sequence[object] = ()) -> list[tuple]:
        if self.db is None:
            return []
        try:
            return self.db.execute(query, params).fetchall()
        except duckdb.Error as exc:
            self._notify_error(f"Query error: {exc}")
            return []

    def _metadata_db_path(self) -> Path:
        return Path(__file__).resolve().parents[1] / "feeds" / "feeds.duckdb"

    def _query_catalog(self, query: str, params: Sequence[object] = ()) -> list[tuple]:
        metadata_db_path = self._metadata_db_path()
        if not metadata_db_path.exists():
            self._notify_error(f"Feeds catalog not found: {metadata_db_path}")
            return []

        try:
            with duckdb.connect(str(metadata_db_path), read_only=True) as catalog_db:
                return catalog_db.execute(query, params).fetchall()
        except duckdb.Error:
            temp_catalog_path = Path("/tmp/mobilis-feeds-catalog.duckdb")
            try:
                shutil.copy2(metadata_db_path, temp_catalog_path)
                with duckdb.connect(str(temp_catalog_path), read_only=True) as catalog_db:
                    return catalog_db.execute(query, params).fetchall()
            except (duckdb.Error, OSError) as fallback_exc:
                self._notify_error(f"Failed to load feeds catalog: {fallback_exc}")
                return []

    def _load_downloaded_feeds(self) -> None:
        downloaded_root = Path.home() / ".mobilis" / "feeds"
        table = self.query_one("#downloaded-feeds-table", DataTable)
        table.clear()
        downloaded_root.mkdir(parents=True, exist_ok=True)

        feed_dirs = sorted(path for path in downloaded_root.iterdir() if path.is_dir())
        for feed_dir in feed_dirs:
            feed_id = feed_dir.name
            has_db = (feed_dir / f"{feed_id}.duckdb").exists()
            has_files = (feed_dir / "files").exists()
            table.add_row(
                feed_id,
                "yes" if has_db else "no",
                "yes" if has_files else "no",
                key=feed_id,
            )
        if feed_dirs and not self.selected_feed_source:
            preferred_feed_dir = next(
                (
                    feed_dir
                    for feed_dir in feed_dirs
                    if (feed_dir / f"{feed_dir.name}.duckdb").exists()
                ),
                feed_dirs[0],
            )
            self.selected_downloaded_feed_id = preferred_feed_dir.name
            self.selected_feed_source = "downloaded"
            self.query_one("#selected-feed-label", Label).update(
                f"Selected downloaded feed: {self.selected_downloaded_feed_id}"
            )

    def _load_feed_catalog(self) -> None:
        query = """
            SELECT
                id,
                provider,
                COALESCE(NULLIF(feed_name, ''), '(unnamed feed)') AS feed_name,
                latest_dataset.hosted_url AS hosted_url
            FROM feeds
            WHERE data_type = 'gtfs'
            ORDER BY provider, id;
            """
        rows = self._query_catalog(query)
        if not rows:
            return

        self.feed_catalog_urls = {
            feed_id: hosted_url
            for feed_id, _provider, _feed_name, hosted_url in rows
            if hosted_url
        }
        self.feed_catalog_rows = [
            (feed_id, provider or "", feed_name, hosted_url)
            for feed_id, provider, feed_name, hosted_url in rows
        ]
        self._render_feed_catalog(self.feed_catalog_rows)

    def _fuzzy_score(self, query: str, provider: str, feed_name: str) -> float:
        query_norm = query.strip().lower()
        if not query_norm:
            return 1.0

        provider_norm = provider.lower()
        feed_name_norm = feed_name.lower()
        combined = f"{provider_norm} {feed_name_norm}".strip()

        substring_boost = 1.0 if query_norm in combined else 0.0
        ratio_provider = SequenceMatcher(None, query_norm, provider_norm).ratio()
        ratio_feed = SequenceMatcher(None, query_norm, feed_name_norm).ratio()
        ratio_combined = SequenceMatcher(None, query_norm, combined).ratio()

        token_hits = 0
        query_tokens = [token for token in query_norm.split() if token]
        if query_tokens:
            token_hits = sum(
                1 for token in query_tokens if token in provider_norm or token in feed_name_norm
            )
            token_ratio = token_hits / len(query_tokens)
        else:
            token_ratio = 0.0

        return max(
            substring_boost,
            ratio_provider,
            ratio_feed,
            ratio_combined,
            token_ratio,
        )

    def _search_feed_catalog(
        self, query: str
    ) -> list[tuple[str, str, str, str | None]]:
        query_norm = query.strip()
        if not query_norm:
            return self.feed_catalog_rows

        scored_rows: list[tuple[float, tuple[str, str, str, str | None]]] = []
        for row in self.feed_catalog_rows:
            feed_id, provider, feed_name, _hosted_url = row
            score = self._fuzzy_score(query_norm, provider, feed_name)
            if score >= 0.35:
                # Slightly prefer provider/feed exact token containment
                if query_norm.lower() in provider.lower() or query_norm.lower() in feed_name.lower():
                    score += 0.15
                scored_rows.append((score, row))

        scored_rows.sort(key=lambda item: (-item[0], item[1][1], item[1][0]))
        return [row for _score, row in scored_rows]

    def _render_feed_catalog(
        self, rows: list[tuple[str, str, str, str | None]]
    ) -> None:
        feed_table = self.query_one("#feed-catalog-table", DataTable)
        feed_table.clear()
        for feed_id, provider, feed_name, _hosted_url in rows:
            feed_table.add_row(feed_id, provider, feed_name, key=feed_id)
        if rows:
            self.selected_catalog_feed_id = rows[0][0]
            if self.selected_feed_source in (None, "catalog"):
                self.selected_feed_source = "catalog"
                self.query_one("#selected-feed-label", Label).update(
                    f"Selected catalog feed: {self.selected_catalog_feed_id}"
                )
        else:
            self.selected_catalog_feed_id = None

    def _apply_feed_catalog_search(self) -> None:
        query = self.query_one("#feed-search-input", Input).value
        results = self._search_feed_catalog(query)
        self._render_feed_catalog(results)
        if query.strip() and not results:
            self._notify_warning(f"No feeds matched '{query.strip()}'.")

    def _search_places(self) -> None:
        place_query = self.query_one("#place-search-input", Input).value.strip()
        if not place_query:
            self._notify_warning("Enter a place to search.")
            return

        try:
            response = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q": place_query,
                    "format": "geojson",
                    "limit": 10,
                },
                headers={
                    "User-Agent": "mobilis/0.0.1 (https://github.com/simovilab/mobilis)"
                },
                timeout=30,
            )
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            self._notify_error(f"Place search failed: {exc}")
            return

        features = payload.get("features", [])
        table = self.query_one("#place-results-table", DataTable)
        table.clear()
        self.place_search_rows = []
        self.selected_place_row_id = None

        for index, feature in enumerate(features):
            geometry = feature.get("geometry") or {}
            coords = geometry.get("coordinates") or []
            if len(coords) < 2:
                continue
            lon = float(coords[0])
            lat = float(coords[1])
            display_name = (
                (feature.get("properties") or {}).get("display_name")
                or f"Place {index + 1}"
            )
            row_id = str(index)
            self.place_search_rows.append((row_id, display_name, lat, lon))
            table.add_row(display_name, f"{lat:.6f}", f"{lon:.6f}", key=row_id)

        if not self.place_search_rows:
            self.query_one("#selected-place-label", Label).update("No place selected.")
            self._notify_warning(f"No places matched '{place_query}'.")
            return

        first_row_id, first_name, first_lat, first_lon = self.place_search_rows[0]
        self.selected_place_row_id = first_row_id
        self.query_one("#selected-place-label", Label).update(
            f"Selected place: {first_name} ({first_lat:.6f}, {first_lon:.6f})"
        )
        if len(self.place_search_rows) > 1:
            self._notify_warning(
                "Multiple places found. Select the correct one, then click 'Find feeds for place'."
            )

    def _selected_place_coordinates(self) -> tuple[float, float, str] | None:
        if self.selected_place_row_id is None:
            return None
        for row_id, display_name, lat, lon in self.place_search_rows:
            if row_id == self.selected_place_row_id:
                return lat, lon, display_name
        return None

    def _search_feeds_by_selected_place(self) -> None:
        selected = self._selected_place_coordinates()
        if selected is None:
            self._notify_warning("Select a place first.")
            return

        lat, lon, display_name = selected
        query = """
            SELECT
                id,
                provider,
                COALESCE(NULLIF(feed_name, ''), '(unnamed feed)') AS feed_name,
                latest_dataset.hosted_url AS hosted_url
            FROM feeds
            WHERE
                data_type = 'gtfs'
                AND COALESCE(
                    latest_dataset.bounding_box.minimum_latitude,
                    bounding_box.minimum_latitude
                ) IS NOT NULL
                AND CAST(? AS DOUBLE) BETWEEN COALESCE(
                    latest_dataset.bounding_box.minimum_latitude,
                    bounding_box.minimum_latitude
                ) AND COALESCE(
                    latest_dataset.bounding_box.maximum_latitude,
                    bounding_box.maximum_latitude
                )
                AND CAST(? AS DOUBLE) BETWEEN COALESCE(
                    latest_dataset.bounding_box.minimum_longitude,
                    bounding_box.minimum_longitude
                ) AND COALESCE(
                    latest_dataset.bounding_box.maximum_longitude,
                    bounding_box.maximum_longitude
                )
            ORDER BY provider, id;
        """
        rows = self._query_catalog(query, (lat, lon))
        self._render_feed_catalog(
            [
                (feed_id, provider or "", feed_name, hosted_url)
                for feed_id, provider, feed_name, hosted_url in rows
            ]
        )
        if rows:
            self.notify(
                f"Found {len(rows)} feeds covering {display_name}.",
                severity="information",
            )
        else:
            self._notify_warning(f"No GTFS feeds cover {display_name}.")

    def _download_and_prepare_feed(self, feed_id: str) -> None:
        hosted_url = self.feed_catalog_urls.get(feed_id)
        if not hosted_url:
            self._notify_error(f"Feed {feed_id} has no latest_dataset.hosted_url")
            return

        self.notify(f"Downloading {feed_id}...", severity="information")
        feed_path = Path.home() / ".mobilis" / "feeds" / feed_id
        files_path = feed_path / "files"
        zip_path = feed_path / f"{feed_id}.zip"
        feed_path.mkdir(parents=True, exist_ok=True)
        if files_path.exists():
            shutil.rmtree(files_path)
        files_path.mkdir(parents=True, exist_ok=True)

        try:
            with requests.get(hosted_url, stream=True, timeout=180) as response:
                response.raise_for_status()
                with zip_path.open("wb") as zip_file:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            zip_file.write(chunk)
            with zipfile.ZipFile(zip_path, "r") as zip_file:
                zip_file.extractall(files_path)
        except (requests.RequestException, zipfile.BadZipFile, OSError) as exc:
            self._notify_error(f"Failed to download/extract {feed_id}: {exc}")
            return
        finally:
            if zip_path.exists():
                zip_path.unlink()

        self._normalize_extracted_feed_files(files_path)

        # Avoid DuckDB config conflicts when re-importing a feed that may already
        # be open in this app (read-only).
        if self.db is not None:
            self.db.close()
            self.db = None

        try:
            import_gtfs(feed_id)
        except (duckdb.Error, ValueError, OSError) as exc:
            self._notify_error(f"Failed to import GTFS for {feed_id}: {exc}")
            return

        self.notify(f"Loaded feed {feed_id}", severity="information")
        self._load_downloaded_feeds()
        self._use_loaded_feed(feed_id)
        self.query_one("#top-menu", TabbedContent).active = "trips-by-route"

    def _normalize_extracted_feed_files(self, files_path: Path) -> None:
        txt_files = list(files_path.glob("*.txt"))
        if txt_files:
            return

        nested_dirs = [path for path in files_path.iterdir() if path.is_dir()]
        if len(nested_dirs) != 1:
            return

        nested_dir = nested_dirs[0]
        for child in list(nested_dir.iterdir()):
            target = files_path / child.name
            if target.exists():
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
            child.rename(target)
        nested_dir.rmdir()

    def _load_agencies(self) -> None:
        agencies = self._query(
            """
            SELECT agency_id, agency_name
            FROM agency
            ORDER BY agency_name;
            """
        )
        agency_select = self.query_one("#agency-select", Select)
        options = [(f"{name} ({agency_id})", agency_id) for agency_id, name in agencies]
        agency_select.set_options(options)
        if options:
            agency_select.value = options[0][1]

    def _load_route_select_options(self) -> None:
        route_rows = self._query(
            """
            SELECT route_id, route_name
            FROM routes_mobilis
            ORDER BY route_name, route_id;
            """
        )
        route_select = self.query_one("#stop-route-select", Select)
        route_select.set_options(
            [(f"{route_name} ({route_id})", route_id) for route_id, route_name in route_rows]
        )
        if route_rows:
            route_select.value = route_rows[0][0]

    def _refresh_routes_by_selected_agency(self) -> None:
        agency_id = self.query_one("#agency-select", Select).value
        routes_table = self.query_one("#routes-table", DataTable)
        routes_table.clear()
        if agency_id is None or agency_id == Select.BLANK:
            return

        rows = self._query(
            """
            SELECT route_id, route_name
            FROM routes_by_agency(?)
            ORDER BY route_name, route_id;
            """,
            (agency_id,),
        )
        for route_id, route_name in rows:
            routes_table.add_row(route_id, route_name, key=route_id)

        if rows:
            self.selected_route_id_for_trips = rows[0][0]
            self._refresh_trips_by_selected_route()
        else:
            self.selected_route_id_for_trips = None
            self._clear_table("#trips-dir-0-table")
            self._clear_table("#trips-dir-1-table")
            self._clear_table("#stop-times-table")

    def _date_value(self) -> str:
        raw = self.query_one("#active-date-input", Input).value.strip()
        return raw or TODAY_ISO

    def _interval_or_none(self, widget_id: str) -> str | None:
        value = self.query_one(widget_id, Input).value.strip()
        return value or None

    def _selected_agency_context(self) -> str:
        agency_id = self.query_one("#agency-select", Select).value
        if agency_id is None or agency_id == Select.BLANK:
            return ""
        rows = self._query(
            "SELECT agency_name FROM agency WHERE agency_id = ? LIMIT 1;",
            (agency_id,),
        )
        if rows:
            return f" for agency {rows[0][0]} ({agency_id})"
        return f" for agency {agency_id}"

    def _find_next_service_date_for_route(
        self, route_id: str, start_date: str
    ) -> str | None:
        rows = self._query(
            """
            SELECT CAST(gs.service_date AS DATE)::VARCHAR AS service_date
            FROM generate_series(
                CAST(? AS DATE),
                CAST(? AS DATE) + INTERVAL 14 DAY,
                INTERVAL 1 DAY
            ) AS gs(service_date)
            WHERE EXISTS (
                SELECT 1
                FROM active_trips_by_route(CAST(gs.service_date AS DATE), ?)
                LIMIT 1
            )
            ORDER BY gs.service_date
            LIMIT 1;
            """,
            (start_date, start_date, route_id),
        )
        return rows[0][0] if rows else None

    def _refresh_trips_by_selected_route(self) -> None:
        if not self.selected_route_id_for_trips:
            return
        active_date = self._date_value()
        lower_limit = self._interval_or_none("#lower-limit-input")
        upper_limit = self._interval_or_none("#upper-limit-input")
        trip_rows = self._query(
            """
            SELECT
                trip_id,
                direction_id,
                trip_departure_time::VARCHAR AS trip_departure_time,
                COALESCE(first_stop, '') AS first_stop,
                COALESCE(last_stop, '') AS last_stop
            FROM active_trips_by_route(CAST(? AS DATE), ?)
            WHERE
                (? IS NULL OR trip_departure_time >= CAST(? AS INTERVAL))
                AND (? IS NULL OR trip_departure_time <= CAST(? AS INTERVAL))
            ORDER BY trip_departure_time, trip_id;
            """,
            (
                active_date,
                self.selected_route_id_for_trips,
                lower_limit,
                lower_limit,
                upper_limit,
                upper_limit,
            ),
        )

        trips_0 = self.query_one("#trips-dir-0-table", DataTable)
        trips_1 = self.query_one("#trips-dir-1-table", DataTable)
        trips_0.clear()
        trips_1.clear()

        if not trip_rows and not lower_limit and not upper_limit:
            agency_context = self._selected_agency_context()
            next_date = self._find_next_service_date_for_route(
                self.selected_route_id_for_trips,
                active_date,
            )
            if next_date and next_date != active_date:
                self._notify_warning(
                    f"No trips found{agency_context} on {active_date}. "
                    f"Try changing the date to {next_date}."
                )
            else:
                self._notify_warning(
                    f"No trips found{agency_context} on {active_date}. Try changing the date."
                )

        first_trip_id: str | None = None
        for trip_id, direction_id, departure_time, first_stop, last_stop in trip_rows:
            row = (departure_time, first_stop, last_stop)
            if int(direction_id or 0) == 0:
                trips_0.add_row(*row, key=trip_id)
                if first_trip_id is None:
                    first_trip_id = trip_id
            else:
                trips_1.add_row(*row, key=trip_id)
                if first_trip_id is None:
                    first_trip_id = trip_id

        if first_trip_id:
            self._refresh_stop_times_by_trip(first_trip_id)
        else:
            self._clear_table("#stop-times-table")

    def _refresh_stop_times_by_trip(self, trip_id: str) -> None:
        stop_time_rows = self._query(
            """
            SELECT
                arrival_time::VARCHAR,
                stop_name
            FROM stop_times_by_trip(?)
            ORDER BY stop_sequence;
            """,
            (trip_id,),
        )
        stop_times_table = self.query_one("#stop-times-table", DataTable)
        stop_times_table.clear()
        for row in stop_time_rows:
            stop_times_table.add_row(*row)

    def _refresh_stops_by_selected_route(self) -> None:
        route_id = self.query_one("#stop-route-select", Select).value
        stops_table = self.query_one("#stops-table", DataTable)
        stops_table.clear()
        if route_id is None or route_id == Select.BLANK:
            self.selected_route_id_for_stops = None
            self._clear_table("#arrivals-table")
            return

        self.selected_route_id_for_stops = route_id
        rows = self._query(
            """
            SELECT stop_id, stop_name
            FROM stops_by_route(?)
            ORDER BY stop_name, stop_id;
            """,
            (route_id,),
        )
        for stop_id, stop_name in rows:
            stops_table.add_row(stop_id, stop_name, key=stop_id)

        if rows:
            self.selected_stop_id_for_arrivals = rows[0][0]
            self._refresh_arrivals_by_selected_stop()
        else:
            self.selected_stop_id_for_arrivals = None
            self._clear_table("#arrivals-table")

    def _refresh_arrivals_by_selected_stop(self) -> None:
        if not self.selected_stop_id_for_arrivals:
            return
        rows = self._query(
            """
            SELECT
                route_name,
                arrival_time::VARCHAR AS arrival_time,
                last_stop
            FROM trips_by_stop(CAST(? AS DATE), ?)
            ORDER BY arrival_time;
            """,
            (self._date_value(), self.selected_stop_id_for_arrivals),
        )
        arrivals_table = self.query_one("#arrivals-table", DataTable)
        arrivals_table.clear()
        for route_name, arrival_time, last_stop in rows:
            arrivals_table.add_row(
                route_name,
                arrival_time,
                last_stop,
            )

    def _clear_table(self, table_id: str) -> None:
        self.query_one(table_id, DataTable).clear()

    # --- Events ----------------------------------------------------------------

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "agency-select":
            self._refresh_routes_by_selected_agency()
        elif event.select.id == "stop-route-select":
            self._refresh_stops_by_selected_route()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "apply-route-filters":
            self._refresh_trips_by_selected_route()
        elif event.button.id == "search-feed-list":
            self._apply_feed_catalog_search()
        elif event.button.id == "search-place-list":
            self._search_places()
        elif event.button.id == "search-feeds-by-place":
            self._search_feeds_by_selected_place()
        elif event.button.id == "refresh-feed-list":
            self._load_downloaded_feeds()
            self._load_feed_catalog()
        elif event.button.id == "load-selected-feed":
            if self.selected_feed_source == "downloaded":
                if not self.selected_downloaded_feed_id:
                    self._notify_warning("Select a downloaded feed from the list first.")
                    return
                self._use_loaded_feed(self.selected_downloaded_feed_id)
                self.query_one("#top-menu", TabbedContent).active = "trips-by-route"
                return
            if not self.selected_catalog_feed_id:
                self._notify_warning("Select a feed from the list first.")
                return
            self._download_and_prepare_feed(self.selected_catalog_feed_id)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.row_key is None:
            return
        row_id = str(event.row_key.value)
        if event.data_table.id == "feed-catalog-table":
            self.selected_catalog_feed_id = row_id
            self.selected_feed_source = "catalog"
            self.query_one("#selected-feed-label", Label).update(
                f"Selected catalog feed: {row_id}"
            )
        elif event.data_table.id == "place-results-table":
            self.selected_place_row_id = row_id
            selected = self._selected_place_coordinates()
            if selected is not None:
                lat, lon, display_name = selected
                self.query_one("#selected-place-label", Label).update(
                    f"Selected place: {display_name} ({lat:.6f}, {lon:.6f})"
                )
        elif event.data_table.id == "downloaded-feeds-table":
            self.selected_downloaded_feed_id = row_id
            self.selected_feed_source = "downloaded"
            self.query_one("#selected-feed-label", Label).update(
                f"Selected downloaded feed: {row_id}"
            )
        elif event.data_table.id in {"trips-dir-0-table", "trips-dir-1-table"}:
            self._refresh_stop_times_by_trip(row_id)
        elif event.data_table.id == "routes-table":
            self.selected_route_id_for_trips = row_id
            self._refresh_trips_by_selected_route()
        elif event.data_table.id == "stops-table":
            self.selected_stop_id_for_arrivals = row_id
            self._refresh_arrivals_by_selected_stop()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "feed-search-input":
            self._apply_feed_catalog_search()
        elif event.input.id == "place-search-input":
            self._search_places()
        elif event.input.id in {
            "active-date-input",
            "lower-limit-input",
            "upper-limit-input",
        }:
            self._refresh_trips_by_selected_route()

    # --- Actions ---------------------------------------------------------------

    def action_reload_all(self) -> None:
        self._load_downloaded_feeds()
        self._load_feed_catalog()
        if self.selected_feed:
            self._refresh_routes_by_selected_agency()
            self._refresh_stops_by_selected_route()


def run_mobilis_go() -> None:
    """Entry point used by the CLI to launch the TUI."""
    MobilisGoApp().run()
