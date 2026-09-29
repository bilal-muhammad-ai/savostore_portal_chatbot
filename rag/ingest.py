"""Ingest rag_data PDFs into Pinecone with heading chunks."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from langchain_core.documents import Document

from config import PINECONE_INDEX_NAME, PINECONE_NAMESPACE, RAG_DATA_DIR
from rag.chunking import chunk_rag_dir
from rag.store import clear_namespace, get_vector_store


def ingest_rag_data(rag_dir: Path | None = None) -> dict[str, Any]:
    """Clear FAQ namespace and upsert heading chunks from PDF directory."""
    directory = Path(rag_dir) if rag_dir is not None else Path(RAG_DATA_DIR)
    if not directory.is_dir():
        raise FileNotFoundError(f"RAG data directory not found: {directory}")

    chunks = chunk_rag_dir(directory)
    if not chunks:
        raise ValueError(f"No PDF chunks produced from {directory}")

    clear_namespace(PINECONE_NAMESPACE)
    store = get_vector_store(PINECONE_NAMESPACE)

    documents = [
        Document(page_content=chunk.text, metadata=chunk.metadata) for chunk in chunks
    ]
    ids = [chunk.chunk_id for chunk in chunks]
    store.add_documents(documents, ids=ids)

    source_files = sorted({c.metadata.get("source_file", "") for c in chunks})
    return {
        "documents": len(source_files),
        "chunks": len(chunks),
        "index": PINECONE_INDEX_NAME,
        "namespace": PINECONE_NAMESPACE,
        "sources": source_files,
    }
