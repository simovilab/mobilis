from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import DataTable, Input, Label, Select


class TripsByStopTabContent(Horizontal):
    def compose(self) -> ComposeResult:
        with Vertical(id="stop-col-1"):
            yield Label("Search settings", classes="section-title")
            yield Select[str](
                options=[],
                prompt="Route ID",
                id="stop-route-select",
            )
            yield Input(
                placeholder="Stop name (coming soon)",
                disabled=True,
                id="stop-name-input",
            )
            yield Input(
                placeholder="Place (coming soon)",
                disabled=True,
                id="place-input",
            )
            yield Input(
                placeholder="Radius (coming soon)",
                disabled=True,
                id="radius-input",
            )
        with Vertical(id="stop-col-2"):
            yield Label("Stops", classes="section-title")
            yield DataTable(id="stops-table")
        with Vertical(id="stop-col-3"):
            yield Label("Next arrivals", classes="section-title")
            yield DataTable(id="arrivals-table")
