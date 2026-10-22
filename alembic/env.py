import os
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool

from alembic import context
from app.db import models  # noqa: F401
from app.db.base import Base

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)
target_metadata = Base.metadata


def _ensure_sqlite_parent(database_url: str) -> None:
    """Create the SQLite parent directory before Alembic opens the database."""
    if not database_url.startswith("sqlite:///") or database_url.endswith(":memory:"):
        return
    database_path = database_url.removeprefix("sqlite:///")
    Path(database_path).parent.mkdir(parents=True, exist_ok=True)


def run_migrations_offline():
    database_url = os.getenv("DATABASE_URL", config.get_main_option("sqlalchemy.url"))
    _ensure_sqlite_parent(database_url)
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    section = config.get_section(config.config_ini_section, {})
    database_url = os.getenv("DATABASE_URL", section["sqlalchemy.url"])
    _ensure_sqlite_parent(database_url)
    section["sqlalchemy.url"] = database_url
    connectable = engine_from_config(section, prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
