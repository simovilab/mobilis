from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, DataTable, Input, Label


class TransitSystemTabContent(Vertical):
    def compose(self) -> ComposeResult:
        with Horizontal(id="transit-search-panel"):
            yield Input(
                placeholder="Search provider or feed name",
                id="feed-search-input",
            )
            yield Button("Search", id="search-feed-list")
            yield Button("Refresh", id="refresh-feed-list")
            yield Button(
                "Load selected feed",
                id="load-selected-feed",
                variant="primary",
            )
        with Horizontal(id="transit-place-panel"):
            yield Input(
                placeholder="Search place",
                id="place-search-input",
            )
            yield Button("Find places", id="search-place-list")
            yield Button("Find feeds for place", id="search-feeds-by-place")
        yield Label("Place matches", classes="section-title")
        yield DataTable(id="place-results-table")
        yield Label("No place selected.", id="selected-place-label")
        yield Label("Downloaded feeds", classes="section-title")
        yield DataTable(id="downloaded-feeds-table")
        yield Label("No feed selected.", id="selected-feed-label")
        yield Label("Catalog feeds", classes="section-title")
        yield DataTable(id="feed-catalog-table")
