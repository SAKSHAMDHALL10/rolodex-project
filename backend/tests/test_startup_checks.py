from unittest.mock import MagicMock, patch

import pytest
from google.genai import errors as genai_errors

from app.core.startup_checks import GeminiModelUnavailableError, validate_gemini_models


def test_skips_validation_when_no_api_key(monkeypatch, caplog):
    monkeypatch.setattr("app.core.startup_checks.settings.GEMINI_API_KEY", "")
    with caplog.at_level("WARNING"):
        validate_gemini_models()  # must not raise
    assert "skipping startup model validation" in caplog.text


def test_raises_clear_error_when_model_is_deprecated(monkeypatch):
    monkeypatch.setattr("app.core.startup_checks.settings.GEMINI_API_KEY", "test-key")
    monkeypatch.setattr("app.core.startup_checks.settings.GEMINI_TEXT_MODEL", "gemini-2.5-flash")

    api_error = genai_errors.APIError(
        404, {"error": {"message": "This model is no longer available.", "status": "NOT_FOUND"}}
    )
    mock_client = MagicMock()
    mock_client.models.get.side_effect = api_error

    with patch("app.core.startup_checks.genai.Client", return_value=mock_client):
        with pytest.raises(GeminiModelUnavailableError, match="GEMINI_TEXT_MODEL"):
            validate_gemini_models()


def test_does_not_block_startup_on_transient_network_error(monkeypatch, caplog):
    monkeypatch.setattr("app.core.startup_checks.settings.GEMINI_API_KEY", "test-key")

    mock_client = MagicMock()
    mock_client.models.get.side_effect = ConnectionError("network unreachable")

    with patch("app.core.startup_checks.genai.Client", return_value=mock_client):
        with caplog.at_level("WARNING"):
            validate_gemini_models()  # must not raise
    assert "transient network issue" in caplog.text


def test_passes_when_both_models_are_available(monkeypatch, caplog):
    monkeypatch.setattr("app.core.startup_checks.settings.GEMINI_API_KEY", "test-key")

    mock_client = MagicMock()
    mock_client.models.get.return_value = MagicMock()

    with patch("app.core.startup_checks.genai.Client", return_value=mock_client):
        with caplog.at_level("INFO"):
            validate_gemini_models()  # must not raise
    assert mock_client.models.get.call_count == 2
    assert "Verified GEMINI_TEXT_MODEL" in caplog.text
    assert "Verified GEMINI_EMBEDDING_MODEL" in caplog.text
