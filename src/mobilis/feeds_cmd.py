"""CLI commands for managing GTFS feeds (``mobilis feeds …``)."""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

import requests
from rich.console import Console

from .show import _print_catalog, _print_downloaded

CATALOG_PATH = Path(__file__).parent.parent / "feeds" / "feeds.duckdb"
FEEDS_DIR = Path.home() / ".mobilis" / "feeds"


# ---------------------------------------------------------------------------
# show
# ---------------------------------------------------------------------------


def cmd_feeds_show(*, downloaded_only: bool = False, catalog_only: bool = False) -> None:
    """Display downloaded feeds and/or the feed catalog."""
    console = Console()
    show_downloaded = not catalog_only
    show_catalog = not downloaded_only

    if show_downloaded:
        _print_downloaded(console)
        if show_catalog:
            console.print()
    if show_catalog:
        _print_catalog(console)


# ---------------------------------------------------------------------------
# remove
# ---------------------------------------------------------------------------


def cmd_feeds_remove(feed_id: str) -> None:
    """Remove a downloaded feed directory."""
    console = Console()
    feed_path = FEEDS_DIR / feed_id
    if not feed_path.exists():
        console.print(f"[yellow]Feed not found:[/yellow] {feed_id}")
        return
    shutil.rmtree(feed_path)
    console.print(f"[green]Removed[/green] {feed_id}")


# ---------------------------------------------------------------------------
# update
# ---------------------------------------------------------------------------


def _get_hosted_url(feed_id: str) -> str | None:
    if not CATALOG_PATH.exists():
        return None
    import duckdb

    con = duckdb.connect(str(CATALOG_PATH), read_only=True)
    row = con.execute(
        "SELECT latest_dataset.hosted_url FROM feeds WHERE id = ?", [feed_id]
    ).fetchone()
    con.close()
    return row[0] if row else None


def _normalize_feed_files(files_path: Path) -> None:
    """If .txt files are nested in a subdirectory, hoist them up."""
    if list(files_path.glob("*.txt")):
        return
    nested_dirs = [p for p in files_path.iterdir() if p.is_dir()]
    if len(nested_dirs) != 1:
        return
    nested_dir = nested_dirs[0]
    for child in list(nested_dir.iterdir()):
        target = files_path / child.name
        if target.exists():
            shutil.rmtree(target) if target.is_dir() else target.unlink()
        child.rename(target)
    nested_dir.rmdir()


def cmd_feeds_update(feed_id: str) -> None:
    """Re-download and re-import a feed from its catalog URL."""
    console = Console()

    hosted_url = _get_hosted_url(feed_id)
    if not hosted_url:
        console.print(
            f"[red]No catalog entry or hosted URL found for[/red] {feed_id}. "
            "Only feeds from the Mobility Database catalog can be updated."
        )
        return

    feed_path = FEEDS_DIR / feed_id
    files_path = feed_path / "files"
    zip_path = feed_path / f"{feed_id}.zip"
    db_path = feed_path / f"{feed_id}.duckdb"

    feed_path.mkdir(parents=True, exist_ok=True)

    # Clear old files and database
    if files_path.exists():
        shutil.rmtree(files_path)
    files_path.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    # Download
    console.print(f"[cyan]Downloading[/cyan] {feed_id} from {hosted_url} …")
    try:
        with requests.get(hosted_url, stream=True, timeout=180) as response:
            response.raise_for_status()
            with zip_path.open("wb") as fh:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        fh.write(chunk)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(files_path)
    except (requests.RequestException, zipfile.BadZipFile, OSError) as exc:
        console.print(f"[red]Download/extract failed:[/red] {exc}")
        return
    finally:
        if zip_path.exists():
            zip_path.unlink()

    _normalize_feed_files(files_path)

    # Import
    console.print(f"[cyan]Importing[/cyan] {feed_id} into DuckDB …")
    try:
        from .import_gtfs import import_gtfs

        import_gtfs(feed_id)
    except Exception as exc:
        console.print(f"[red]Import failed:[/red] {exc}")
        return

    console.print(f"[green]Done.[/green] Feed [bold]{feed_id}[/bold] updated.")
