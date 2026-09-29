"""RAG ingest API routes."""

from fastapi import APIRouter, HTTPException

from rag.ingest import ingest_rag_data

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/ingest")
def ingest():
    try:
        result = ingest_rag_data()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return result
