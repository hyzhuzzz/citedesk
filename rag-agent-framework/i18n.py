"""Tiny language pack loader.

All user-facing text, agent instructions, tool descriptions, fallback answers
and chart titles are resolved through :func:`t` so a single switch in
``config.LANGUAGE`` changes the whole application.
"""

from __future__ import annotations

import importlib
from typing import Any

import config

_CACHE: dict[str, dict[str, Any]] = {}


def _strings(language: str) -> dict[str, Any]:
    if language not in _CACHE:
        module = importlib.import_module(f"locales.{language}")
        _CACHE[language] = module.STRINGS
    return _CACHE[language]


def t(key: str) -> str:
    """Return the string registered under ``key`` for the active language.

    Missing keys return the key itself, which makes omissions obvious during
    development instead of silently producing an empty label.
    """
    language = config.LANGUAGE if config.LANGUAGE in ("zh", "en") else "zh"
    value = _strings(language).get(key, key)
    return value if isinstance(value, str) else str(value)
