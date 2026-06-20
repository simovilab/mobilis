---
icon: lucide/signpost
---

# mobilis show

`mobilis show` prints Rich-formatted information about a transit resource and exits immediately. It is well suited for scripts, aliases and quick terminal lookups.

```bash
mobilis show <resource> [arguments]
```

---

## mobilis show stop

```bash
mobilis show stop <stop_id>
```

Prints a summary panel for the given stop ID.

!!! warning "Status: stub"
    The stop panel currently shows placeholder values. Real GTFS lookups (name, coordinates, routes served) will be added in a future release.

---

## Planned resources

The goal is for every major GTFS entity to be reachable through `mobilis show`:

| Command | Description |
|---|---|
| `mobilis show route <route_id>` | Name, type, agency, served stops, active alerts |
| `mobilis show trip <trip_id>` | Shape, calendar, full stop-time sequence |
| `mobilis show agency <agency_id>` | Fleet- and network-level summary |

## Output formats (planned)

- **Default:** Rich-formatted panel, as today.
- `--json` — machine-readable JSON for piping.
- `--plain` — minimal text without colour codes, suitable for `grep` / `awk`.
