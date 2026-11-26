"""Write and read per-question audit records.

Only the question, source file names/pages and usage metrics are persisted.
API keys and document bodies are never logged.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from sqlalchemy import select

from audit.db import QALog, SessionLocal, init_db


def write_log(
    question: str,
    called_kb: bool,
    sources: list[dict],
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    total_tokens: int,
    latency_ms: int,
    is_unknown: bool,
    created_at: datetime | None = None,
) -> int:
    init_db()
    record = QALog(
        created_at=created_at or datetime.now(),
        question=question,
        called_kb=bool(called_kb),
        sources_json=json.dumps(sources or [], ensure_ascii=False),
        model=model or "",
        prompt_tokens=int(prompt_tokens),
        completion_tokens=int(completion_tokens),
        total_tokens=int(total_tokens),
        latency_ms=int(latency_ms),
        is_unknown=bool(is_unknown),
    )
    with SessionLocal() as session:
        session.add(record)
        session.commit()
        return int(record.id)


def query_logs(
    start: datetime | None = None,
    end: datetime | None = None,
    keyword: str | None = None,
) -> list[QALog]:
    """Return logs in descending time order, optionally filtered."""
    init_db()
    statement = select(QALog)
    if start is not None:
        statement = statement.where(QALog.created_at >= start)
    if end is not None:
        statement = statement.where(QALog.created_at <= end)
    if keyword:
        statement = statement.where(QALog.question.contains(keyword))
    statement = statement.order_by(QALog.created_at.desc())
    with SessionLocal() as session:
        return list(session.scalars(statement).all())


def to_dict(record: QALog) -> dict[str, Any]:
    """Convert a row into a plain dictionary for Pandas/Streamlit."""
    return {
        "created_at": record.created_at,
        "question": record.question,
        "called_kb": bool(record.called_kb),
        "sources": ", ".join(
            f"{item.get('file_name', '')} p.{item.get('page', '')}".strip()
            if item.get("page")
            else str(item.get("file_name", ""))
            for item in json.loads(record.sources_json or "[]")
        ),
        "model": record.model,
        "prompt_tokens": record.prompt_tokens,
        "completion_tokens": record.completion_tokens,
        "total_tokens": record.total_tokens,
        "latency_ms": record.latency_ms,
        "is_unknown": bool(record.is_unknown),
    }
