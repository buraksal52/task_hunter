import sqlite3

from app.db.backup import backup_sqlite, verify_sqlite_backup


def test_sqlite_backup_can_be_restored_and_verified(tmp_path):
    source = tmp_path / "hunter.db"
    backup = tmp_path / "backup" / "hunter.db"
    with sqlite3.connect(source) as connection:
        connection.execute("CREATE TABLE jobs (id INTEGER PRIMARY KEY, title TEXT NOT NULL)")
        connection.execute("INSERT INTO jobs(title) VALUES ('backup test')")
        connection.commit()

    backup_sqlite(source, backup)

    assert verify_sqlite_backup(backup)
    with sqlite3.connect(backup) as connection:
        assert connection.execute("SELECT title FROM jobs").fetchone() == ("backup test",)


def test_sqlite_backup_rejects_same_path(tmp_path):
    database = tmp_path / "hunter.db"
    database.touch()
    try:
        backup_sqlite(database, database)
    except ValueError as error:
        assert "destination" in str(error)
    else:
        raise AssertionError("same-path backup should fail")
