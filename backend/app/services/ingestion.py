"""
Orchestrates the full ingestion pipeline:

  raw LinkedIn text/URL
    -> clean_profile_text
    -> extract_profile (Gemini structured output)
    -> build_embedding_text + embed_text
    -> find_duplicates
    -> persist Contact row (or return duplicate candidates for the caller to decide)
"""
import logging

from sqlalchemy.orm import Session

from app.models.contact import Contact
from app.schemas.contact import (
    ContactListItem,
    ContactRead,
    DuplicateCandidate,
    ExtractionResult,
    IngestRequest,
    IngestResponse,
)
from app.services.cleaning import clean_profile_text
from app.services.dedup import find_duplicates
from app.services.embeddings import build_embedding_text, embed_text
from app.services.extraction import extract_profile

logger = logging.getLogger(__name__)


def _fetch_url_placeholder(url: str) -> str:
    """
    Fetching and scraping a live LinkedIn URL requires an authenticated
    session (LinkedIn blocks anonymous scraping), which is out of scope for
    this pipeline. Callers that only have a URL should instead paste the
    profile text/export; we surface a clear error rather than silently
    returning nothing.
    """
    raise ValueError(
        "Fetching LinkedIn profiles directly by URL is not supported "
        "(LinkedIn requires an authenticated session to view full profile data). "
        "Please paste the profile text or an exported profile instead, and keep "
        "the URL in `linkedin_url` for reference."
    )


def ingest_profile(db: Session, request: IngestRequest, force_create: bool = False) -> IngestResponse:
    if request.source_type == "url":
        source_text = _fetch_url_placeholder(request.linkedin_url or "")
    else:
        source_text = request.clean_or_raise()

    cleaned = clean_profile_text(source_text)
    extraction: ExtractionResult = extract_profile(cleaned)

    embedding_text = build_embedding_text(extraction)
    embedding = embed_text(embedding_text)

    if not force_create:
        duplicates = find_duplicates(
            db,
            full_name=extraction.full_name,
            linkedin_url=request.linkedin_url,
            current_company=extraction.current_company,
            embedding=embedding,
        )
        if duplicates:
            logger.info(
                "Ingestion of %s matched %d possible duplicate(s); not auto-creating",
                extraction.full_name,
                len(duplicates),
            )
            return IngestResponse(
                status="possible_duplicate",
                duplicates=[
                    DuplicateCandidate(
                        contact=ContactListItem.model_validate(m.contact),
                        match_reasons=m.reasons,
                        similarity_score=round(m.similarity_score, 3),
                    )
                    for m in duplicates
                ],
            )

    contact = Contact(
        full_name=extraction.full_name,
        headline=extraction.headline,
        linkedin_url=request.linkedin_url,
        current_company=extraction.current_company,
        current_title=extraction.current_title,
        location=extraction.location,
        industry=extraction.industry,
        summary=extraction.summary,
        experience=[e.model_dump() for e in extraction.experience],
        education=[e.model_dump() for e in extraction.education],
        skills=extraction.skills,
        technologies=extraction.technologies,
        domains=extraction.domains,
        capabilities=extraction.capabilities,
        interests=extraction.interests,
        relevance_summary=extraction.relevance_summary,
        relevance_tags=extraction.relevance_tags,
        connection_notes=[request.initial_note.model_dump(mode="json")] if request.initial_note else [],
        raw_source_text=cleaned,
        source_type=request.source_type,
        embedding=embedding,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    logger.info("Created contact %s (%s)", contact.full_name, contact.id)

    return IngestResponse(status="created", contact=ContactRead.model_validate(contact))
