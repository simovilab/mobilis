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