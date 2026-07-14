from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app


def _broken_db_session():
    """
    Dependency override that raises a real SQLAlchemyError (OperationalError)
    by pointing at a guaranteed-unreachable port, simulating a dead database
    more faithfully than a hand-rolled mock.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(
        "postgresql+psycopg://postgres:postgres@localhost:1/nonexistent", pool_pre_ping=False
    )
    session_local = sessionmaker(bind=engine)
    db = session_local()
    try:
        yield db
    finally:
        db.close()


def test_unhandled_db_error_on_business_endpoint_returns_clean_503():
    """
    Regression test: before this fix, any endpoint other than /health/ready
    let a database error propagate as an unhandled 500 with no useful body.
    The frontend needs a distinguishable status code (503) to tell "database
    problem" apart from "Gemini problem" (502) or "genuinely unreachable"
    (no HTTP response at all).
    """
    app.dependency_overrides[get_db] = _broken_db_session
    try:
        client = TestClient(app)
        r = client.get("/api/v1/dashboard")
        assert r.status_code == 503
        assert r.json() == {"detail": "Database error. Check server logs for details."}

        r2 = client.get("/api/v1/contacts")
        assert r2.status_code == 503
        assert r2.json() == {"detail": "Database error. Check server logs for details."}
    finally:
        app.dependency_overrides.pop(get_db, None)
