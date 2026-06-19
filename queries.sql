-- The routes for an agency for a certain mode

SELECT
    route_id,
    route_short_name
FROM routes
WHERE 
    agency_id = '1' AND 
    route_type = 3;

-- The trips in a route

SELECT
    trip_id,
    shape_id
FROM trips
WHERE
    route_id = '39' AND
    service_id = 'SummerSunday' AND
    direction_id = 0;

-- The trips in a stop

SELECT
    t.route_id,
    s_last.stop_name AS last_stop,
    st.arrival_time
FROM stop_times st
    JOIN trips t ON st.trip_id = t.trip_id
    JOIN stops s ON st.stop_id = s.stop_id
    JOIN LATERAL (
        SELECT stop_name 
        FROM stop_times lst
        JOIN stops ls ON lst.stop_id = ls.stop_id
        WHERE lst.trip_id = t.trip_id
        ORDER BY lst.stop_sequence DESC
        LIMIT 1
    ) AS s_last ON TRUE
WHERE
    st.stop_id = '61365' AND
    t.service_id = 'SummerWeekday' AND
    t.direction_id = 0
ORDER BY st.arrival_time;

-- The sequence of stops in a trip

SELECT 
    s.stop_name,
    st.arrival_time
FROM stop_times st
    JOIN stops s ON st.stop_id = s.stop_id
    JOIN trips t ON st.trip_id = t.trip_id
WHERE 
    t.route_id = '39' AND 
    t.service_id = 'SummerSunday' AND 
    t.direction_id = 0 AND 
    t.trip_id = '77137007'
ORDER BY st.stop_sequence;

-- DuckDB macro to get the first departure time for a trip (the departure time is actually stored in the stop_times table as INTERVAL)

CREATE OR REPLACE MACRO first_departure_time(t_id) AS (
    SELECT arrival_time
    FROM stop_times
    WHERE stop_times.trip_id = t_id
    ORDER BY stop_sequence
    LIMIT 1
);

-- Active trips for a route today (calendar + calendar_dates exceptions)

WITH 
    base_services AS (
        SELECT c.service_id
        FROM calendar c
        WHERE
            current_date BETWEEN c.start_date AND c.end_date
            AND CASE dayofweek(current_date)
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
        WHERE cd.date = current_date
            AND cd.exception_type = 1
    ),
    removed_services AS (
        SELECT cd.service_id
        FROM calendar_dates cd
        WHERE cd.date = current_date
            AND cd.exception_type = 2
    ),
    active_services AS (
        (
            SELECT service_id FROM base_services
            UNION
            SELECT service_id FROM added_services
        )
        EXCEPT
        SELECT service_id FROM removed_services
    )
    SELECT
        t.trip_id,
        t.route_id,
        t.service_id,
        t.direction_id,
        first_departure_time(t.trip_id) AS trip_departure_time
    FROM trips t
    WHERE
        t.route_id = '39' AND direction_id = 0
        AND t.service_id IN (SELECT service_id FROM active_services)
    ORDER BY trip_departure_time ASC;
