"""Command-line interface for mobilis.

Exposes three top-level commands:

* ``mobilis go`` — launch the passenger-facing Textual TUI dashboard.
* ``mobilis explore`` — launch the analyst/researcher TUI for inspecting
  and exporting GTFS feed data.
* ``mobilis show <resource> <id>`` — print information about a transit
  resource (currently only ``stop``) using Rich for pretty output.

This is a minimal stub; real GTFS data fetching will arrive in a future
release.
"""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

from . import __version__


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mobilis",
        description=(
            "Visualize public transportation information from GTFS feeds "
            "in the terminal."
        ),
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # mobilis go — passenger-facing TUI
    subparsers.add_parser(
        "go",
        help="Start the passenger TUI dashboard.",
        description=(
            "Start the mobilis passenger TUI dashboard (powered by Textual) "
            "with live transit information for riders."
        ),
    )

    # mobilis explore — researcher/analytics TUI
    subparsers.add_parser(
        "explore",
        help="Start the GTFS explorer TUI.",
        description=(
            "Start the mobilis explorer TUI for analyzing and exporting "
            "GTFS feed data (stats, tables, etc.)."
        ),
    )

    # mobilis show <resource> <id>
    show = subparsers.add_parser(
        "show",
        help="Show information about a transit resource.",
        description="Show information about a transit resource.",
    )
    show_sub = show.add_subparsers(dest="resource", required=True)

    stop = show_sub.add_parser(
        "stop",
        help="Show information about a stop.",
        description="Show information about a stop by stop code or id.",
    )
    stop.add_argument("stop_id", help="Stop code or id, e.g. ABC123.")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "go":
        from .go import run_mobilis_go

        run_mobilis_go()
        return 0

    if args.command == "explore":
        from .explore import run_mobilis_explore

        run_mobilis_explore()
        return 0

    if args.command == "show" and args.resource == "stop":
        from .show import show_stop

        show_stop(args.stop_id)
        return 0

    parser.error(f"Unknown command: {args.command!r}")
    return 2  # pragma: no cover — argparse exits before reaching here


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
