"""Pinecone + Hugging Face embedding helpers."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

from config import (
    EMBEDDING_DIMENSION,
    EMBEDDING_MODEL,
    HF_TOKEN,
    PINECONE_API_KEY,
    PINECONE_ENVIRONMENT,
    PINECONE_INDEX_NAME,
    PINECONE_NAMESPACE,
    RAG_TOP_K,
)


@lru_cache(maxsize=1)
def get_embeddings() -> HuggingFaceEndpointEmbeddings:
    """Hugging Face Inference API embeddings (no local torch required)."""
    if not HF_TOKEN:
        raise RuntimeError("HF_TOKEN is not set")
    return HuggingFaceEndpointEmbeddings(
        model=EMBEDDING_MODEL,
        huggingfacehub_api_token=HF_TOKEN,
    )


@lru_cache(maxsize=1)
def get_pinecone_client() -> Pinecone:
    if not PINECONE_API_KEY:
        raise RuntimeError("PINECONE_API_KEY is not set")
    return Pinecone(api_key=PINECONE_API_KEY)


def _cloud_region() -> tuple[str, str]:
    """Parse cloud/region from PINECONE_ENVIRONMENT like 'us-east-1-aws'."""
    env = (PINECONE_ENVIRONMENT or "us-east-1-aws").strip().lower()
    if env.endswith("-aws"):
        return "aws", env[: -len("-aws")]
    if env.endswith("-gcp"):
        return "gcp", env[: -len("-gcp")]
    if env.endswith("-azure"):
        return "azure", env[: -len("-azure")]
    return "aws", env


def ensure_index() -> str:
    """Ensure a 384-dim FAQ index exists; return its name."""
    if not PINECONE_INDEX_NAME:
        raise RuntimeError("PINECONE_INDEX_NAME / PINECONE_FAQ_INDEX_NAME is not set")

    pc = get_pinecone_client()
    names = {idx["name"] for idx in pc.list_indexes()}
    if PINECONE_INDEX_NAME not in names:
        cloud, region = _cloud_region()
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=EMBEDDING_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(cloud=cloud, region=region),
        )
    return PINECONE_INDEX_NAME


def get_index():
    ensure_index()
    return get_pinecone_client().Index(PINECONE_INDEX_NAME)


def get_vector_store(namespace: str | None = None) -> PineconeVectorStore:
    ns = namespace if namespace is not None else PINECONE_NAMESPACE
    return PineconeVectorStore(
        index=get_index(),
        embedding=get_embeddings(),
        namespace=ns,
        text_key="text",
    )


def clear_namespace(namespace: str | None = None) -> None:
    """Delete all vectors in the FAQ namespace (idempotent re-ingest)."""
    ns = namespace if namespace is not None else PINECONE_NAMESPACE
    index = get_index()
    try:
        index.delete(delete_all=True, namespace=ns)
    except Exception:
        # Empty namespace or unsupported delete_all — ignore.
        pass


def build_metadata_filter(
    warehouse: str | None = None,
    doc_type: str | None = None,
) -> dict[str, Any] | None:
    conditions: list[dict[str, Any]] = []
    if warehouse:
        conditions.append({"warehouse": {"$eq": warehouse.lower()}})
    if doc_type:
        conditions.append({"doc_type": {"$eq": doc_type}})
    if not conditions:
        return None
    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}


def similarity_search(
    query: str,
    *,
    warehouse: str | None = None,
    doc_type: str | None = None,
    k: int | None = None,
) -> list[dict[str, Any]]:
    store = get_vector_store()
    filt = build_metadata_filter(warehouse=warehouse, doc_type=doc_type)
    top_k = k if k is not None else RAG_TOP_K
    docs = store.similarity_search(query, k=top_k, filter=filt)
    results: list[dict[str, Any]] = []
    for doc in docs:
        results.append(
            {
                "content": doc.page_content,
                "metadata": dict(doc.metadata or {}),
            }
        )
    return results
