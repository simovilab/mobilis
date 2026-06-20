"""Regenerate the bundled Mobility Database feed catalog.

Downloads the latest feeds.json and rebuilds the DuckDB catalog that ships
inside the package at ``src/mobilis/data/feeds.duckdb``. The raw JSON download
is kept under ``src/feeds/`` as a build input and is NOT shipped in the wheel.
"""

from pathlib import Path

import duckdb
import requests

FEEDS_URL = "https://data.simovilab.org/mobility-database/feeds.json"

PACKAGE_DIR = Path(__file__).resolve().parent
JSON_PATH = PACKAGE_DIR.parent / "feeds" / "feeds.json"
DUCKDB_PATH = PACKAGE_DIR / "data" / "feeds.duckdb"

JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
DUCKDB_PATH.parent.mkdir(parents=True, exist_ok=True)

response = requests.get(FEEDS_URL)
with open(JSON_PATH, "w") as f:
    f.write(response.text)

with duckdb.connect(str(DUCKDB_PATH)) as d:
    d.from_json(str(JSON_PATH))
    n_feeds = d.sql("""
        SELECT count(id) FROM feeds 
        WHERE data_type = 'gtfs' AND source_info.authentication_type = 0;
    """)
    d.sql("""
        UPDATE feeds
        SET bbox = CASE
            WHEN bounding_box IS NULL THEN NULL
            ELSE ST_MakeEnvelope(
                bounding_box.minimum_longitude,
                bounding_box.minimum_latitude,
                bounding_box.maximum_longitude,
                bounding_box.maximum_latitude
        ) 
        END;
        """)
