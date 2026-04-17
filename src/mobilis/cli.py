"""Command-line interface for mobilis.

Exposes two top-level commands:

* ``mobilis run`` — launch the Textual TUI dashboard.
* ``mobilis info <resource> <id>`` — print information about a transit
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

    # mobilis run
    subparsers.add_parser(
        "run",
        help="Start the TUI dashboard.",
        description="Start the mobilis TUI dashboard (powered by Textual).",
    )

    # mobilis info <resource> <id>
    info = subparsers.add_parser(
        "info",
        help="Show information about a transit resource.",
        description="Show information about a transit resource.",
    )
    info_sub = info.add_subparsers(dest="resource", required=True)

    stop = info_sub.add_parser(
        "stop",
        help="Show information about a stop.",
        description="Show information about a stop by stop code or id.",
    )
    stop.add_argument("stop_id", help="Stop code or id, e.g. ABC123.")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        from .tui import run_dashboard

        run_dashboard()
        return 0

    if args.command == "info" and args.resource == "stop":
        from .info import show_stop

        show_stop(args.stop_id)
        return 0

    parser.error(f"Unknown command: {args.command!r}")
    return 2  # pragma: no cover — argparse exits before reaching here


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
