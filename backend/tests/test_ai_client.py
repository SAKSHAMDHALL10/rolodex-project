import pytest

from app.core.ai_client import OpenAIKeyMissingError, get_openai_client


def test_raises_clean_error_when_key_missing(monkeypatch):
    monkeypatch.setattr("app.core.ai_client.settings.OPENAI_API_KEY", "")
    get_openai_client.cache_clear()
    with pytest.raises(OpenAIKeyMissingError):
        get_openai_client()


def test_openai_key_missing_error_is_catchable_as_openai_error():
    import openai

    assert issubclass(OpenAIKeyMissingError, openai.OpenAIError)


def test_returns_client_when_key_present(monkeypatch):
    monkeypatch.setattr("app.core.ai_client.settings.OPENAI_API_KEY", "sk-test-key")
    get_openai_client.cache_clear()
    client = get_openai_client()
    assert client.api_key == "sk-test-key"
    get_openai_client.cache_clear()
