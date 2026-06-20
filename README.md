# mobilis

> **v0.1 alpha** — the passenger TUI and feed-management CLI are functional. GTFS feeds are downloaded, imported into DuckDB, and browsable from the terminal.

`mobilis` is a terminal-first tool for exploring public transportation data from [GTFS](https://gtfs.org/) static schedule feeds. It lets riders, operators and developers browse transit schedules without leaving the terminal.

Built with:

- [`textual`](https://github.com/Textualize/textual) — interactive TUI dashboards.
- [`rich`](https://github.com/Textualize/rich) — formatted one-shot CLI output.
- [`duckdb`](https://duckdb.org/) — embedded analytics engine for fast GTFS queries.
- [`uv`](https://github.com/astral-sh/uv) — packaging and environment management.

## Commands

```bash
# Passenger TUI — browse schedules for any GTFS feed
mobilis go
mobilis go mdb-466          # skip the feed selector, load feed directly

# Feed management
mobilis feeds show          # list downloaded feeds + catalog
mobilis feeds show -d       # downloaded feeds only
mobilis feeds show -c       # catalog only
mobilis feeds update mdb-466
mobilis feeds remove mdb-466

# One-shot output (Rich-formatted)
mobilis show stop ABC123
```

## Quick start

```bash
git clone https://github.com/simovilab/mobilis.git
cd mobilis
uv sync
uv run mobilis go
```

## Documentation

Full documentation is in [`docs/`](./docs/).

## License

See [`LICENSE`](./LICENSE).
