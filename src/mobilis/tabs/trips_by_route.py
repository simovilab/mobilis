from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Button, DataTable, Input, Label, Select


class TripsByRouteTabContent(Horizontal):
    def compose(self) -> ComposeResult:
        with Vertical(id="route-col-1"):
            with Vertical(id="route-search-panel"):
                yield Label("Search settings", classes="section-title")
                yield Select[str](
                    options=[],
                    prompt="Agency",
                    id="agency-select",
                )
                yield Input(
                    placeholder="YYYY-MM-DD",
                    id="active-date-input",
                )
                yield Input(
                    placeholder="Lower limit interval (e.g. 07:00:00)",
                    id="lower-limit-input",
                )
                yield Input(
                    placeholder="Upper limit interval (e.g. 10:00:00)",
                    id="upper-limit-input",
                )
                yield Button(
                    "Refresh trips",
                    id="apply-route-filters",
                    variant="primary",
                )
            with Vertical(id="route-list-panel"):
                yield Label("Routes", classes="section-title")
                yield DataTable(id="routes-table")
        with Vertical(id="route-col-2"):
            with Vertical(id="trips-dir-0-panel"):
                yield Label("Direction 0", classes="section-title")
                yield DataTable(id="trips-dir-0-table")
            with Vertical(id="trips-dir-1-panel"):
                yield Label("Direction 1", classes="section-title")
                yield DataTable(id="trips-dir-1-table")
        with Vertical(id="route-col-3"):
            yield Label("Stop times", classes="section-title")
            yield DataTable(id="stop-times-table")
