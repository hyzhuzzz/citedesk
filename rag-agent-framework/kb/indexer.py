"""Chunking, embedding and Chroma index maintenance.

The LlamaIndex layer is intentionally LLM-free: ``Settings.llm`` is set to
``None`` so no hidden summarisation can happen.  Every conversational token is
spent by the OpenAI Agents SDK instead.
"""

from __future__ import annotations

from pathlib import Path

import chromadb
from llama_index.core import Settings, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai_like import OpenAILikeEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

import config
import i18n
from kb.loader import load_documents

# No LLM at the LlamaIndex layer: retrieval returns raw nodes only.
Settings.llm = None


def get_embed_model() -> OpenAILikeEmbedding:
    """Build the OpenAI-protocol embedding client from configuration."""
    if not config.EMBEDDING_MODEL:
        raise ValueError(i18n.t("err_no_embedding_model"))
    return OpenAILikeEmbedding(
        model_name=config.EMBEDDING_MODEL,
        api_key=config.EMBEDDING_API_KEY,
        api_base=config.EMBEDDING_BASE_URL,
    )


def _get_client(chroma_path: str | Path | None = None) -> chromadb.PersistentClient:
    return chromadb.PersistentClient(path=str(chroma_path or config.CHROMA_DIR))


def _normalise_metadata(nodes) -> None:
    """Attach uniform ``file_name``/``page`` fields used by citations."""
    for node in nodes:
        metadata = dict(node.metadata or {})
        file_name = metadata.get("file_name") or metadata.get("file_path") or "unknown"
        page = metadata.get("page_label") or metadata.get("page_number") or ""
        metadata["file_name"] = str(file_name)
        metadata["page"] = str(page)
        node.metadata = metadata


def build_index(
    docs_dir: str | Path | None = None,
    chroma_path: str | Path | None = None,
    collection_name: str | None = None,
):
    """Read all documents, chunk, embed and replace the Chroma collection.

    Old data is cleared through the Chroma API (``delete_collection``) instead
    of deleting directories, which avoids Windows SQLite file-lock errors.
    """
    documents = load_documents(docs_dir)
    if not documents:
        raise ValueError(i18n.t("err_no_docs"))

    name = collection_name or config.COLLECTION_NAME
    client = _get_client(chroma_path)
    try:
        client.delete_collection(name)
    except Exception:
        # Collection did not exist yet - nothing to clear.
        pass
    collection = client.get_or_create_collection(name)

    splitter = SentenceSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
    )
    nodes = splitter.get_nodes_from_documents(documents)
    _normalise_metadata(nodes)

    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex(
        nodes,
        storage_context=storage_context,
        embed_model=get_embed_model(),
        show_progress=False,
    )
    return index


def load_index(
    chroma_path: str | Path | None = None,
    collection_name: str | None = None,
):
    """Re-open an existing Chroma collection without re-embedding documents."""
    name = collection_name or config.COLLECTION_NAME
    client = _get_client(chroma_path)
    collection = client.get_or_create_collection(name)
    vector_store = ChromaVectorStore(chroma_collection=collection)
    return VectorStoreIndex.from_vector_store(
        vector_store,
        embed_model=get_embed_model(),
    )
