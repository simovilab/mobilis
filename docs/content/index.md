---
icon: lucide/bus
---

# Mobilis

`mobilis` is a terminal-first tool for exploring public transportation schedules from [GTFS](https://gtfs.org/) static feeds. It lets riders, operators and developers download any feed from the global [Mobility Database](https://mobilitydatabase.org/) catalog, import it locally, and browse agencies, routes, stops and timetables — entirely from the terminal.

!!! tip "v0.1 alpha"
    The passenger TUI and feed-management CLI are fully functional.
    GTFS feeds are downloaded on demand, imported into an embedded DuckDB database, and browsable through keyboard-driven screens.

## Commands at a glance

```bash
# Passenger TUI
mobilis go                  # start and choose a feed interactively
mobilis go mdb-466          # start and load feed mdb-466 immediately

# Feed management
mobilis feeds show          # list downloaded feeds + catalog
mobilis feeds show -d       # downloaded feeds only
mobilis feeds show -c       # full catalog only
mobilis feeds update mdb-466
mobilis feeds remove mdb-466

# One-shot output
mobilis show stop ABC123
```

## Pages

- [Installation](installation.md) — get `mobilis` running on your machine.
- [`mobilis go`](go.md) — the interactive passenger TUI.
- [`mobilis feeds`](feeds.md) — download and manage GTFS feeds.
- [`mobilis show`](show.md) — Rich-formatted one-shot lookups.
- [`mobilis explore`](explore.md) — GTFS analytics TUI *(planned)*.

## Design principles

- **Keyboard-first.** The entire TUI is navigable without a mouse.
- **Local-first.** Feeds are downloaded once into `~/.mobilis/feeds/` and queried locally with DuckDB — no remote server required after the initial download.
- **Standards-based.** Consumes GTFS Schedule as-is; no custom intermediate format.
- **Open catalog.** Feed discovery uses the open Mobility Database catalog bundled with the package.
