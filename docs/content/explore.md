---
icon: lucide/scan-search
---

# Explore

`mobilis explore` launches the **analyst TUI**: a companion to [`mobilis go`](go.md) aimed at researchers, operators and data engineers who want to inspect, summarize and export GTFS feeds.

```bash
mobilis explore
```

!!! warning "Status: stub"
    The current screen ships placeholder stats and a mock tables list.
    No GTFS file is actually parsed yet.

## Planned features

### Feed sources

* Open a local GTFS `.zip` or extracted directory.
* Open a remote feed by URL (static schedule and/or GTFS-RT).
* Open a curated transit catalog entry by agency/feed id.

### Summary tab

* High-level counts: agencies, routes, stops, trips, stop times.
* Service calendar coverage (start/end dates, active weekdays).
* Spatial bounding box and centroid of the network.
* Feed validation summary (warnings and errors).

### Tables tab

* Browsable list of every file in the feed (`agency.txt`,
  `stops.txt`, `routes.txt`, …) with row counts.
* Per-table data grid with column filtering and sorting.
* Quick schema view: columns, types, nullability, sample values.

### Export tab

* Export the active view, selection or whole table to:
    * CSV
    * Parquet
    * GeoJSON (for stops, shapes and derived layers)
* Save reproducible "exports" as named recipes in the project.
### Keybindings

* ++q++ — quit.
* ++o++ — open a feed.
* ++e++ — export current view.

Fuzzy-find (++ctrl+p++), jump-to-table and per-column filter bindings
will be added as the underlying features land.

## Non-goals

* Editing GTFS feeds. `mobilis explore` is read-only by design.
* Being a routing engine. Use a dedicated tool (OpenTripPlanner, OSRM,
  Valhalla, ...) if you need itineraries.
