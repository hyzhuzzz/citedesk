"""All function tools live here.

Additional business tools (order lookup, stock lookup, mail sending, ...) can
be added in this file only; the rest of the framework needs no changes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agents import RunContextWrapper, function_tool

import i18n
from kb.retriever import retrieve


@dataclass
class AgentContext:
    """Per-turn mutable state filled by tool calls, never parsed from text."""

    retriever: Any = None
    called_kb: bool = False
    sources: list[dict] = field(default_factory=list)
    no_source: bool = False


@function_tool(description_override=i18n.t("tool_search_kb"))
def search_kb(ctx: RunContextWrapper[AgentContext], query: str) -> str:
    """Retrieve raw knowledge-base snippets for ``query``.

    The description exposed to the model comes from the language pack via
    ``description_override``; this docstring is for developers only.
    """
    context = ctx.context
    context.called_kb = True

    results = retrieve(context.retriever, query)
    if not results:
        context.no_source = True
        return i18n.t("no_relevant")

    context.sources = [
        {"file_name": item["file_name"], "page": item["page"]}
        for item in results
    ]

    blocks: list[str] = []
    for index, item in enumerate(results, start=1):
        location = item["file_name"]
        if item["page"]:
            location = f"{location} (p.{item['page']})"
        blocks.append(f"[{index}] {location}\n{item['text']}")
    return "\n\n".join(blocks)


# --- Extension skeletons (intentionally left as no-ops) --------------------
#
# @function_tool
# def lookup_order(ctx: RunContextWrapper[AgentContext], order_id: str) -> str:
#     """Look up an order by id."""
#     ...
#
# @function_tool
# def lookup_inventory(ctx: RunContextWrapper[AgentContext], sku: str) -> str:
#     """Check stock for a SKU."""
#     ...
