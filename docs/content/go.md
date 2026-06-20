---
icon: lucide/fullscreen
---

# Go

`mobilis go` launches the **passenger-facing TUI**: a live dashboard aimed at riders who want quick answers about nearby stops, upcoming departures and service disruptions.

```bash
mobilis go
```

!!! info "Status: early scaffold"
    The command now includes a **Transit System** page that lists GTFS feeds from `src/feeds/feeds.duckdb` and can load a selected feed into `~/.mobilis/feeds/<feed_id>/`.
    After loading, it enables the `Trips by route` and `Trips by stop` flows.

## Planned features

### Stops sidebar

- Favorite / recent / nearby stops (geolocation-based, opt-in).
- Search by stop code, name or route.
- Highlight of stops with active alerts.

### Departures tab

- Live, auto-refreshing list of upcoming departures for the selected stop.
- Route, headsign, scheduled ETA and real-time delay/early indicator.
- Color-coded status (on time, delayed, early, cancelled).

### Service alerts tab

- Streaming log of active GTFS-RT service alerts.
- Filter by route, stop or severity.

### Occupancy tab

- Current vehicle occupancy for approaching trips, when the feed
  publishes it.
- Short-term history as a sparkline.

### Keybindings

- ++q++ — quit.
- ++r++ — refresh data.
- ++a++ — add/test an alert (stub action).
  Additional bindings (search, favorites, follow-a-vehicle) will land
  alongside the matching features.

## Configuration (planned)

- Default feed URL(s) and agency filter.
- Units (minutes vs. absolute time) and locale.
- Theme overrides via Textual CSS.
