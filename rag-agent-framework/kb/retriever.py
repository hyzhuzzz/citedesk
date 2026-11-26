"""Raw-node retrieval only.

``index.as_retriever()`` is used deliberately: ``query_engine`` would trigger a
second, hidden LLM call and distort both latency and token accounting.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import config
from kb.indexer import load_index


def get_retriever(
    chroma_path: str | Path | None = None,
    collection_name: str | None = None,
    top_k: int | None = None,
):
    index = load_index(chroma_path=chroma_path, collection_name=collection_name)
    return index.as_retriever(similarity_top_k=top_k or config.TOP_K)


def retrieve(retriever: Any, query: str, score_threshold: float | None = None) -> list[dict]:
    """Return top-k raw snippets with source metadata, filtered by score."""
    threshold = config.SCORE_THRESHOLD if score_threshold is None else score_threshold
    nodes = retriever.retrieve(query)
    results: list[dict] = []
    for node in nodes:
        score = float(node.score or 0.0)
        if score < threshold:
            continue
        metadata = dict(node.metadata or {})
        results.append(
            {
                "text": node.get_content(),
                "file_name": str(metadata.get("file_name") or "unknown"),
                "page": str(metadata.get("page") or ""),
                "score": score,
            }
        )
    return results
