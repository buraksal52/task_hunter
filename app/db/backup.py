"""Consistent SQLite backup helper using SQLite's online backup API."""

from __future__ import annotations

import sqlite3
from pathlib import Path


def backup_sqlite(source_path: str | Path, destination_path: str | Path) -> None:
    """Copy a live SQLite database consistently, including WAL state."""
    source = Path(source_path)
    destination = Path(destination_path)
    if source.resolve() == destination.resolve():
        raise ValueError("backup destination must differ from source")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with (
        sqlite3.connect(source) as source_connection,
        sqlite3.connect(destination) as destination_connection,
    ):
        source_connection.backup(destination_connection)


def verify_sqlite_backup(backup_path: str | Path) -> bool:
    """Run a read-only integrity check against a backup artifact."""
    with sqlite3.connect(f"file:{Path(backup_path).resolve()}?mode=ro", uri=True) as connection:
        return connection.execute("PRAGMA integrity_check").fetchone() == ("ok",)
