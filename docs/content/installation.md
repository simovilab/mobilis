---
icon: lucide/rocket
---

# Installation

Mobilis targets Python 3.10+ and is managed with [uv](https://github.com/astral-sh/uv).

## From source (recommended for v0.1)

```bash
git clone https://github.com/simovilab/mobilis.git
cd mobilis
uv sync
uv run mobilis --help
```

Verify the version:

```bash
uv run mobilis --version
```

## From PyPI

Once published:

```bash
pip install mobilis
# or, as an isolated tool:
uv tool install mobilis
```

## Requirements

| Requirement | Notes |
|---|---|
| Python ≥ 3.10 | Tested on 3.10 – 3.13 |
| Terminal with 256-color + Unicode | Virtually all modern terminals qualify |
| Internet access | Required only for the initial feed download |

## Feed data directory

Mobilis stores downloaded feed data under:

```
~/.mobilis/
└── feeds/
    └── <feed_id>/
        ├── files/          ← extracted GTFS .txt files
        └── <feed_id>.duckdb
```

This directory is created automatically the first time a feed is loaded.

## Development build

```bash
uv build          # produces sdist + wheel in dist/
```

To run directly from the source tree without installing:

```bash
PYTHONPATH=src uv run python -m mobilis go
```
