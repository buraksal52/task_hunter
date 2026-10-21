from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings
from app.db import models  # noqa: F401
from app.db.base import Base


def make_engine(settings: Settings):
    if settings.database_url.startswith("sqlite:///") and not settings.database_url.endswith(
        ":memory:"
    ):
        database_path = settings.database_url.removeprefix("sqlite:///")
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)
    connect_args = (
        {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
    )
    engine = create_engine(settings.database_url, connect_args=connect_args, future=True)
    if settings.database_url.startswith("sqlite"):

        @event.listens_for(engine, "connect")
        def set_sqlite_pragmas(dbapi_connection, _):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA busy_timeout=5000")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


def create_session_factory(settings: Settings):
    engine = make_engine(settings)
    return engine, sessionmaker(bind=engine, class_=Session, expire_on_commit=False)


def init_db(engine) -> None:
    Base.metadata.create_all(engine)
    with engine.connect() as connection:
        connection.execute(text("PRAGMA foreign_keys=ON"))
        connection.commit()


def get_db(session_factory) -> Generator[Session, None, None]:
    with session_factory() as session:
        yield session
