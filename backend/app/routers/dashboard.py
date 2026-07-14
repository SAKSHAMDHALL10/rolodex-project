"""
/dashboard endpoint: the numbers and shortcuts shown on the homepage.

Top-skills/industries/tags are computed by unnesting the JSONB array columns,
which is the simplest correct way to aggregate over "list of strings per row"
without a normalized join table.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import Column, func, select, true
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.contact import Contact, SearchLog
from app.schemas.contact import ContactListItem, DashboardStats, TopCount

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _top_from_jsonb_array(db: Session, column: Column, limit: int = 8) -> list[TopCount]:
    """
    Aggregate value counts from a JSONB array column (e.g. skills, technologies,
    relevance_tags) by unnesting it via a LATERAL join in the FROM clause.
    Takes a real Column object (via SQLAlchemy Core's table_valued()) rather
    than a column-name string, so there's no identifier interpolated into raw
    SQL at any point, and the LATERAL join is explicit rather than relying on
    an implicit comma-join (which SQLAlchemy otherwise flags as a suspected
    accidental cartesian product).
    """
    unnested = func.jsonb_array_elements_text(column).table_valued("value").lateral()
    stmt = (
        select(unnested.c.value.label("name"), func.count().label("count"))
        .select_from(Contact.__table__)
        .join(unnested, true())
        .group_by(unnested.c.value)
        .order_by(func.count().desc(), unnested.c.value.asc())
        .limit(limit)
    )
    rows = db.execute(stmt).all()
    return [TopCount(name=row.name, count=row.count) for row in rows]


@router.get("", response_model=DashboardStats)
def get_dashboard(db: Session = Depends(get_db)):
    total_contacts = db.execute(select(func.count(Contact.id))).scalar_one()

    recent_contacts = (
        db.execute(select(Contact).order_by(Contact.created_at.desc()).limit(6))
        .scalars()
        .all()
    )

    recent_search_rows = (
        db.execute(select(SearchLog.query).order_by(SearchLog.created_at.desc()).limit(8))
        .scalars()
        .all()
    )
    # De-dupe while preserving recency order.
    seen: set[str] = set()
    recent_searches: list[str] = []
    for q in recent_search_rows:
        if q not in seen:
            seen.add(q)
            recent_searches.append(q)

    return DashboardStats(
        total_contacts=total_contacts,
        recent_contacts=[ContactListItem.model_validate(c) for c in recent_contacts],
        top_skills=_top_from_jsonb_array(db, Contact.skills),
        top_industries=_top_industries(db),
        top_tags=_top_from_jsonb_array(db, Contact.relevance_tags),
        recent_searches=recent_searches,
    )


def _top_industries(db: Session, limit: int = 8) -> list[TopCount]:
    """industry is a plain string column (not JSONB), so it's grouped directly."""
    stmt = (
        select(Contact.industry.label("name"), func.count().label("count"))
        .where(Contact.industry.isnot(None), Contact.industry != "")
        .group_by(Contact.industry)
        .order_by(func.count().desc(), Contact.industry.asc())
        .limit(limit)
    )
    rows = db.execute(stmt).all()
    return [TopCount(name=row.name, count=row.count) for row in rows]
