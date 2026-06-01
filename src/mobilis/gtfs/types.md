These are the field types in GTFS Schedule:

- **Color**: Some values could be parsed as strings (e.g., `F383DC`) and others as integers (e.g., `859246|`), so they must be cast as `VARCHAR`.
- Currency code
- Currency amount
- **Date**: Service day in the non-traditional YYYYMMDD format that will be parsed as integer, so they must be converted to a `DATE` format.
- Email
- Enum
- ID
- Language code
- **Latitude**: Along with longitude, a new geometry column will be created by combining the two into a `POINT` data type for easier geospatial queries.
- **Longitude**: Along with latitude, a new geometry column will be created by combining the two into a `POINT` data type for easier geospatial queries.
- Float
- Integer
- **Phone number**: The formatting could vary widely, so they must be cast as `VARCHAR`.
- **Time** - Time in the HH:MM:SS format (H:MM:SS is also accepted). The time is measured from "noon minus 12h" of the service day (effectively midnight except for days on which daylight savings time changes occur). For times occurring after midnight on the service day, enter the time as a value greater than 24:00:00 in HH:MM:SS. They must be converted to an `INTERVAL` data type to avoid issues with times greater than 24 hours.
  Example: 14:30:00 for 2:30PM or 25:35:00 for 1:35AM on the next day.
- Local time - Time in the HH:MM:SS format (H:MM:SS is also accepted). Represents a wall-clock time
- Text
- Timezone
- URL

The ones that require special handling are: color, date, time, (latitude, longitude), and phone number.

Most field types are properly imported by DuckDB, but some require manual parsing and validation. For example, the `Date` type is imported as an integer (e.g., 20240101) and needs to be converted to a `DATE` format for easier manipulation. Similarly, `Time` fields are imported as `TIME` but require conversion to an `INTERVAL` data type.

In that sense, the following standard GTFS tables require additional parsing and transformation:

| Table                  | Date fields                        | Time fields                                                                                    | Other fields                      |
| ---------------------- | ---------------------------------- | ---------------------------------------------------------------------------------------------- | --------------------------------- |
| `agency`               | None                               | None                                                                                           | `agency_phone`                    |
| `stops`                | None                               | None                                                                                           | `stop_lat`, `stop_lon`            |
| `routes`               | None                               | None                                                                                           | `route_color`, `route_text_color` |
| `trips`                | None                               | None                                                                                           | None                              |
| `stop_times`           | None                               | `arrival_time`, `departure_time`, `start_pickup_drop_off_window`, `end_pickup_drop_off_window` | None                              |
| `calendar`             | `start_date`, `end_date`           | None                                                                                           | None                              |
| `calendar_dates`       | `date`                             | None                                                                                           | None                              |
| `fare_attributes`      | None                               | None                                                                                           | None                              |
| `fare_rules`           | None                               | None                                                                                           | None                              |
| `timeframes`           | None                               | None (local times)                                                                             | None                              |
| `rider_categories`     | None                               | None                                                                                           | None                              |
| `fare_media`           | None                               | None                                                                                           | None                              |
| `fare_products`        | None                               | None                                                                                           | None                              |
| `fare_leg_rules`       | None                               | None                                                                                           | None                              |
| `fare_leg_join_rules`  | None                               | None                                                                                           | None                              |
| `fare_transfer_rules`  | None                               | None                                                                                           | None                              |
| `areas`                | None                               | None                                                                                           | None                              |
| `stop_areas`           | None                               | None                                                                                           | None                              |
| `networks`             | None                               | None                                                                                           | None                              |
| `route_networks`       | None                               | None                                                                                           | None                              |
| `shapes`               | None                               | None                                                                                           | `shape_pt_lat`, `shape_pt_lon`    |
| `frequencies`          | None                               | `start_time`, `end_time`                                                                       | None                              |
| `transfers`            | None                               | None                                                                                           | None                              |
| `pathways`             | None                               | None                                                                                           | None                              |
| `levels`               | None                               | None                                                                                           | None                              |
| `location_groups`      | None                               | None                                                                                           | None                              |
| `location_group_stops` | None                               | None                                                                                           | None                              |
| `locations.geojson`    | None                               | None                                                                                           | `geometry.coordinates`            |
| `booking_rules`        | None                               | `prior_notice_last_time`, `prior_notice_start_time`                                            | `phone_number`                    |
| `translations`         | None                               | None                                                                                           | `translation`, `field_value`      |
| `feed_info`            | `feed_start_date`, `feed_end_date` | None                                                                                           | None                              |
| `attributions`         | None                               | None                                                                                           | `attribution_phone`               |
