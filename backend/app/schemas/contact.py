"""
Pydantic schemas (API contracts + the structured-output contract with OpenAI).
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Shared sub-objects
# ---------------------------------------------------------------------------
class ExperienceItem(BaseModel):
    title: str
    company: str
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None


class EducationItem(BaseModel):
    school: str
    degree: str | None = None
    field_of_study: str | None = None
    start_year: str | None = None
    end_year: str | None = None


class ConnectionNote(BaseModel):
    note_type: Literal[
        "met_at_hackathon",
        "worked_together",
        "referral",
        "investor",
        "mentor",
        "mutual_connection",
        "future_collaboration",
        "other",
    ] = "other"
    text: str
    created_at: datetime = Field(default_factory=lambda: datetime.utcnow())


# ---------------------------------------------------------------------------
# Ingestion
# ---------------------------------------------------------------------------
class IngestRequest(BaseModel):
    """Input for turning a LinkedIn profile into a rolodex entry."""

    source_type: Literal["url", "text", "export"] = "text"
    linkedin_url: str | None = None
    raw_text: str | None = Field(
        default=None,
        description="Pasted LinkedIn profile text, or JSON export contents.",
    )
    initial_note: ConnectionNote | None = None

    def clean_or_raise(self) -> str:
        if self.source_type == "url":
            if not self.linkedin_url:
                raise ValueError("linkedin_url is required when source_type='url'")
            return self.linkedin_url
        if not self.raw_text or not self.raw_text.strip():
            raise ValueError("raw_text is required when source_type is 'text' or 'export'")
        return self.raw_text


# ---------------------------------------------------------------------------
# What the LLM must return (OpenAI structured JSON output contract)
# ---------------------------------------------------------------------------
class ExtractionResult(BaseModel):
    full_name: str
    headline: str | None = None
    current_title: str | None = None
    current_company: str | None = None
    industry: str | None = None
    location: str | None = None
    summary: str
    experience: list[ExperienceItem] = Field(default_factory=list)
    education: list[EducationItem] = Field(default_factory=list)

    skills: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    domains: list[str] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)

    relevance_summary: str = Field(
        description="2-4 sentences: why this person matters, when someone would "
        "need them, who should reach out and for what."
    )
    relevance_tags: list[str] = Field(
        default_factory=list,
        description="Short searchable tags, e.g. 'FinTech specialist', "
        "'Hiring manager', 'Distributed systems'.",
    )


# ---------------------------------------------------------------------------
# Contact CRUD
# ---------------------------------------------------------------------------
class ContactBase(BaseModel):
    full_name: str
    headline: str | None = None
    linkedin_url: str | None = None
    photo_url: str | None = None
    current_company: str | None = None
    current_title: str | None = None
    location: str | None = None
    industry: str | None = None
    summary: str | None = None
    experience: list[ExperienceItem] = Field(default_factory=list)
    education: list[EducationItem] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    domains: list[str] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    relevance_summary: str | None = None
    relevance_tags: list[str] = Field(default_factory=list)
    connection_notes: list[ConnectionNote] = Field(default_factory=list)


class ContactRead(ContactBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    source_type: str | None = None
    created_at: datetime
    updated_at: datetime


class ContactListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    headline: str | None = None
    current_company: str | None = None
    current_title: str | None = None
    location: str | None = None
    relevance_tags: list[str] = Field(default_factory=list)
    created_at: datetime


class ContactUpdate(BaseModel):
    connection_notes: list[ConnectionNote] | None = None
    relevance_summary: str | None = None
    relevance_tags: list[str] | None = None
    current_company: str | None = None
    current_title: str | None = None


class DuplicateCandidate(BaseModel):
    contact: ContactListItem
    match_reasons: list[str]
    similarity_score: float


class IngestResponse(BaseModel):
    status: Literal["created", "possible_duplicate"]
    contact: ContactRead | None = None
    duplicates: list[DuplicateCandidate] = Field(default_factory=list)


class MergeRequest(BaseModel):
    keep_id: uuid.UUID
    duplicate_id: uuid.UUID


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------
class SearchFilters(BaseModel):
    role: str | None = None
    company: str | None = None
    industry: str | None = None
    skills: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    location: str | None = None


class SearchRequest(BaseModel):
    query: str | None = None
    filters: SearchFilters = Field(default_factory=SearchFilters)
    semantic: bool = True
    limit: int = Field(default=20, ge=1, le=100)


class SearchResultItem(BaseModel):
    contact: ContactListItem
    score: float | None = None
    matched_on: list[str] = Field(default_factory=list)


class SearchResponse(BaseModel):
    query: str | None = None
    interpreted_filters: SearchFilters
    results: list[SearchResultItem]
    total: int


class NaturalLanguageQuery(BaseModel):
    query: str


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
class TopCount(BaseModel):
    name: str
    count: int


class DashboardStats(BaseModel):
    total_contacts: int
    recent_contacts: list[ContactListItem]
    top_skills: list[TopCount]
    top_industries: list[TopCount]
    top_tags: list[TopCount]
    recent_searches: list[str]
