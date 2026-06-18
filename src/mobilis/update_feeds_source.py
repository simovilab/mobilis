import duckdb
import requests

FEEDS_URL = "https://data.simovilab.org/mobility-database/feeds.json"

response = requests.get(FEEDS_URL)
with open("feeds/feeds.json", "w") as f:
    f.write(response.text)

with duckdb.connect("feeds.duckdb") as d:
    d.from_json("feeds/feeds.json")
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
