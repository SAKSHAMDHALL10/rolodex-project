"""
Shared Gemini (Google GenAI) client construction.

Both the extraction and embeddings services need a Gemini client; this
centralizes that and gives a single place to fail fast when `GEMINI_API_KEY`
isn't configured, rather than letting every call site make a live network
round-trip just to hit an auth error from Gemini's side.
"""
from functools import lru_cache

from google import genai
from google.genai import types

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
    return genai.Client(
        api_key=settings.GEMINI_API_KEY,
        # IMPORTANT: the SDK does NOT retry by default. Verified directly in
        # google.genai._api_client.retry_args(): when retry_options is None
        # (i.e. unconfigured, as it was before this fix), it returns
        # `{'stop': tenacity.stop_after_attempt(1), 'reraise': True}` - one
        # attempt, no retry, immediate failure. Gemini's API frequently
        # returns transient 503 "The model is overloaded, please try again
        # later" errors under normal production load (a long-documented,
        # widely-reported behavior, not something a client misconfiguration
        # causes) - without this, every one of those transient blips
        # surfaced immediately as a 502 to the frontend. Passing an (empty)
        # HttpRetryOptions here activates the SDK's own built-in defaults:
        # 5 attempts with exponential backoff + jitter, retrying on
        # 408/429/500/502/503/504.
        http_options=types.HttpOptions(retry_options=types.HttpRetryOptions()),
    )
