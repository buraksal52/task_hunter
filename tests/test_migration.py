from pathlib import Path

from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

from alembic import command


def test_alembic_upgrade_from_empty_database(tmp_path: Path, monkeypatch):
    db_path = tmp_path / "nested" / "migration.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    config = Config("alembic.ini")
    command.upgrade(config, "head")
    engine = create_engine(f"sqlite:///{db_path}")
    tables = set(inspect(engine).get_table_names())
    assert {
        "sources",
        "jobs",
        "collection_tasks",
        "notification_outbox",
        "telegram_updates",
    } <= tables
    assert "expires_at" in {column["name"] for column in inspect(engine).get_columns("jobs")}
    assert "notified_at" in {column["name"] for column in inspect(engine).get_columns("jobs")}
    assert "duration_ms" in {
        column["name"] for column in inspect(engine).get_columns("collection_runs")
    }
    with engine.connect() as connection:
        source_rows = connection.execute(
            text("SELECT source_key, enabled, policy_status FROM sources ORDER BY source_key")
        ).all()
    assert source_rows == [("himalayas", False, "approved"), ("jobicy", False, "approved")]
    command.upgrade(config, "head")
