"""SQLite engine, session factory, and schema bootstrap."""

from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from backend.models.base import Base

# Default file lives at the repo root so a server restart keeps data.
# Tests override HONEYCHAIN_DATABASE_URL with a temporary SQLite file.
_DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "honeychain.db"
DATABASE_URL = os.environ.get(
    "HONEYCHAIN_DATABASE_URL",
    f"sqlite:///{_DEFAULT_DB_PATH}",
)

engine: Engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


@event.listens_for(engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection: object, _connection_record: object) -> None:
    cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def init_db() -> None:
    """Create tables and seed the two demonstration hives if missing."""

    # Imported here so every ORM model is registered on Base.metadata.
    from backend import models as _models  # noqa: F401
    from backend.services.seed_service import seed_reference_data

    Base.metadata.create_all(bind=engine)
    _ensure_user_columns(engine)
    session = SessionLocal()
    try:
        seed_reference_data(session)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _ensure_user_columns(bind: Engine) -> None:
    """Add columns to existing SQLite files that predate the user profile fields."""

    with bind.begin() as conn:
        rows = conn.execute(text("PRAGMA table_info(users)")).fetchall()
        names = {row[1] for row in rows}
        statements = {
            "email": "ALTER TABLE users ADD COLUMN email VARCHAR(120)",
            "phone": "ALTER TABLE users ADD COLUMN phone VARCHAR(40)",
            "active": "ALTER TABLE users ADD COLUMN active BOOLEAN DEFAULT 1",
        }
        for column, sql in statements.items():
            if column not in names:
                conn.execute(text(sql))


def get_db() -> Generator[Session, None, None]:
    """Yield a session.

    HTTPException is often raised after a valid domain write (for example
    an oracle rejection that must remain visible in CloneWatch). Those
    writes are committed. Unexpected errors roll back.
    """

    from fastapi import HTTPException

    session = SessionLocal()
    try:
        yield session
        session.commit()
    except HTTPException:
        session.commit()
        raise
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def reset_engine(database_url: str) -> Engine:
    """Rebuild the global engine. Used only by tests."""

    global DATABASE_URL, engine, SessionLocal
    DATABASE_URL = database_url
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        echo=False,
    )

    @event.listens_for(engine, "connect")
    def _fk(dbapi_connection: object, _connection_record: object) -> None:
        cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    SessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    return engine
