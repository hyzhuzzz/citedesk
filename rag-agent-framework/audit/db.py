"""SQLAlchemy 2.0 schema and session management.

SQLite gets WAL and a busy timeout automatically.  Changing ``DATABASE_URL``
to a PostgreSQL DSN is the only step needed to migrate the audit store; no
SQLite-specific SQL is used anywhere in the project.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from sqlalchemy import DateTime, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

import config


class Base(DeclarativeBase):
    pass


class QALog(Base):
    __tablename__ = "qa_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, index=True)
    question: Mapped[str] = mapped_column()
    called_kb: Mapped[bool] = mapped_column(default=False)
    sources_json: Mapped[str] = mapped_column(default="[]")
    model: Mapped[str] = mapped_column(default="")
    prompt_tokens: Mapped[int] = mapped_column(default=0)
    completion_tokens: Mapped[int] = mapped_column(default=0)
    total_tokens: Mapped[int] = mapped_column(default=0)
    latency_ms: Mapped[int] = mapped_column(default=0)
    is_unknown: Mapped[bool] = mapped_column(default=False, index=True)


def _make_engine():
    url = config.DATABASE_URL
    if url.startswith("sqlite"):
        raw = url.split(":///", 1)[-1]
        path = Path(raw.replace("\\", "/"))
        if not path.is_absolute():
            path = config.BASE_DIR / path
        path.parent.mkdir(parents=True, exist_ok=True)
        engine = create_engine(
            f"sqlite:///{path.as_posix()}",
            connect_args={"check_same_thread": False, "timeout": 30},
        )

        @event.listens_for(engine, "connect")
        def _sqlite_pragmas(dbapi_connection, _connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA busy_timeout=30000")
            cursor.close()

        return engine
    return create_engine(url, pool_pre_ping=True)


engine = _make_engine()
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def init_db() -> None:
    Base.metadata.create_all(engine)
