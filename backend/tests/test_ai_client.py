import pytest
from google import genai

from app.core.ai_client import GeminiKeyMissingError, get_gemini_client


def test_raises_clean_error_when_key_missing(monkeypatch):
    monkeypatch.setattr("app.core.ai_client.settings.GEMINI_API_KEY", "")
    get_gemini_client.cache_clear()
    with pytest.raises(GeminiKeyMissingError, match="Gemini API key is not configured."):
        get_gemini_client()


def test_returns_client_when_key_present(monkeypatch):
    monkeypatch.setattr("app.core.ai_client.settings.GEMINI_API_KEY", "test-gemini-key")
    get_gemini_client.cache_clear()
    client = get_gemini_client()
    assert isinstance(client, genai.Client)
    get_gemini_client.cache_clear()
