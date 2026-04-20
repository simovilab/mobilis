---
icon: lucide/rocket
---

# Installation

Mobilis is a Python package. It targets Python 3.10+ and ships a single
console script, `mobilis`.

## From PyPI

Once the first release is out:

```bash
pip install mobilis
```

Or, as an isolated tool managed by [uv](https://github.com/astral-sh/uv):

```bash
uv tool install mobilis
```

Verify the installation:

```bash
mobilis --version
mobilis --help
```

## From source

Clone the repository and sync a development environment with `uv`:

```bash
git clone https://github.com/simovilab/mobilis.git
cd mobilis
uv sync
uv run mobilis --help
```

To produce distributable artifacts:

```bash
uv build          # writes sdist + wheel into dist/
```

## Requirements

- Python 3.10 or newer.
- A terminal emulator with 256-color and Unicode support (most modern
  terminals qualify).
- For `mobilis explore` against remote feeds: network access to the
  configured GTFS endpoint.
