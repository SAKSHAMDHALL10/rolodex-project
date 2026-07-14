from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"


def test_docs_available():
    response = client.get("/docs")
    assert response.status_code == 200


def test_readiness_check_reports_database_status():
    """
    /health/ready must never crash - it should cleanly report either a
    healthy or unreachable database, with the right status code and shape
    either way. Written to not assume whether a real Postgres is reachable
    in the environment running this test.
    """
    response = client.get("/health/ready")
    assert response.status_code in (200, 503)
    body = response.json()
    if response.status_code == 200:
        assert body == {"status": "ok", "database": "connected"}
    else:
        assert body["status"] == "unavailable"
        assert body["database"] == "unreachable"
        assert "detail" in body


def test_liveness_check_does_not_depend_on_database():
    """/health must stay 200 regardless of database state - it's a pure liveness probe."""
    response = client.get("/health")
    assert response.status_code == 200
