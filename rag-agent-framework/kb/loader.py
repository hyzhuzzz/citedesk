"""Document loading and file management.

Only text-based PDF, DOCX, TXT and MD files are handled.  Scanned documents
requiring OCR are deliberately out of scope.
"""

from __future__ import annotations

from pathlib import Path

from llama_index.core import SimpleDirectoryReader

import config


def list_documents(docs_dir: str | Path | None = None) -> list[dict]:
    """Return name/size records for every supported document on disk."""
    directory = Path(docs_dir or config.DOCS_DIR)
    directory.mkdir(parents=True, exist_ok=True)
    files = [
        path
        for path in sorted(directory.iterdir())
        if path.is_file() and path.suffix.lower() in config.SUPPORTED_EXTENSIONS
    ]
    return [{"name": path.name, "size": path.stat().st_size} for path in files]


def delete_document(name: str, docs_dir: str | Path | None = None) -> bool:
    """Remove one document by file name. Returns True when a file was removed."""
    directory = Path(docs_dir or config.DOCS_DIR)
    target = (directory / Path(name).name).resolve()
    if target.parent != directory.resolve() or not target.is_file():
        return False
    target.unlink()
    return True


def load_documents(docs_dir: str | Path | None = None):
    """Load documents as LlamaIndex ``Document`` objects."""
    directory = Path(docs_dir or config.DOCS_DIR)
    directory.mkdir(parents=True, exist_ok=True)
    reader = SimpleDirectoryReader(
        input_dir=str(directory),
        required_exts=config.SUPPORTED_EXTENSIONS,
        recursive=False,
        exclude_hidden=True,
    )
    return reader.load_data()


def save_uploaded_file(name: str, content: bytes, docs_dir: str | Path | None = None) -> Path:
    """Persist an uploaded file into the document directory."""
    directory = Path(docs_dir or config.DOCS_DIR)
    directory.mkdir(parents=True, exist_ok=True)
    safe_name = Path(name).name
    if Path(safe_name).suffix.lower() not in config.SUPPORTED_EXTENSIONS:
        raise ValueError(safe_name)
    target = directory / safe_name
    target.write_bytes(content)
    return target
