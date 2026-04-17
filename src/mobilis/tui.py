"""Textual TUI dashboard for mobilis (stub).

This is intentionally a toy: no real GTFS data is fetched. The goal is to
showcase a few Textual widgets we'll use in the real dashboard (data tables,
tabs, progress bars, sparklines, a log, keybindings, and custom CSS).
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta

from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    Label,
    ProgressBar,
    RichLog,
    Sparkline,
    TabbedContent,
    TabPane,
)

# --- Mock data ---------------------------------------------------------------

MOCK_STOPS: list[tuple[str, str, str]] = [
    ("ABC123", "Main St & 5th", "Inbound"),
    ("ABC124", "Main St & 7th", "Inbound"),
    ("XYZ900", "Central Station", "Both"),
    ("LMN045", "Riverside Park", "Outbound"),
    ("QRS777", "Airport Terminal 2", "Both"),
]

MOCK_ROUTES: list[tuple[str, str, str]] = [
    ("42", "Downtown Loop", "bus"),
    ("L1", "Red Line", "light rail"),
    ("N3", "Night Owl", "bus"),
    ("X9", "Airport Express", "bus"),
]

_STATUSES = [
    ("on time", "green"),
    ("+1 min", "yellow"),
    ("+3 min", "yellow"),
    ("+7 min", "red"),
    ("early", "cyan"),
]


# --- Widgets -----------------------------------------------------------------


class StopsTable(DataTable):
    """Left-hand table listing known stops."""

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.zebra_stripes = True
        self.add_columns("Code", "Name", "Direction")
        for row in MOCK_STOPS:
            self.add_row(*row)


class DeparturesTable(DataTable):
    """Upcoming departures for the selected stop."""

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.zebra_stripes = True
        self.add_columns("Route", "Headsign", "ETA", "Status")
        self.refresh_rows()

    def refresh_rows(self) -> None:
        self.clear()
        now = datetime.now()
        for route, name, _mode in MOCK_ROUTES:
            eta = now + timedelta(minutes=random.randint(1, 20))
            status, color = random.choice(_STATUSES)
            self.add_row(
                Text(route, style="bold cyan"),
                name,
                eta.strftime("%H:%M"),
                Text(status, style=color),
            )


# --- App ---------------------------------------------------------------------


class MobilisApp(App):
    """Placeholder dashboard app.

    Future versions will render live GTFS feeds: stops, routes, vehicles
    and service alerts. For now everything here is mock data.
    """

    CSS = """
    Screen {
        layout: vertical;
    }

    #body {
        height: 1fr;
    }

    #sidebar {
        width: 38;
        border-right: solid $primary 50%;
        padding: 0 1;
    }

    #content {
        padding: 0 1;
    }

    .section-title {
        padding: 1 0 0 0;
        color: $accent;
        text-style: bold;
    }

    StopsTable, DeparturesTable {
        height: 1fr;
    }

    ProgressBar {
        margin: 1 0;
    }

    Sparkline {
        height: 3;
        margin: 1 0;
    }

    RichLog {
        height: 1fr;
        background: $surface;
    }
    """

    TITLE = "mobilis"
    SUB_TITLE = "GTFS in the terminal — stub dashboard"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh data"),
        ("a", "add_alert", "Add alert"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="body"):
            with Vertical(id="sidebar"):
                yield Label("Stops", classes="section-title")
                yield StopsTable(id="stops")
            with Vertical(id="content"):
                with TabbedContent(initial="departures"):
                    with TabPane("Departures", id="departures"):
                        yield DeparturesTable(id="departures-table")
                    with TabPane("Service alerts", id="alerts"):
                        yield RichLog(
                            id="alerts-log",
                            highlight=True,
                            markup=True,
                            wrap=True,
                        )
                    with TabPane("Occupancy", id="occupancy"):
                        with Vertical():
                            yield Label(
                                "Vehicle occupancy (mock)",
                                classes="section-title",
                            )
                            yield ProgressBar(
                                total=100,
                                show_eta=False,
                                id="occupancy-bar",
                            )
                            yield Label(
                                "Passengers/minute — last 30 samples",
                                classes="section-title",
                            )
                            yield Sparkline(
                                [random.randint(0, 100) for _ in range(30)],
                                id="spark",
                            )
        yield Footer()

    def on_mount(self) -> None:
        log = self.query_one("#alerts-log", RichLog)
        log.write("[bold red]DELAY[/] Route 42: +5 min due to traffic.")
        log.write("[bold yellow]DETOUR[/] L1 rerouted via 8th Ave.")
        log.write("[green]OK[/] N3 running on schedule.")
        self.query_one("#occupancy-bar", ProgressBar).update(
            progress=random.randint(10, 95)
        )

    # --- Actions -------------------------------------------------------------

    def action_refresh(self) -> None:
        self.query_one("#departures-table", DeparturesTable).refresh_rows()
        self.query_one("#occupancy-bar", ProgressBar).update(
            progress=random.randint(10, 95)
        )
        self.query_one("#spark", Sparkline).data = [
            random.randint(0, 100) for _ in range(30)
        ]
        self.query_one("#alerts-log", RichLog).write(
            f"[dim]{datetime.now():%H:%M:%S}[/] refreshed mock data"
        )

    def action_add_alert(self) -> None:
        route, headsign, _ = random.choice(MOCK_ROUTES)
        self.query_one("#alerts-log", RichLog).write(
            f"[bold magenta]INFO[/] {route} → {headsign}: new service note."
        )


def run_dashboard() -> None:
    """Entry point used by the CLI to launch the TUI."""
    MobilisApp().run()
