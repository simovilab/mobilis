from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import DataTable, Label


class FeedInfoTabContent(Vertical):
    def compose(self) -> ComposeResult:
        yield Label("Feed information", classes="section-title")
        yield DataTable(id="feed-info-table")
        yield Label("Feed stats", classes="section-title")
        yield DataTable(id="feed-stats-table")
