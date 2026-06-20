---
icon: lucide/database
---

# mobilis feeds

`mobilis feeds` manages the GTFS feeds stored locally under `~/.mobilis/feeds/`.

```bash
mobilis feeds <subcommand> [options]
```

---

## mobilis feeds show

Lists downloaded feeds and/or feeds from the bundled catalog.

```bash
mobilis feeds show              # both sections
mobilis feeds show --downloaded # downloaded feeds only  (short: -d)
mobilis feeds show --catalog     # catalog only          (short: -c)
```

### Downloaded feeds

Shows every directory found in `~/.mobilis/feeds/` with catalog metadata looked up from the bundled `feeds.duckdb`:

| Column | Description |
|---|---|
| Feed ID | Directory name (= feed identifier) |
| Provider | Organisation name from the Mobility Database |
| Feed name | Feed-level name from the Mobility Database (if set) |
| GTFS files | Whether extracted `.txt` files are present |

Feeds added manually (e.g. `incofer`, `mbta`) show `–` for Provider and Feed name because they are not in the catalog.

### Catalog

Shows all GTFS feeds from the Mobility Database catalog:

| Column | Description |
|---|---|
| ID | Catalog identifier (`mdb-*`, `tld-*`, `ntd-*`) |
| Provider | Operating organisation |
| Feed name | Feed-level name (optional in the catalog) |
| URL | `✓` if a downloadable ZIP URL is available |

---

## mobilis feeds update

Re-downloads and re-imports a feed from its catalog URL.

```bash
mobilis feeds update <feed_id>
```

The command:

1. Looks up `latest_dataset.hosted_url` in the catalog for `<feed_id>`.
2. Clears the existing `files/` directory and `.duckdb` database.
3. Downloads and extracts the GTFS ZIP.
4. Re-imports all tables with `import_gtfs`.

!!! note
    Only feeds with a catalog entry (`mdb-*` / `tld-*` / `ntd-*`) can be updated this way. Manually created feeds (e.g. `incofer`) are not in the catalog and must be updated by hand.

---

## mobilis feeds remove

Deletes a feed's local directory entirely.

```bash
mobilis feeds remove <feed_id>
```

This removes `~/.mobilis/feeds/<feed_id>/` including all extracted files and the DuckDB database. The action is immediate and irreversible; download again with `mobilis feeds update` or from within `mobilis go`.

---

## Feed storage layout

```
~/.mobilis/
└── feeds/
    └── <feed_id>/
        ├── files/              ← extracted GTFS .txt files
        │   ├── agency.txt
        │   ├── routes.txt
        │   ├── stops.txt
        │   ├── trips.txt
        │   ├── stop_times.txt
        │   ├── calendar.txt        (optional)
        │   ├── calendar_dates.txt  (optional, ≥ 1 of these two required)
        │   ├── shapes.txt
        │   └── feed_info.txt       (optional)
        └── <feed_id>.duckdb    ← imported DuckDB database
```

## Feed import

Feed import is handled by `src/mobilis/import_gtfs.py`. It reads the GTFS `.txt` files and creates typed DuckDB tables. Key behaviour:

- `calendar.txt` and `calendar_dates.txt` are both optional; at least one must be present. Whichever is missing is replaced by an empty stub table so that queries still work.
- `feed_info.txt` is optional; when present, its data is stored in a `feed_info` table and shown in the **Feed info** tab of `mobilis go`.
- `agency_id` in `routes.txt` is optional for single-agency feeds; the importer fills it from `agency.txt` automatically.
- `arrival_time` and `departure_time` are stored as `INTERVAL` (not `TIME`) to support GTFS values beyond `23:59:59`.
