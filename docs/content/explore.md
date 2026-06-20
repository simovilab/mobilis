---
icon: lucide/scan-search
---

# mobilis explore

`mobilis explore` will launch an **analyst TUI** aimed at researchers, operators and data engineers who need to inspect, summarise and export GTFS feeds in depth.

```bash
mobilis explore
```

!!! warning "Status: planned"
    `mobilis explore` is a stub in v0.1. The command starts but shows no real data. Development will begin after the passenger TUI (`mobilis go`) stabilises.

---

## Planned features

### Feed sources

- Open a local GTFS `.zip` or extracted directory.
- Open a remote feed by URL.
- Load any feed already imported by `mobilis feeds`.

### Summary tab

- High-level counts: agencies, routes, stops, trips, stop times.
- Service calendar coverage (start/end dates, active weekdays).
- Spatial bounding box and centroid of the network.

### Tables tab

- Browsable list of every file in the feed with row counts.
- Per-table data grid with column filtering and sorting.
- Quick schema view: column names, types and sample values.

### Export tab

- Export any table or selection to CSV, Parquet or GeoJSON.

### Keybindings (planned)

| Key | Action |
|-----|--------|
| ++q++ | Quit |
| ++o++ | Open a feed |
| ++e++ | Export current view |

---

## Non-goals

- **Editing feeds.** `mobilis explore` is read-only by design.
- **Routing.** For itinerary planning use a dedicated engine (OpenTripPlanner, Valhalla, …).
