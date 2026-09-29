"""FAQ knowledge retrieval tool backed by Pinecone."""

from __future__ import annotations

from typing import Optional

from langchain_core.tools import tool

from rag.store import similarity_search


@tool
def search_knowledge(
    query: str,
    warehouse: Optional[str] = None,
    doc_type: Optional[str] = None,
) -> list[dict]:
    """Search Savostore FAQ knowledge (warehouse addresses, prohibited items).

    Args:
        query: Natural-language question or keywords.
        warehouse: Optional filter — \"california\" or \"oregon\".
        doc_type: Optional filter — \"warehouse_address\" or \"prohibited_items\".
    """
    warehouse_norm = warehouse.strip().lower() if warehouse else None
    doc_type_norm = doc_type.strip().lower() if doc_type else None
    if warehouse_norm in ("ca", "cal"):
        warehouse_norm = "california"
    if warehouse_norm in ("or", "ore"):
        warehouse_norm = "oregon"
    return similarity_search(
        query,
        warehouse=warehouse_norm,
        doc_type=doc_type_norm,
    )
