"""Rich-formatted ``mobilis show`` output."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

CATALOG_PATH = Path(__file__).parent.parent / "feeds" / "feeds.duckdb"
FEEDS_DIR = Path.home() / ".mobilis" / "feeds"


def _print_downloaded(console: Console) -> None:
    feed_ids: list[str] = []
    if FEEDS_DIR.exists():
        feed_ids = sorted(e.name for e in FEEDS_DIR.iterdir() if e.is_dir())

    metadata: dict[str, tuple[str, str]] = {}
    if CATALOG_PATH.exists() and feed_ids:
        try:
            import duckdb

            con = duckdb.connect(str(CATALOG_PATH), read_only=True)
            placeholders = ", ".join("?" * len(feed_ids))
            rows = con.execute(
                f"SELECT id, provider, COALESCE(feed_name, '') FROM feeds WHERE id IN ({placeholders})",
                feed_ids,
            ).fetchall()
            con.close()
            metadata = {r[0]: (r[1] or "", r[2] or "") for r in rows}
        except Exception:
            pass

    table = Table(
        "Feed ID",
        "Provider",
        "Feed name",
        "GTFS files",
        title="[bold cyan]Downloaded feeds[/bold cyan]",
        show_lines=False,
        border_style="cyan",
    )
    for feed_id in feed_ids:
        entry = FEEDS_DIR / feed_id
        has_files = (entry / "files").is_dir() and any((entry / "files").iterdir())
        provider, feed_name = metadata.get(feed_id, ("", ""))
        table.add_row(
            feed_id,
            provider or "[dim]–[/dim]",
            feed_name or "[dim]–[/dim]",
            "[green]✓[/green]" if has_files else "[dim]–[/dim]",
        )
    if table.row_count == 0:
        table.add_row("[dim]none[/dim]", "", "", "")
    console.print(table)


def _print_catalog(console: Console) -> None:
    if not CATALOG_PATH.exists():
        console.print("[yellow]Catalog not found at[/yellow]", str(CATALOG_PATH))
        return
    try:
        import duckdb

        con = duckdb.connect(str(CATALOG_PATH), read_only=True)
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

    table = Table(
        "ID",
        "Provider",
        "Feed name",
        "URL",
        title=f"[bold cyan]Feed catalog (GTFS)[/bold cyan] [dim]— {len(rows)} feeds[/dim]",
        show_lines=False,
        border_style="cyan",
    )
    for feed_id, provider, feed_name, hosted_url in rows:
        table.add_row(
            feed_id or "",
            provider or "",
            feed_name or "[dim]–[/dim]",
            "[green]✓[/green]" if hosted_url else "[dim]–[/dim]",
        )
    console.print(table)


def show_stop(stop_id: str) -> None:
    """Render information about a stop (stub)."""
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
