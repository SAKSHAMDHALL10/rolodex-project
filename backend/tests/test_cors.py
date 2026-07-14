from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_preflight_succeeds_for_configured_origin():
    """Baseline: a correctly-configured origin must get a clean 200 preflight."""
    r = client.options(
        "/api/v1/dashboard",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert r.status_code == 200
    assert r.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_preflight_rejects_unconfigured_origin_with_informative_400():
    """
    An origin that's genuinely not allowed should still get Starlette's
    informative 400 "Disallowed CORS origin" - this is intentional
    (see starlette.middleware.cors.CORSMiddleware.preflight_response) and
    distinguishes a real misconfiguration from the trailing-slash bug below.
    """
    r = client.options(
        "/api/v1/dashboard",
        headers={
            "Origin": "https://totally-unrelated-site.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert r.status_code == 400
    assert "origin" in r.text.lower()


def test_preflight_succeeds_on_post_contacts_ingest():
    """Spot-check a second real endpoint the frontend actually calls."""
    r = client.options(
        "/api/v1/contacts/ingest",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert r.status_code == 200
