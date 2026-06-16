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
