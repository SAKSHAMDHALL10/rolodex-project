"""
Core ORM models.

Contact is the single "rolodex entry" table. It is deliberately denormalized
(JSON columns for lists) because the access pattern is "read whole entry,
render whole entry" and "filter/search across many entries" rather than
relational joins across skills/companies tables. This keeps the extraction
pipeline simple: one JSON object in, one row out.
"""
import uuid
from datetime import datetime, timezone

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import settings
from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # --- Identity ---
    full_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    headline: Mapped[str | None] = mapped_column(String(500), nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(
        String(500), nullable=True, unique=False, index=True
    )
    photo_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    current_company: Mapped[str | None] = mapped_column(String(255), index=True)
    current_title: Mapped[str | None] = mapped_column(String(255), index=True)
    location: Mapped[str | None] = mapped_column(String(255))
    industry: Mapped[str | None] = mapped_column(String(255), index=True)
    summary: Mapped[str | None] = mapped_column(Text)

    # --- Structured history (list[dict]) ---
    experience: Mapped[list | None] = mapped_column(JSONB, default=list)
    education: Mapped[list | None] = mapped_column(JSONB, default=list)

    # --- Capability extraction (list[str]) ---
    skills: Mapped[list | None] = mapped_column(JSONB, default=list)
    technologies: Mapped[list | None] = mapped_column(JSONB, default=list)
    domains: Mapped[list | None] = mapped_column(JSONB, default=list)
    capabilities: Mapped[list | None] = mapped_column(JSONB, default=list)
    interests: Mapped[list | None] = mapped_column(JSONB, default=list)

    # --- Relevance extraction: the whole point of the project ---
    relevance_summary: Mapped[str | None] = mapped_column(Text)
    relevance_tags: Mapped[list | None] = mapped_column(JSONB, default=list)

    # --- Relationship / networking context ---
    connection_notes: Mapped[list | None] = mapped_column(JSONB, default=list)

    # --- Raw + provenance ---
    raw_source_text: Mapped[str | None] = mapped_column(Text)
    source_type: Mapped[str | None] = mapped_column(String(50))  # url | text | export

    # --- Vector search ---
    embedding: Mapped[list | None] = mapped_column(
        Vector(settings.OPENAI_EMBEDDING_DIMENSIONS), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Contact {self.full_name!r} ({self.current_title})>"


class SearchLog(Base):
    """Stores recent natural-language searches for the dashboard widget."""

    __tablename__ = "search_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    query: Mapped[str] = mapped_column(String(500), nullable=False)
    result_count: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
