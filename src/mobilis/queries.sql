CREATE OR REPLACE TEMP MACRO first_departure_time(trip_id_param) AS (
    SELECT arrival_time
    FROM stop_times
    WHERE stop_times.trip_id = trip_id_param
    ORDER BY stop_sequence
    LIMIT 1
);

CREATE OR REPLACE TEMP MACRO active_services(active_date) AS TABLE
WITH
    base_services AS (
        SELECT c.service_id
        FROM calendar c
        WHERE
            active_date BETWEEN c.start_date AND c.end_date
            AND CASE dayofweek(active_date)
                WHEN 0 THEN c.sunday
                WHEN 1 THEN c.monday
                WHEN 2 THEN c.tuesday
                WHEN 3 THEN c.wednesday
                WHEN 4 THEN c.thursday
                WHEN 5 THEN c.friday
                WHEN 6 THEN c.saturday
            END = 1
    ),
    added_services AS (
        SELECT cd.service_id
        FROM calendar_dates cd
        WHERE cd.date = active_date
            AND cd.exception_type = 1
    ),
    removed_services AS (
        SELECT cd.service_id
        FROM calendar_dates cd
        WHERE cd.date = active_date
            AND cd.exception_type = 2
    )
SELECT service_id
FROM (
    (
        SELECT service_id FROM base_services
        UNION
        SELECT service_id FROM added_services
    )
    EXCEPT
    SELECT service_id FROM removed_services
);

CREATE OR REPLACE TEMP MACRO routes_by_agency(agency_id_param) AS TABLE
SELECT
    r.route_id,
    r.route_name
FROM routes_mobilis r
WHERE
    r.agency_id = agency_id_param
    OR (
        (r.agency_id IS NULL OR r.agency_id = '')
        AND (SELECT COUNT(*) FROM agency) = 1
    );

CREATE OR REPLACE TEMP MACRO active_trips_by_route(active_date, route_id_param) AS TABLE
SELECT
    t.trip_id,
    t.route_id,
    t.service_id,
    t.direction_id,
    COALESCE(first_stop.first_stop_name, '') AS first_stop,
    COALESCE(last_stop.last_stop_name, '') AS last_stop,
    first_departure_time(t.trip_id) AS trip_departure_time
FROM trips t
JOIN LATERAL (
    SELECT s.stop_name AS first_stop_name
    FROM stop_times st
    JOIN stops s ON s.stop_id = st.stop_id
    WHERE st.trip_id = t.trip_id
    ORDER BY st.stop_sequence ASC
    LIMIT 1
) AS first_stop ON TRUE
JOIN LATERAL (
    SELECT s.stop_name AS last_stop_name
    FROM stop_times st
    JOIN stops s ON s.stop_id = st.stop_id
    WHERE st.trip_id = t.trip_id
    ORDER BY st.stop_sequence DESC
    LIMIT 1
) AS last_stop ON TRUE
WHERE
    t.route_id = route_id_param
    AND t.service_id IN (SELECT service_id FROM active_services(active_date));

CREATE OR REPLACE TEMP MACRO stop_times_by_trip(trip_id_param) AS TABLE
SELECT
    st.trip_id,
    st.stop_id,
    s.stop_name,
    st.stop_sequence,
    st.arrival_time,
    st.departure_time
FROM stop_times st
JOIN stops s ON s.stop_id = st.stop_id
WHERE st.trip_id = trip_id_param;

CREATE OR REPLACE TEMP MACRO stops_by_route(route_id_param) AS TABLE
SELECT DISTINCT
    s.stop_id,
    s.stop_name
FROM stop_times st
JOIN trips t ON t.trip_id = st.trip_id
JOIN stops s ON s.stop_id = st.stop_id
WHERE t.route_id = route_id_param;

CREATE OR REPLACE TEMP MACRO trips_by_stop(active_date, stop_id_param) AS TABLE
SELECT
    t.trip_id,
    t.route_id,
    r.route_name,
    COALESCE(first_stop.first_stop_name, '') AS first_stop,
    COALESCE(last_stop.last_stop_name, '') AS last_stop,
    t.direction_id,
    st.arrival_time
FROM stop_times st
JOIN trips t ON t.trip_id = st.trip_id
JOIN routes_mobilis r ON r.route_id = t.route_id
JOIN LATERAL (
    SELECT s.stop_name AS first_stop_name
    FROM stop_times st2
    JOIN stops s ON s.stop_id = st2.stop_id
    WHERE st2.trip_id = t.trip_id
    ORDER BY st2.stop_sequence ASC
    LIMIT 1
) AS first_stop ON TRUE
JOIN LATERAL (
    SELECT s.stop_name AS last_stop_name
    FROM stop_times st2
    JOIN stops s ON s.stop_id = st2.stop_id
    WHERE st2.trip_id = t.trip_id
    ORDER BY st2.stop_sequence DESC
    LIMIT 1
) AS last_stop ON TRUE
WHERE
    st.stop_id = stop_id_param
    AND t.service_id IN (SELECT service_id FROM active_services(active_date))
ORDER BY st.arrival_time;
