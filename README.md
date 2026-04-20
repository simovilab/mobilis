# mobilis

> **Status:** early stub. This package currently only scaffolds the CLI/TUI
> surface; GTFS data integration has not been implemented yet.

`mobilis` is a terminal-first tool for exploring public transportation information from [GTFS](https://gtfs.org/) feeds (both static schedules and real-time updates). It aims to give riders, operators and hackers a fast, keyboard-driven way to answer questions like *"when is the next bus at this stop?"* or *"which vehicles are currently running on route 42?"* — without
leaving the terminal.

It is built with:

- [`rich`](https://github.com/Textualize/rich) for nicely formatted one-shot output (e.g. `mobilis show stop ABC123`).
- [`textual`](https://github.com/Textualize/textual) for the interactive dashboards (`mobilis go`, `mobilis explore`).
- [`uv`](https://github.com/astral-sh/uv) for packaging and environment management.

## Planned commands

```
mobilis go                      # passenger TUI: live transit info for riders
mobilis explore                 # analyst TUI: GTFS feed stats and export
mobilis show stop ABC123        # show details for a stop by code/id
```

More subcommands (routes, trips, vehicles, alerts, …) will follow.

## Installation

Once published to PyPI:

```
pip install mobilis
# or
uv tool install mobilis
```

## Development

```
uv sync
uv run mobilis --help
uv build          # produce sdist + wheel in dist/
```

## License

See [`LICENSE`](./LICENSE).
