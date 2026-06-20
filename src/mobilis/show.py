"""Rich-formatted ``mobilis show`` output."""

from __future__ import annotations

import os
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table


def show_feeds() -> None:
    """Display downloaded feeds and a summary of the catalog."""
    console = Console()

    # --- Downloaded feeds ---
    feeds_dir = Path.home() / ".mobilis" / "feeds"
    downloaded = Table(
        "Feed ID",
        "GTFS files",
        "DuckDB",
        title="[bold cyan]Downloaded feeds[/bold cyan]",
        show_lines=False,
        border_style="cyan",
    )
    if feeds_dir.exists():
        for entry in sorted(feeds_dir.iterdir()):
            if not entry.is_dir():
                continue
            feed_id = entry.name
            has_files = (entry / "files").is_dir() and any((entry / "files").iterdir())
            has_db = (entry / f"{feed_id}.duckdb").exists()
            downloaded.add_row(
                feed_id,
                "[green]✓[/green]" if has_files else "[dim]–[/dim]",
                "[green]✓[/green]" if has_db else "[dim]–[/dim]",
            )
    if downloaded.row_count == 0:
        downloaded.add_row("[dim]none[/dim]", "", "")

    console.print(downloaded)
    console.print()

    # --- Catalog summary ---
    catalog_path = Path(__file__).parent.parent / "feeds" / "feeds.duckdb"
    if not catalog_path.exists():
        console.print("[yellow]Catalog not found at[/yellow]", str(catalog_path))
        return

    try:
        import duckdb

        con = duckdb.connect(str(catalog_path), read_only=True)
        rows = con.execute(
            """
            SELECT
                id,
                provider,
                COALESCE(feed_name, '') AS feed_name,
                COALESCE(latest_dataset.hosted_url, '') AS hosted_url
            FROM feeds
            WHERE data_type = 'gtfs'
            ORDER BY provider, feed_name
            """
        ).fetchall()
        con.close()
    except Exception as exc:
        console.print(f"[red]Could not read catalog:[/red] {exc}")
        return

    catalog = Table(
        "ID",
        "Provider",
        "Feed name",
        "URL",
        title=f"[bold cyan]Feed catalog (GTFS)[/bold cyan] [dim]— {len(rows)} feeds[/dim]",
        show_lines=False,
        border_style="cyan",
    )
    for feed_id, provider, feed_name, hosted_url in rows:
        catalog.add_row(
            feed_id or "",
            provider or "",
            feed_name or "[dim]–[/dim]",
            "[green]✓[/green]" if hosted_url else "[dim]–[/dim]",
        )

    console.print(catalog)


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
