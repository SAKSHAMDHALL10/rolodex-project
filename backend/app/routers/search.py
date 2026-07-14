"""
/search endpoints: structured filter search, semantic search, and the
natural-language endpoint that powers the AI search box.
"""
from fastapi import APIRouter, Depends, HTTPException
from google.genai import errors as genai_errors
from sqlalchemy.orm import Session

from app.core.ai_client import GeminiKeyMissingError
from app.core.database import get_db
from app.models.contact import SearchLog
from app.schemas.contact import NaturalLanguageQuery, SearchRequest, SearchResponse
from app.services.search import run_natural_language_search, run_search

router = APIRouter(prefix="/search", tags=["search"])


def _log_search(db: Session, query: str, result_count: int) -> None:
    if not query:
        return
    db.add(SearchLog(query=query, result_count=result_count))
    db.commit()


@router.post("", response_model=SearchResponse)
def search(payload: SearchRequest, db: Session = Depends(get_db)):
    """Structured + optional semantic search over explicit filters."""
    try:
        filters, results = run_search(db, payload)
    except GeminiKeyMissingError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except genai_errors.APIError as exc:
        raise HTTPException(
            status_code=502, detail=f"AI search service error: {exc.message}"
        ) from exc
    _log_search(db, payload.query or "", len(results))
    return SearchResponse(
        query=payload.query, interpreted_filters=filters, results=results, total=len(results)
    )


@router.post("/natural-language", response_model=SearchResponse)
def natural_language_search(payload: NaturalLanguageQuery, db: Session = Depends(get_db)):
    """
    The AI search box: "Who do we know with startup hiring experience?" ->
    parsed into structured filters + semantic phrase -> executed as a hybrid
    search.
    """
    try:
        filters, results = run_natural_language_search(db, payload.query)
    except GeminiKeyMissingError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except genai_errors.APIError as exc:
        raise HTTPException(
            status_code=502, detail=f"AI search service error: {exc.message}"
        ) from exc
    _log_search(db, payload.query, len(results))
    return SearchResponse(
        query=payload.query, interpreted_filters=filters, results=results, total=len(results)
    )
