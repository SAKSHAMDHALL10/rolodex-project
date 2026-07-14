import time
from unittest.mock import patch

import httpx
import pytest
from google.genai import errors as genai_errors

from app.core.ai_client import get_gemini_client


def _503_response(request):
    return httpx.Response(
        503,
        json={
            "error": {
                "message": "The model is overloaded. Please try again later.",
                "status": "UNAVAILABLE",
            }
        },
        request=request,
    )


def _200_response(request):
    return httpx.Response(
        200,
        json={
            "candidates": [
                {"content": {"parts": [{"text": "hello"}], "role": "model"}, "finishReason": "STOP"}
            ]
        },
        request=request,
    )


@pytest.fixture
def gemini_client(monkeypatch):
    monkeypatch.setattr("app.core.ai_client.settings.GEMINI_API_KEY", "test-retry-key")
    get_gemini_client.cache_clear()
    client = get_gemini_client()
    yield client
    get_gemini_client.cache_clear()


def test_transient_503_is_retried_and_recovers(gemini_client):
    """
    Regression test for a real production incident: Gemini's well-documented
    transient "model is overloaded" 503 was surfacing immediately as a 502 to
    the frontend on the very first occurrence, because the client had no
    retry policy configured (the SDK's default with retry_options=None is
    exactly one attempt, no retry - verified directly in google.genai.
    _api_client.retry_args()). This confirms the fix actually retries.
    """
    call_count = {"n": 0}

    def flaky_send(self, request, **kwargs):
        call_count["n"] += 1
        return _503_response(request) if call_count["n"] < 3 else _200_response(request)

    with patch.object(httpx.Client, "send", flaky_send):
        response = gemini_client.models.generate_content(
            model="gemini-3.5-flash", contents="test prompt"
        )

    assert call_count["n"] == 3
    assert response.text == "hello"


def test_persistent_503_fails_cleanly_after_exhausting_retries(gemini_client):
    """A genuinely down Gemini must still fail (as a catchable APIError), not hang forever."""
    call_count = {"n": 0}

    def always_503(self, request, **kwargs):
        call_count["n"] += 1
        return _503_response(request)

    with patch.object(httpx.Client, "send", always_503):
        start = time.time()
        with pytest.raises(genai_errors.APIError) as exc_info:
            gemini_client.models.generate_content(model="gemini-3.5-flash", contents="test")
        elapsed = time.time() - start

    assert call_count["n"] == 5  # SDK default: 5 attempts including the initial call
    assert exc_info.value.code == 503
    assert elapsed < 30  # bounded - must not hang indefinitely
