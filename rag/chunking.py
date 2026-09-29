"""Heading-aware PDF chunking with warehouse/document metadata."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader

# Explicit headings observed in rag_data PDFs (order does not matter for matching).
KNOWN_HEADINGS: tuple[str, ...] = (
    "Minimum Shipping Charges",
    "Verification & Consolidation Available",
    "Verification & Consolidation Not Available",
    "Shipment Protection Available",
    "No Shipment Protection",
    "Returns Not Supported",
    "No in-person Drop-Offs",
    "Use the Exact Name and Address",
    "California Address",
    "Oregon Address",
    "Warehouse Hours",
    "Ship With Us in Two Simple Steps",
    "Important warehouse disclaimer",
    "Prohibited Items",
    "Items We Can Ship With Conditions",
    "Important Notes",
)

_FILE_META: dict[str, dict[str, str]] = {
    "warehouse-address-california.pdf": {
        "doc_type": "warehouse_address",
        "warehouse": "california",
        "title": "California, USA",
    },
    "warehouse-address-oregon.pdf": {
        "doc_type": "warehouse_address",
        "warehouse": "oregon",
        "title": "Oregon, USA",
    },
    "prohibited-items-list.pdf": {
        "doc_type": "prohibited_items",
        "title": "Prohibited Items List",
    },
}


@dataclass
class RagChunk:
    text: str
    metadata: dict[str, str]
    chunk_id: str


def extract_pdf_text(path: Path) -> str:
    reader = PdfReader(str(path))
    parts: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        parts.append(text)
    return "\n".join(parts)


def _normalize_text(text: str) -> str:
    text = text.replace("\x0c", "\n")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _is_heading_line(line: str) -> str | None:
    stripped = line.strip()
    if not stripped:
        return None
    for heading in KNOWN_HEADINGS:
        if stripped == heading:
            return heading
    return None


def _doc_meta_for_file(filename: str) -> dict[str, str]:
    meta = dict(_FILE_META.get(filename, {"doc_type": "unknown", "title": filename}))
    meta["source_file"] = filename
    return meta


def _context_prefix(doc_meta: dict[str, str]) -> str:
    warehouse = doc_meta.get("warehouse")
    if warehouse:
        return f"Warehouse: {warehouse.capitalize()}"
    return f"Doc: {doc_meta.get('title', 'FAQ')}"


def chunk_text_by_headings(text: str, doc_meta: dict[str, str]) -> list[RagChunk]:
    """Split document text on known headings; keep each section as one chunk."""
    normalized = _normalize_text(text)
    lines = normalized.split("\n")

    sections: list[tuple[str, list[str]]] = []
    current_heading = "Introduction"
    current_body: list[str] = []

    for line in lines:
        matched = _is_heading_line(line)
        if matched:
            if current_body or current_heading != "Introduction":
                sections.append((current_heading, current_body))
            current_heading = matched
            current_body = []
            continue
        current_body.append(line)

    sections.append((current_heading, current_body))

    prefix = _context_prefix(doc_meta)
    source_file = doc_meta["source_file"]
    chunks: list[RagChunk] = []

    for index, (heading, body_lines) in enumerate(sections):
        body = "\n".join(body_lines).strip()
        if not body and heading == "Introduction":
            continue
        content_parts = [prefix, f"Heading: {heading}"]
        if body:
            content_parts.append(body)
        chunk_text = "\n\n".join(content_parts)
        metadata = {
            **doc_meta,
            "heading": heading,
            "heading_path": heading,
            "chunk_index": str(index),
        }
        # Pinecone metadata values must be non-null; omit empty warehouse.
        if not metadata.get("warehouse"):
            metadata.pop("warehouse", None)
        chunk_id = f"{source_file}::{index}"
        chunks.append(RagChunk(text=chunk_text, metadata=metadata, chunk_id=chunk_id))

    return chunks


def chunk_pdf(path: Path) -> list[RagChunk]:
    doc_meta = _doc_meta_for_file(path.name)
    text = extract_pdf_text(path)
    return chunk_text_by_headings(text, doc_meta)


def chunk_rag_dir(rag_dir: Path) -> list[RagChunk]:
    chunks: list[RagChunk] = []
    for path in sorted(rag_dir.glob("*.pdf")):
        chunks.extend(chunk_pdf(path))
    return chunks
