"""Lightweight acceptance harness.

Usage::

    python eval.py

Builds a dedicated evaluation index from ``eval_samples/``, runs all test
questions through the real agent (OpenAI Agents SDK, no mocked answers) and
prints hit-rate / fallback-accuracy plus a machine-readable report.
"""

from __future__ import annotations

import json
from pathlib import Path

import config
import i18n
from agent.service_agent import run_chat_stream
from kb.indexer import build_index
from kb.retriever import get_retriever

EVAL_COLLECTION = "rag_agent_eval"


def main() -> int:
    print(i18n.t("eval_header"))
    if not config.LLM_MODEL:
        raise SystemExit(i18n.t("err_no_llm_model"))
    if not config.EMBEDDING_MODEL:
        raise SystemExit(i18n.t("err_no_embedding_model"))

    sample_dir = config.BASE_DIR / "eval_samples"
    chroma_dir = config.DATA_DIR / "eval_chroma"
    chroma_dir.mkdir(parents=True, exist_ok=True)

    build_index(
        docs_dir=sample_dir,
        chroma_path=chroma_dir,
        collection_name=EVAL_COLLECTION,
    )
    retriever = get_retriever(
        chroma_path=chroma_dir,
        collection_name=EVAL_COLLECTION,
    )

    samples = json.loads(
        (sample_dir / "test_questions.json").read_text(encoding="utf-8")
    )
    report: list[dict] = []
    correct = 0

    for sample in samples:
        info = run_chat_stream(sample["question"], retriever=retriever)
        answer = info["answer"]
        if sample["answerable"]:
            passed = (
                not info["is_unknown"]
                and info["called_kb"]
                and any(keyword.lower() in answer.lower() for keyword in sample["keywords"])
            )
        else:
            passed = info["is_unknown"]
        correct += int(passed)
        status = i18n.t("eval_ok") if passed else i18n.t("eval_fail")
        report.append(
            {
                "id": sample["id"],
                "question": sample["question"],
                "answerable": sample["answerable"],
                "passed": passed,
                "answer": answer,
                "is_unknown": info["is_unknown"],
                "sources": info["sources"],
                "total_tokens": info["total_tokens"],
            }
        )
        print(
            f"[{sample['id']:>2}] {status} | unknown={info['is_unknown']} | "
            f"{sample['question']}"
        )

    summary = i18n.t("eval_summary").format(correct=correct, total=len(samples))
    print(summary)

    output: Path = config.DATA_DIR / "eval_report.json"
    output.write_text(
        json.dumps(
            {"summary": summary, "correct": correct, "total": len(samples), "results": report},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Report: {output}")
    return 0 if correct >= 18 else 1


if __name__ == "__main__":
    raise SystemExit(main())
