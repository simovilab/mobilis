"""Rich-formatted ``mobilis info`` output (stub)."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table


def show_stop(stop_id: str) -> None:
    """Render information about a stop.

    This is a placeholder that shows how the final output will look.
    Real GTFS lookups will be wired in later.
    """
    console = Console()

    table = Table(show_header=False, box=None, pad_edge=False)
    table.add_column(style="bold cyan")
    table.add_column()
    table.add_row("Stop ID", stop_id)
    table.add_row("Name", "[dim]unknown (stub)[/dim]")
    table.add_row("Location", "[dim]unknown (stub)[/dim]")
    table.add_row("Routes", "[dim]unknown (stub)[/dim]")

    console.print(
        Panel(
            table,
            title=f"[bold]Stop {stop_id}[/bold]",
            subtitle="[dim]mobilis stub — GTFS integration pending[/dim]",
            border_style="cyan",
        )
    )
