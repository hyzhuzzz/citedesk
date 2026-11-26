"""Agent construction, streaming execution and usage accounting.

This module has no Streamlit dependency, so the same functions can be reused
by a FastAPI wrapper later.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any, Callable

from agents import Agent, Runner, set_default_openai_api, set_tracing_disabled
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from openai import AsyncOpenAI

import config
import i18n
from agent.tools import AgentContext, search_kb


def _build_instructions() -> str:
    return (
        i18n.t("agent_instructions")
        .replace("{fallback}", i18n.t("fallback_answer"))
        .replace("{marker}", i18n.t("no_relevant"))
    )


def build_agent() -> Agent:
    """Create an agent bound to the configured OpenAI-protocol endpoint."""
    if not config.LLM_MODEL:
        raise ValueError(i18n.t("err_no_llm_model"))

    # Tracing would call OpenAI's hosted endpoint even for third-party models.
    set_tracing_disabled(True)

    model: Any
    if config.LLM_BASE_URL:
        # Any OpenAI-compatible gateway must use Chat Completions, not Responses.
        set_default_openai_api("chat_completions")
        client = AsyncOpenAI(
            api_key=config.LLM_API_KEY,
            base_url=config.LLM_BASE_URL,
        )
        model = OpenAIChatCompletionsModel(
            model=config.LLM_MODEL,
            openai_client=client,
        )
    else:
        model = config.LLM_MODEL

    return Agent(
        name=i18n.t("agent_name"),
        instructions=_build_instructions(),
        tools=[search_kb],
        model=model,
    )


def _delta_text(event: Any) -> str | None:
    """Extract streamed answer text from an Agents SDK stream event."""
    if getattr(event, "type", None) != "raw_response_event":
        return None
    data = getattr(event, "data", None)
    if data is None:
        return None

    # Chat Completions chunks: data.choices[0].delta.content
    choices = getattr(data, "choices", None)
    if choices:
        delta = getattr(choices[0], "delta", None)
        content = getattr(delta, "content", None) if delta is not None else None
        if isinstance(content, str) and content:
            return content

    # Responses API style deltas, kept for the official-endpoint path.
    delta = getattr(data, "delta", None)
    if isinstance(delta, str) and delta:
        return delta
    text = getattr(delta, "text", None) if delta is not None else None
    if isinstance(text, str) and text:
        return text
    return None


def run_chat_stream(
    question: str,
    history: list[tuple[str, str] | dict] | None = None,
    retriever: Any = None,
    on_delta: Callable[[str], None] | None = None,
) -> dict:
    """Run one turn and return answer, sources and real token usage.

    ``on_delta`` receives each streamed text chunk so a UI can render it live.
    The returned dictionary maps directly onto one audit-log row.
    """
    context = AgentContext(retriever=retriever)
    messages: list[dict] = []
    for item in history or []:
        role, content = (item.get("role"), item.get("content")) if isinstance(item, dict) else item
        if role in ("user", "assistant"):
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": question})

    agent = build_agent()
    started = time.perf_counter()
    result = Runner.run_streamed(
        agent,
        input=messages,
        context=context,
        max_turns=config.MAX_TURNS,
    )

    async def _consume() -> str:
        collected: list[str] = []
        async for event in result.stream_events():
            chunk = _delta_text(event)
            if chunk:
                collected.append(chunk)
                if on_delta is not None:
                    on_delta(chunk)
        return "".join(collected)

    streamed_text = asyncio.run(_consume())
    latency_ms = int((time.perf_counter() - started) * 1000)

    answer = str(result.final_output or streamed_text or "").strip()

    # Enforce the strict-grounding contract even if the model ignores the
    # instruction to echo the fallback sentence verbatim.
    fallback = i18n.t("fallback_answer")
    if config.ENFORCE_FALLBACK_ON_NO_SOURCE and (
        not context.called_kb or context.no_source
    ):
        answer = fallback

    usage = getattr(result, "usage", None)
    if usage is None:
        usage = getattr(getattr(result, "context_wrapper", None), "usage", None)

    return {
        "answer": answer,
        "called_kb": context.called_kb,
        "sources": context.sources,
        "model": config.LLM_MODEL,
        "prompt_tokens": int(getattr(usage, "input_tokens", 0) or 0),
        "completion_tokens": int(getattr(usage, "output_tokens", 0) or 0),
        "total_tokens": int(getattr(usage, "total_tokens", 0) or 0),
        "latency_ms": latency_ms,
        "is_unknown": answer == fallback,
    }
