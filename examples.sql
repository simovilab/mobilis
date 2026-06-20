/*
MBTA GTFS feed Database
*/

ATTACH 'mbta.duckdb' AS mbta;

/*
 Loading Feed Info
*/

CREATE TABLE feed_info AS
  SELECT
    * EXCLUDE(feed_start_date, feed_end_date),
    CAST(strptime(CAST(feed_start_date AS VARCHAR), '%Y%m%d') AS DATE) AS feed_start_date,
    CAST(strptime(CAST(feed_end_date AS VARCHAR), '%Y%m%d') AS DATE) AS feed_end_date
  FROM read_csv('~/mbta/feed_info.txt');

  /*
Loading Agency
*/

CREATE TABLE agency AS
  SELECT 
    * EXCLUDE(agency_phone, agency_id),
    CAST(agency_phone AS VARCHAR) AS agency_phone,
    CAST(agency_id AS VARCHAR) AS agency_id
  FROM read_csv('~/mbta/agency.txt');

/*
Loading Stops
*/

INSTALL spatial;
LOAD spatial;

CREATE TABLE stops AS
  SELECT
    *,
    ST_Point(stop_lon, stop_lat) AS stop_loc
  FROM read_csv('~/mbta/stops.txt')

/*
Loading Routes
*/

CREATE TABLE routes AS
  SELECT
    * EXCLUDE(route_color, route_text_color),
    CAST(route_color AS VARCHAR) AS route_color,
    CAST(route_text_color AS VARCHAR) AS route_text_color
  FROM read_csv('~/mbta/routes.txt');

/*
Loading Trips
*/

CREATE TABLE trips AS
  SELECT * FROM read_csv('~/mbta/trips.txt', types={'route_id': 'VARCHAR'}, quote='"')

/*
Loading Stop Times
*/

CREATE TABLE stop_times AS
SELECT
  * EXCLUDE(arrival_time, departure_time),
  INTERVAL (
    CAST(split_part(arrival_time::VARCHAR, ':', 1) AS INTEGER) * 3600 +
    CAST(split_part(arrival_time::VARCHAR, ':', 2) AS INTEGER) * 60 +
    CAST(split_part(arrival_time::VARCHAR, ':', 3) AS INTEGER)
  ) SECOND AS arrival_time,
  INTERVAL (
    CAST(split_part(departure_time::VARCHAR, ':', 1) AS INTEGER) * 3600 +
    CAST(split_part(departure_time::VARCHAR, ':', 2) AS INTEGER) * 60 +
    CAST(split_part(departure_time::VARCHAR, ':', 3) AS INTEGER)
  ) SECOND AS departure_time
FROM read_csv('~/mbta/stop_times.txt', types={'arrival_time': 'VARCHAR', 'departure_time': 'VARCHAR', 'stop_id': 'VARCHAR'});

/*
Select data for stop_id "609" where arrival_time is after 8:32 AM in increasing order of arrival_time, and get stop_name from stops table
*/

SELECT st.*, s.stop_name, s.stop_desc 
  FROM stop_times st JOIN stops s ON st.stop_id = s.stop_id
  WHERE st.stop_id = '609' AND st.arrival_time > INTERVAL '8 hours 32 minutes' 
  ORDER BY st.arrival_time ASC
  LIMIT 20;