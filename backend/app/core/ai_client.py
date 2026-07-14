"""
Shared OpenAI client construction.

Both the extraction and embeddings services need an OpenAI client; this
centralizes that (removing duplicated `_client()` helpers) and gives a
single place to fail fast when `OPENAI_API_KEY` isn't configured, rather
than letting every call site make a live network round-trip just to hit an
auth error from OpenAI's side.
"""
from functools import lru_cache

import openai
from openai import OpenAI

from app.core.config import settings


class OpenAIKeyMissingError(openai.OpenAIError):
    """
    Raised before any network call when OPENAI_API_KEY isn't configured.
    Subclasses openai.OpenAIError so existing `except openai.OpenAIError`
    handling in the routers already catches this correctly - callers get a
    clean 502 with an actionable message instead of an unhandled crash or a
    generic upstream authentication error.
    """


@lru_cache
def get_openai_client() -> OpenAI:
    if not settings.OPENAI_API_KEY:
        raise OpenAIKeyMissingError(
            "OPENAI_API_KEY is not configured on this server. AI extraction and "
            "AI-powered search are unavailable until it's set in the environment."
        )
    return OpenAI(api_key=settings.OPENAI_API_KEY)
