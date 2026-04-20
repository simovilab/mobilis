---
icon: lucide/bus
---

# Mobilis

`mobilis` is a terminal-first tool for exploring public transportation data
from [GTFS](https://gtfs.org/) feeds — both static schedules and real-time
updates. It targets two audiences from a single codebase:

- **Passengers and riders**, through a live dashboard that answers
  everyday questions such as _"when is the next bus?"_ or _"is my route
  delayed?"_.
- **Researchers, operators and analysts**, through a feed explorer that
  summarizes, inspects and exports GTFS datasets.

!!! warning "Status: early stub"
    Mobilis currently only scaffolds the CLI, TUIs and documentation. No real GTFS data is parsed yet — every table, metric and alert you see   in the app is mock data. These pages describe the planned feature set.

## Commands at a glance

```bash
mobilis go                      # passenger TUI: live transit info for riders
mobilis explore                 # analyst TUI: GTFS feed stats and export
mobilis show stop ABC123        # one-shot details for a stop by code/id
```

Each command has its own page:

- [Installation](installation.md) — how to get `mobilis` on your machine.
- [`mobilis go`](go.md) — the passenger dashboard.
- [`mobilis explore`](explore.md) — the GTFS analytics TUI.
- [`mobilis show`](show.md) — Rich-formatted one-shot lookups.

## Design goals

- **Keyboard-first.** Everything usable without leaving the terminal.
- **Two audiences, one tool.** A clear split between passenger-facing
  views (`go`) and analyst-facing views (`explore`).
- **Standards-based.** Consumes GTFS Schedule and GTFS Realtime as-is,
  without a custom intermediate format.
- **Scriptable.** Anything visible in a TUI should also be reachable
  through a one-shot `mobilis show ...` command suitable for piping.
