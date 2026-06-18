import os
import duckdb
from .required import REQUIRED_FIELDS

required_tables = set(REQUIRED_FIELDS)
feeds_path = os.path.expanduser("~/.mobilis/feeds")


def import_gtfs(feed_id: str):
    feed_path = os.path.join(feeds_path, feed_id)
    files_path = os.path.join(feed_path, "files")
    actual_files = {
        os.path.splitext(f)[0] for f in os.listdir(files_path) if f.endswith(".txt")
    }
    if not required_tables.issubset(actual_files):
        missing_tables = required_tables - actual_files
        raise ValueError(
            f"Feed {feed_id} is missing required tables: {', '.join(missing_tables)}"
        )

    with duckdb.connect(f"{feed_path}/{feed_id}.duckdb") as d:
        d.execute("INSTALL spatial; LOAD spatial;")

        # Agency
        agency_required_fields = set(REQUIRED_FIELDS["agency"])
        csv_path = os.path.join(files_path, "agency.txt")
        rows = d.execute(
            "DESCRIBE SELECT * FROM read_csv_auto(?, header=true)",
            [csv_path],
        ).fetchall()
        agency_actual_fields = set(row[0] for row in rows)
        if agency_required_fields.issubset(agency_actual_fields):
            d.sql(f"""
                CREATE OR REPLACE TABLE agency AS
                SELECT 
                    CAST(agency_id AS VARCHAR) AS agency_id,
                    agency_name,
                    agency_url,
                    agency_timezone,
                FROM read_csv('{files_path}/agency.txt');
                """)
        else:
            missing_fields = agency_required_fields - agency_actual_fields
            raise ValueError(
                f"Feed {feed_id} is missing required fields in agency.txt: {', '.join(missing_fields)}"
            )

        # Stops
        stops_required_fields = set(REQUIRED_FIELDS["stops"])
        csv_path = os.path.join(files_path, "stops.txt")
        rows = d.execute(
            "DESCRIBE SELECT * FROM read_csv_auto(?, header=true)",
            [csv_path],
        ).fetchall()
        stops_actual_fields = set(row[0] for row in rows)
        if stops_required_fields.issubset(stops_actual_fields):
            d.sql(f"""
                CREATE OR REPLACE TABLE stops AS
                SELECT 
                    CAST(stop_id AS VARCHAR) AS stop_id,
                    stop_name,
                    stop_lat,
                    stop_lon,
                  ST_Point(stop_lon, stop_lat) AS stop_point,
                FROM read_csv('{files_path}/stops.txt');
                """)
        else:
            missing_fields = stops_required_fields - stops_actual_fields
            raise ValueError(
                f"Feed {feed_id} is missing required fields in stops.txt: {', '.join(missing_fields)}"
            )

        # Routes
        routes_required_fields = set(REQUIRED_FIELDS["routes"])
        csv_path = os.path.join(files_path, "routes.txt")
        rows = d.execute(
            "DESCRIBE SELECT * FROM read_csv_auto(?, header=true)",
            [csv_path],
        ).fetchall()
        routes_actual_fields = set(row[0] for row in rows)
        route_name_fields = ()
        if (
            "route_short_name" not in routes_actual_fields
            and "route_long_name" not in routes_actual_fields
        ):
            raise ValueError(
                f"Feed {feed_id} must have at least one of route_short_name or route_long_name in routes.txt"
            )
        elif "route_short_name" in routes_actual_fields:
            route_name_fields += ("route_short_name",)
        elif "route_long_name" in routes_actual_fields:
            route_name_fields += ("route_long_name",)
        if routes_required_fields.issubset(routes_actual_fields):
            d.sql(f"""
                CREATE OR REPLACE TABLE routes AS
                SELECT 
                    CAST(route_id AS VARCHAR) AS route_id,
                    agency_id,
                    {", ".join(route_name_fields)},
                    route_type,
                FROM read_csv('{files_path}/routes.txt');
                """)
        else:
            missing_fields = routes_required_fields - routes_actual_fields
            raise ValueError(
                f"Feed {feed_id} is missing required fields in routes.txt: {', '.join(missing_fields)}"
            )

        # Calendar
        calendar_required_fields = set(REQUIRED_FIELDS["calendar"])
        csv_path = os.path.join(files_path, "calendar.txt")
        rows = d.execute(
            "DESCRIBE SELECT * FROM read_csv_auto(?, header=true)",
            [csv_path],
        ).fetchall()
        calendar_actual_fields = set(row[0] for row in rows)
        if calendar_required_fields.issubset(calendar_actual_fields):
            d.sql(f"""
                CREATE OR REPLACE TABLE calendar AS
                SELECT 
                    CAST(service_id AS VARCHAR) AS service_id,
                    monday,
                    tuesday,
                    wednesday,
                    thursday,
                    friday,
                    saturday,
                    sunday,
                    CAST(strptime(CAST(start_date AS VARCHAR), '%Y%m%d') AS DATE) AS start_date,
                    CAST(strptime(CAST(end_date AS VARCHAR), '%Y%m%d') AS DATE) AS end_date,
                FROM read_csv('{files_path}/calendar.txt');
                """)
        else:
            missing_fields = calendar_required_fields - calendar_actual_fields
            raise ValueError(
                f"Feed {feed_id} is missing required fields in calendar.txt: {', '.join(missing_fields)}"
            )

        # Shapes
        shapes_required_fields = set(REQUIRED_FIELDS["shapes"])
        csv_path = os.path.join(files_path, "shapes.txt")
        rows = d.execute(
            "DESCRIBE SELECT * FROM read_csv_auto(?, header=true)",
            [csv_path],
        ).fetchall()
        shapes_actual_fields = set(row[0] for row in rows)
        if shapes_required_fields.issubset(shapes_actual_fields):
            d.sql(f"""
                CREATE OR REPLACE TABLE shapes AS
                SELECT 
                    CAST(shape_id AS VARCHAR) AS shape_id,
                    shape_pt_lat,
                    shape_pt_lon,
                    shape_pt_sequence,
                    ST_Point(shape_pt_lon, shape_pt_lat) AS shape_pt,
                FROM read_csv('{files_path}/shapes.txt');
                """)
            d.sql("""
                CREATE OR REPLACE TABLE geoshapes AS
                SELECT 
                    shape_id,
                    ST_MakeLine(list(shape_pt ORDER BY shape_pt_sequence)) AS geometry
                FROM shapes
                GROUP BY shape_id;
                """)
        else:
            missing_fields = shapes_required_fields - shapes_actual_fields
            raise ValueError(
                f"Feed {feed_id} is missing required fields in shapes.txt: {', '.join(missing_fields)}"
            )

        # Trips
        trips_required_fields = set(REQUIRED_FIELDS["trips"])
        csv_path = os.path.join(files_path, "trips.txt")
        rows = d.execute(
            "DESCRIBE SELECT * FROM read_csv_auto(?, header=true)",
            [csv_path],
        ).fetchall()
        trips_actual_fields = set(row[0] for row in rows)
        if trips_required_fields.issubset(trips_actual_fields):
            d.sql(f"""
                CREATE OR REPLACE TABLE trips AS
                SELECT 
                    route_id,
                    service_id,
                    trip_id,
                    shape_id,
                    direction_id,
                FROM read_csv('{files_path}/trips.txt', types={{"route_id": 'VARCHAR', 'service_id': 'VARCHAR', 'trip_id': 'VARCHAR', 'shape_id': 'VARCHAR'}}, quote='"');
                """)
        else:
            missing_fields = trips_required_fields - trips_actual_fields
            raise ValueError(
                f"Feed {feed_id} is missing required fields in trips.txt: {', '.join(missing_fields)}"
            )

        # Stop Times
        stop_times_required_fields = set(REQUIRED_FIELDS["stop_times"])
        csv_path = os.path.join(files_path, "stop_times.txt")
        rows = d.execute(
            "DESCRIBE SELECT * FROM read_csv_auto(?, header=true)",
            [csv_path],
        ).fetchall()
        stop_times_actual_fields = set(row[0] for row in rows)
        if stop_times_required_fields.issubset(stop_times_actual_fields):
            d.sql(f"""
                CREATE OR REPLACE TABLE stop_times AS
                SELECT 
                    trip_id,
                    stop_id,
                    stop_sequence,
                    INTERVAL (
                            CAST(split_part(arrival_time, ':', 1) AS INTEGER) * 3600 +
                            CAST(split_part(arrival_time, ':', 2) AS INTEGER) * 60 +
                            CAST(split_part(arrival_time, ':', 3) AS INTEGER)
                        ) SECOND AS arrival_time,
                    INTERVAL (
                            CAST(split_part(departure_time, ':', 1) AS INTEGER) * 3600 +
                            CAST(split_part(departure_time, ':', 2) AS INTEGER) * 60 +
                            CAST(split_part(departure_time, ':', 3) AS INTEGER)
                        ) SECOND AS departure_time,
                FROM read_csv('{files_path}/stop_times.txt', types={{"trip_id": 'VARCHAR', 'stop_id': 'VARCHAR', 'arrival_time': 'VARCHAR', 'departure_time': 'VARCHAR'}}, quote='"');
                """)
        else:
            missing_fields = stop_times_required_fields - stop_times_actual_fields
            raise ValueError(
                f"Feed {feed_id} is missing required fields in stop_times.txt: {', '.join(missing_fields)}"
            )

        # Calendar Dates
        calendar_dates_required_fields = set(REQUIRED_FIELDS["calendar_dates"])
        csv_path = os.path.join(files_path, "calendar_dates.txt")
        rows = d.execute(
            "DESCRIBE SELECT * FROM read_csv_auto(?, header=true)",
            [csv_path],
        ).fetchall()
        calendar_dates_actual_fields = set(row[0] for row in rows)
        if calendar_dates_required_fields.issubset(calendar_dates_actual_fields):
            d.sql(f"""
                CREATE OR REPLACE TABLE calendar_dates AS
                SELECT 
                    CAST(service_id AS VARCHAR) AS service_id,
                    CAST(strptime(CAST(date AS VARCHAR), '%Y%m%d') AS DATE) AS date,
                    exception_type,
                FROM read_csv('{files_path}/calendar_dates.txt');
                """)
        else:
            missing_fields = (
                calendar_dates_required_fields - calendar_dates_actual_fields
            )
            raise ValueError(
                f"Feed {feed_id} is missing required fields in calendar_dates.txt: {', '.join(missing_fields)}"
            )
