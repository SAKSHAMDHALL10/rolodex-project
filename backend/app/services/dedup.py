"""
Duplicate detection.

Before inserting a new contact we check, in order of confidence:
  1. Exact LinkedIn URL match -> certain duplicate.
  2. Fuzzy full-name match + same current_company -> very likely duplicate.
  3. Embedding cosine similarity above threshold -> possible duplicate
     (same person described slightly differently, or re-pasted profile).

Anything flagged is returned to the caller as a "possible_duplicate" response
so the user can choose to merge instead of silently creating a second row.
"""
from dataclasses import dataclass

from rapidfuzz import fuzz
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.contact import Contact


@dataclass
class DuplicateMatch:
    contact: Contact
    reasons: list[str]
    similarity_score: float


def find_duplicates(
    db: Session,
    *,
    full_name: str,
    linkedin_url: str | None,
    current_company: str | None,
    embedding: list[float] | None,
) -> list[DuplicateMatch]:
    matches: dict[str, DuplicateMatch] = {}

    # 1. Exact LinkedIn URL match.
    if linkedin_url:
        exact = db.execute(
            select(Contact).where(Contact.linkedin_url == linkedin_url)
        ).scalars().all()
        for contact in exact:
            matches[str(contact.id)] = DuplicateMatch(
                contact=contact, reasons=["Exact LinkedIn URL match"], similarity_score=1.0
            )

    # 2. Fuzzy name match, optionally reinforced by same company.
    #
    # This loads every contact into memory and scores each one in Python
    # (O(n) per ingestion). That's the right tradeoff for a rolodex's actual
    # scale (hundreds to low thousands of contacts) and keeps match quality
    # exact rather than approximate. If this table grows into the tens of
    # thousands, replace this with a SQL-side trigram similarity query
    # (`CREATE EXTENSION pg_trgm`, then `full_name % :name` / `similarity()`,
    # with a GIN trigram index on full_name) rather than adding an arbitrary
    # row LIMIT here, which would silently start missing duplicates outside
    # whatever subset of rows the limit happens to return.
    candidates = db.execute(select(Contact)).scalars().all()
    for contact in candidates:
        if str(contact.id) in matches:
            continue
        name_score = fuzz.token_sort_ratio(full_name.lower(), contact.full_name.lower())
        if name_score >= settings.DUPLICATE_NAME_FUZZ_THRESHOLD:
            reasons = [f"Name similarity {name_score:.0f}%"]
            same_company = (
                current_company
                and contact.current_company
                and current_company.strip().lower() == contact.current_company.strip().lower()
            )
            if same_company:
                reasons.append("Same current company")
            matches[str(contact.id)] = DuplicateMatch(
                contact=contact, reasons=reasons, similarity_score=name_score / 100
            )

    # 3. Embedding similarity (cosine distance via pgvector's <=> operator).
    if embedding is not None:
        rows = db.execute(
            select(
                Contact,
                Contact.embedding.cosine_distance(embedding).label("distance"),
            )
            .where(Contact.embedding.isnot(None))
            .order_by("distance")
            .limit(5)
        ).all()
        for contact, distance in rows:
            similarity = 1 - float(distance)
            if similarity >= settings.DUPLICATE_SIMILARITY_THRESHOLD:
                existing = matches.get(str(contact.id))
                reason = f"Embedding similarity {similarity:.0%}"
                if existing:
                    existing.reasons.append(reason)
                    existing.similarity_score = max(existing.similarity_score, similarity)
                else:
                    matches[str(contact.id)] = DuplicateMatch(
                        contact=contact, reasons=[reason], similarity_score=similarity
                    )

    return sorted(matches.values(), key=lambda m: m.similarity_score, reverse=True)
