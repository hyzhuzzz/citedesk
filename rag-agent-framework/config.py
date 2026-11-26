"""Central configuration for the RAG agent framework.

Every model name, endpoint, credential and path is resolved here from the
environment (``.env``) so that no other module needs to know a vendor or a
concrete model identifier.  LLM and Embedding settings are intentionally kept
separate because many third-party LLM gateways do not expose an embedding API.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


# ---------------------------------------------------------------------------
# Global language switch.  Change to "en" and restart the application.
# ---------------------------------------------------------------------------
LANGUAGE = "zh"  # "zh" | "en"

# ---------------------------------------------------------------------------
# LLM (OpenAI Agents SDK).  No model name is hardcoded in this file.
# ---------------------------------------------------------------------------
LLM_API_KEY = _env("LLM_API_KEY")
LLM_BASE_URL = _env("LLM_BASE_URL") or None
LLM_MODEL = _env("LLM_MODEL")

# ---------------------------------------------------------------------------
# Embedding (LlamaIndex OpenAILikeEmbedding).  Falls back to the LLM settings.
# ---------------------------------------------------------------------------
EMBEDDING_API_KEY = _env("EMBEDDING_API_KEY") or LLM_API_KEY
EMBEDDING_BASE_URL = _env("EMBEDDING_BASE_URL") or LLM_BASE_URL
EMBEDDING_MODEL = _env("EMBEDDING_MODEL")

# The Agents SDK reads these variables for its default client.  Setting them
# here keeps the official endpoint path working without touching application code.
if LLM_API_KEY:
    os.environ.setdefault("OPENAI_API_KEY", LLM_API_KEY)
if LLM_BASE_URL:
    os.environ.setdefault("OPENAI_BASE_URL", LLM_BASE_URL)

# ---------------------------------------------------------------------------
# Storage / paths
# ---------------------------------------------------------------------------
DATABASE_URL = _env("DATABASE_URL") or f"sqlite:///{BASE_DIR / 'data' / 'audit.db'}"

DATA_DIR = BASE_DIR / "data"
DOCS_DIR = DATA_DIR / "docs"
CHROMA_DIR = DATA_DIR / "chroma"
COLLECTION_NAME = "rag_agent_kb"

for _directory in (DATA_DIR, DOCS_DIR, CHROMA_DIR):
    _directory.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Retrieval / conversation tuning
# ---------------------------------------------------------------------------
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
TOP_K = 5
SCORE_THRESHOLD = float(_env("SCORE_THRESHOLD", "0.45"))
HISTORY_ROUNDS = 6
MAX_TURNS = 6

# Safety net: when the knowledge base returns nothing, force the exact
# fallback sentence instead of trusting the model to paraphrase it.
ENFORCE_FALLBACK_ON_NO_SOURCE = True

SUPPORTED_EXTENSIONS = [".pdf", ".docx", ".txt", ".md"]
