"""
Startup-time checks that fail loudly and clearly instead of letting a broken
AI-provider configuration surface later as an obscure runtime exception in
the middle of a real request (which is exactly what happened when
gemini-2.5-flash was deprecated out from under a running deployment).
"""
import logging

from google import genai
from google.genai import errors as genai_errors

from app.core.config import settings

logger = logging.getLogger(__name__)


class GeminiModelUnavailableError(RuntimeError):
    """
    Raised at startup when a configured Gemini model is confirmed invalid,
    renamed, or deprecated by the Gemini API itself. Deliberately allowed to
    propagate out of the FastAPI lifespan startup phase, so the process
    fails to boot with a clear message - the same "fail fast on bad config"
    treatment already given to a malformed DATABASE_URL - rather than
    starting "successfully" and then failing every real request with a
    generic error deep in the AI provider's SDK.
    """


def validate_gemini_models() -> None:
    """
    Verify GEMINI_TEXT_MODEL and GEMINI_EMBEDDING_MODEL actually exist and are
    reachable, by asking the Gemini API directly (client.models.get) rather
    than trusting the configured model strings blindly.

    - If GEMINI_API_KEY isn't set: skipped entirely. This is existing,
      deliberate behavior - the app must still start and serve non-AI
      endpoints without a key; AI endpoints then fail per-request with a
      clear 502 (see app/core/ai_client.py) instead of blocking the whole
      deployment.
    - If the API confirms a model is missing/renamed/deprecated (a genuine,
      unambiguous API-level error): raises GeminiModelUnavailableError.
    - If the check itself can't complete for an unrelated reason (network
      unreachable, timeout, transient 5xx): logged as a warning and startup
      continues, since that's an infrastructure blip, not a configuration
      error, and settings that will very likely become reachable again
      shouldn't permanently block deployment.
    """
    if not settings.GEMINI_API_KEY:
        logger.warning(
            "GEMINI_API_KEY not set - skipping startup model validation. "
            "AI-powered endpoints will return a clear 502 until it's configured."
        )
        return

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    for env_var, model_name in (
        ("GEMINI_TEXT_MODEL", settings.GEMINI_TEXT_MODEL),
        ("GEMINI_EMBEDDING_MODEL", settings.GEMINI_EMBEDDING_MODEL),
    ):
        try:
            client.models.get(model=model_name)
        except genai_errors.APIError as exc:
            raise GeminiModelUnavailableError(
                f"{env_var}={model_name!r} is not available from the Gemini API "
                f"(HTTP {exc.code}: {exc.message}). This usually means the model "
                f"has been deprecated or renamed. Update the {env_var} environment "
                "variable to a currently supported model - see "
                "https://ai.google.dev/gemini-api/docs/models for the current "
                "list - then redeploy. No code changes are needed."
            ) from exc
        except Exception as exc:  # noqa: BLE001 - deliberately broad, see docstring
            logger.warning(
                "Could not verify %s=%r at startup (%s: %s) - continuing without "
                "blocking startup, since this looks like a transient network "
                "issue rather than a configuration error.",
                env_var,
                model_name,
                type(exc).__name__,
                exc,
            )
            return
        else:
            logger.info("Verified %s=%r is available.", env_var, model_name)
