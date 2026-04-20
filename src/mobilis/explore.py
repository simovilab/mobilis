"""Textual TUI for ``mobilis explore`` — GTFS feed analytics (stub).

Audience: researchers and analysts who want to inspect, summarize and
export GTFS feed data. Counterpart of :mod:`mobilis.go`, which is the
passenger-facing dashboard.

This is intentionally a minimal scaffold — no real GTFS parsing or
export yet. It lays out the widgets we'll flesh out later: a feed
summary, a stats panel, a tables browser, and an export pane.
"""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    Label,
    TabbedContent,
    TabPane,
)

# --- Mock data ---------------------------------------------------------------

# Typical GTFS file set; counts are placeholders until real parsing lands.
MOCK_FEED_TABLES: list[tuple[str, int]] = [
    ("agency.txt", 0),
    ("stops.txt", 0),
    ("routes.txt", 0),
    ("trips.txt", 0),
    ("stop_times.txt", 0),
    ("calendar.txt", 0),
    ("shapes.txt", 0),
]

MOCK_STATS: list[tuple[str, str]] = [
    ("Agencies", "—"),
    ("Routes", "—"),
    ("Stops", "—"),
    ("Trips", "—"),
    ("Stop times", "—"),
    ("Service date range", "—"),
]


# --- Widgets -----------------------------------------------------------------


class TablesList(DataTable):
    """List of GTFS tables in the loaded feed."""

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.zebra_stripes = True
        self.add_columns("Table", "Rows")
        for name, rows in MOCK_FEED_TABLES:
            self.add_row(name, str(rows) if rows else "—")


class StatsTable(DataTable):
    """Summary statistics for the loaded feed."""

    def on_mount(self) -> None:
        self.show_header = False
        self.add_columns("Metric", "Value")
        for metric, value in MOCK_STATS:
            self.add_row(metric, value)


# --- App ---------------------------------------------------------------------


class MobilisExploreApp(App):
    """Placeholder explorer app for GTFS analytics and export.

    Future versions will load a GTFS feed (static and/or real-time),
    compute statistics, allow drilling into individual tables, and
    export filtered subsets to CSV / Parquet / GeoJSON.
    """

    CSS = """
    Screen {
        layout: vertical;
    }

    #body {
        height: 1fr;
        padding: 0 1;
    }

    .section-title {
        padding: 1 0 0 0;
        color: $accent;
        text-style: bold;
    }

    DataTable {
        height: 1fr;
    }
    """

    TITLE = "mobilis explore"
    SUB_TITLE = "GTFS analytics — stub"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("o", "open_feed", "Open feed"),
        ("e", "export", "Export"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="body"):
            with TabbedContent(initial="summary"):
                with TabPane("Summary", id="summary"):
                    yield Label("Feed statistics", classes="section-title")
                    yield StatsTable(id="stats")
                with TabPane("Tables", id="tables"):
                    yield Label("GTFS tables", classes="section-title")
                    yield TablesList(id="tables-list")
                with TabPane("Export", id="export"):
                    yield Label("Export", classes="section-title")
                    yield Label(
                        "[dim]Export to CSV / Parquet / GeoJSON — coming soon.[/dim]",
                        id="export-placeholder",
                    )
        yield Footer()

    # --- Actions -------------------------------------------------------------

    def action_open_feed(self) -> None:
        """Placeholder — will prompt for a GTFS feed path/URL."""

    def action_export(self) -> None:
        """Placeholder — will export the current view/selection."""


def run_mobilis_explore() -> None:
    """Entry point used by the CLI to launch the explorer TUI."""
    MobilisExploreApp().run()
