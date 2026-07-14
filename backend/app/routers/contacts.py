"""
/contacts endpoints: ingestion, read, update (notes/tags), delete, merge.
"""
import uuid

import openai
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.contact import Contact
from app.schemas.contact import (
    ContactListItem,
    ContactRead,
    ContactUpdate,
    IngestRequest,
    IngestResponse,
    MergeRequest,
)
from app.services.ingestion import ingest_profile

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.post("/ingest", response_model=IngestResponse)
def ingest_contact(payload: IngestRequest, db: Session = Depends(get_db)):
    """
    Accept a LinkedIn profile (pasted text, export, or URL reference) and turn
    it into a rolodex entry. Returns `possible_duplicate` with candidates
    instead of creating a row if a likely match already exists.
    """
    try:
        return ingest_profile(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except openai.OpenAIError as exc:
        raise HTTPException(
            status_code=502, detail=f"AI extraction service error: {exc}"
        ) from exc


@router.post("/ingest/force", response_model=IngestResponse)
def ingest_contact_force(payload: IngestRequest, db: Session = Depends(get_db)):
    """Same as /ingest but bypasses duplicate detection (user confirmed 'create anyway')."""
    try:
        return ingest_profile(db, payload, force_create=True)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except openai.OpenAIError as exc:
        raise HTTPException(
            status_code=502, detail=f"AI extraction service error: {exc}"
        ) from exc


@router.get("", response_model=list[ContactListItem])
def list_contacts(
    db: Session = Depends(get_db),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
):
    rows = (
        db.execute(
            select(Contact).order_by(Contact.created_at.desc()).limit(limit).offset(offset)
        )
        .scalars()
        .all()
    )
    return rows


@router.get("/{contact_id}", response_model=ContactRead)
def get_contact(contact_id: uuid.UUID, db: Session = Depends(get_db)):
    contact = db.get(Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.patch("/{contact_id}", response_model=ContactRead)
def update_contact(contact_id: uuid.UUID, payload: ContactUpdate, db: Session = Depends(get_db)):
    contact = db.get(Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    update_data = payload.model_dump(exclude_unset=True)
    if "connection_notes" in update_data and update_data["connection_notes"] is not None:
        existing = contact.connection_notes or []
        contact.connection_notes = existing + [
            n if isinstance(n, dict) else n.model_dump(mode="json") for n in payload.connection_notes
        ]
        update_data.pop("connection_notes")
    for field, value in update_data.items():
        if value is not None:
            setattr(contact, field, value)

    db.commit()
    db.refresh(contact)
    return contact


@router.delete("/{contact_id}", status_code=204)
def delete_contact(contact_id: uuid.UUID, db: Session = Depends(get_db)):
    contact = db.get(Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    db.delete(contact)
    db.commit()


@router.post("/merge", response_model=ContactRead)
def merge_contacts(payload: MergeRequest, db: Session = Depends(get_db)):
    """
    Merge `duplicate_id` into `keep_id`: union list fields, keep the richer
    scalar fields, append a connection note documenting the merge, then
    delete the duplicate row.
    """
    if payload.keep_id == payload.duplicate_id:
        raise HTTPException(
            status_code=400, detail="keep_id and duplicate_id must refer to different contacts"
        )

    keep = db.get(Contact, payload.keep_id)
    dup = db.get(Contact, payload.duplicate_id)
    if not keep or not dup:
        raise HTTPException(status_code=404, detail="One or both contacts not found")

    def _union(a: list | None, b: list | None) -> list:
        a, b = a or [], b or []
        seen, merged = set(), []
        for item in a + b:
            key = item if isinstance(item, str) else str(item)
            if key not in seen:
                seen.add(key)
                merged.append(item)
        return merged

    keep.skills = _union(keep.skills, dup.skills)
    keep.technologies = _union(keep.technologies, dup.technologies)
    keep.domains = _union(keep.domains, dup.domains)
    keep.capabilities = _union(keep.capabilities, dup.capabilities)
    keep.interests = _union(keep.interests, dup.interests)
    keep.relevance_tags = _union(keep.relevance_tags, dup.relevance_tags)
    keep.experience = _union(keep.experience, dup.experience)
    keep.education = _union(keep.education, dup.education)
    keep.connection_notes = (keep.connection_notes or []) + (dup.connection_notes or [])
    keep.linkedin_url = keep.linkedin_url or dup.linkedin_url
    keep.summary = keep.summary or dup.summary
    keep.relevance_summary = keep.relevance_summary or dup.relevance_summary

    db.delete(dup)
    db.commit()
    db.refresh(keep)
    return keep
