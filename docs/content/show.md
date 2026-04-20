---
icon: lucide/signpost
---

# Show

`mobilis show` is the **one-shot, non-interactive** counterpart to the `go` and `explore` TUIs. It prints a Rich-formatted summary for a single resource and exits, making it well suited for scripts, aliases and quick lookups.

```bash
mobilis show <resource> <id>
```

!!! warning "Status: stub"
    Only `mobilis show stop` is wired up, and it returns placeholder
    fields. Real GTFS lookups will be added as the data layer lands.

## Available today

### Stop

Print identifying information for a stop given its code or id.

```
mobilis show stop ABC123
```

Planned fields:

* Stop code and internal id.
* Human-readable name and parent station, if any.
* Coordinates and zone id.
* Routes that serve the stop.
* Wheelchair boarding and other accessibility flags.

## Planned resources

The goal is for every major GTFS entity to be reachable through
`mobilis show`:

* `mobilis show route <route_id>` — name, type, agency, served stops, active alerts.
* `mobilis show trip <trip_id>` — shape, calendar, full stop-time sequence.
* `mobilis show vehicle <vehicle_id>` — current position, occupancy and assigned trip.
* `mobilis show alert <alert_id>` — cause, effect, affected entities and active period.
* `mobilis show agency <agency_id>` — fleet- and network-level summary.

## Output formats (planned)

* Default: Rich panel, as today.
* `--json` — machine-readable output for piping.
* `--plain` — minimal text, no colors, suitable for `grep`/`awk`.
