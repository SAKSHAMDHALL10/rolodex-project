"""
Shared Gemini (Google GenAI) client construction.

Both the extraction and embeddings services need a Gemini client; this
centralizes that and gives a single place to fail fast when `GEMINI_API_KEY`
isn't configured, rather than letting every call site make a live network
round-trip just to hit an auth error from Gemini's side.
"""
from functools import lru_cache

from google import genai

from app.core.config import settings


class GeminiKeyMissingError(Exception):
    """
    Raised before any network call when GEMINI_API_KEY isn't configured.
    Caught explicitly (alongside google.genai.errors.APIError) in the routers
    to return a clean 502 with an actionable message instead of an unhandled
    crash or a generic upstream authentication error.
    """


@lru_cache
def get_gemini_client() -> genai.Client:
    if not settings.GEMINI_API_KEY:
        raise GeminiKeyMissingError("Gemini API key is not configured.")
    return genai.Client(api_key=settings.GEMINI_API_KEY)
