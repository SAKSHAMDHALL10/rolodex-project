"""
Search service.

Combines:
  - Structured filtering (role/company/industry/skills/technologies/tags), applied
    as SQL predicates over indexed columns and JSONB containment checks.
  - Semantic search over the `embedding` column using pgvector cosine distance.
  - Natural language -> structured filters + semantic phrase, via the
    extraction service's `parse_natural_language_query`.
"""
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.contact import Contact
from app.schemas.contact import SearchFilters, SearchRequest, SearchResultItem
from app.services.embeddings import embed_text
from app.services.extraction import parse_natural_language_query


def _apply_filters(stmt, filters: SearchFilters):
    if filters.role:
        stmt = stmt.where(Contact.current_title.ilike(f"%{filters.role}%"))
    if filters.company:
        stmt = stmt.where(Contact.current_company.ilike(f"%{filters.company}%"))
    if filters.industry:
        stmt = stmt.where(Contact.industry.ilike(f"%{filters.industry}%"))
    if filters.location:
        stmt = stmt.where(Contact.location.ilike(f"%{filters.location}%"))
    for skill in filters.skills:
        stmt = stmt.where(Contact.skills.contains([skill]))
    for tech in filters.technologies:
        stmt = stmt.where(Contact.technologies.contains([tech]))
    for tag in filters.tags:
        stmt = stmt.where(Contact.relevance_tags.contains([tag]))
    return stmt


def keyword_search(db: Session, text_query: str, filters: SearchFilters, limit: int):
    stmt = select(Contact)
    stmt = _apply_filters(stmt, filters)
    if text_query:
        like = f"%{text_query}%"
        stmt = stmt.where(
            or_(
                Contact.full_name.ilike(like),
                Contact.headline.ilike(like),
                Contact.summary.ilike(like),
                Contact.relevance_summary.ilike(like),
                Contact.current_company.ilike(like),
                Contact.current_title.ilike(like),
            )
        )
    stmt = stmt.limit(limit)
    return db.execute(stmt).scalars().all()


def semantic_search(db: Session, text_query: str, filters: SearchFilters, limit: int):
    query_embedding = embed_text(text_query)
    stmt = select(Contact, Contact.embedding.cosine_distance(query_embedding).label("distance"))
    stmt = _apply_filters(stmt, filters)
    stmt = stmt.where(Contact.embedding.isnot(None)).order_by("distance").limit(limit)
    rows = db.execute(stmt).all()
    return [(contact, 1 - float(distance)) for contact, distance in rows]


def run_search(db: Session, request: SearchRequest) -> tuple[SearchFilters, list[SearchResultItem]]:
    filters = request.filters
    semantic_phrase = request.query

    results: list[SearchResultItem] = []

    if request.semantic and semantic_phrase:
        for contact, score in semantic_search(db, semantic_phrase, filters, request.limit):
            results.append(
                SearchResultItem(contact=contact, score=round(score, 4), matched_on=["semantic"])
            )
    else:
        for contact in keyword_search(db, semantic_phrase or "", filters, request.limit):
            results.append(SearchResultItem(contact=contact, score=None, matched_on=["keyword"]))

    return filters, results


def run_natural_language_search(db: Session, query: str, limit: int = 20):
    """Turn free text into filters via the LLM, then execute a hybrid search."""
    parsed = parse_natural_language_query(query)
    filters = SearchFilters(
        role=parsed.get("role"),
        company=parsed.get("company"),
        industry=parsed.get("industry"),
        location=parsed.get("location"),
        skills=parsed.get("skills") or [],
        technologies=parsed.get("technologies") or [],
        tags=parsed.get("tags") or [],
    )
    semantic_phrase = parsed.get("semantic_phrase") or query

    request = SearchRequest(query=semantic_phrase, filters=filters, semantic=True, limit=limit)
    _, results = run_search(db, request)

    # Fall back to keyword search if semantic search found nothing (e.g. no
    # embeddings populated yet in a fresh/local dataset).
    if not results:
        request.semantic = False
        request.query = query
        _, results = run_search(db, request)

    return filters, results
