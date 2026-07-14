"""
Application configuration.

All values are read from environment variables (see .env.example).
Nothing sensitive is hard-coded.
"""
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- App ---
    APP_NAME: str = "AI Rolodex Agent"
    ENVIRONMENT: str = Field(default="development")
    API_V1_PREFIX: str = "/api/v1"
    LOG_LEVEL: str = "INFO"

    # --- Database ---
    # Example: postgresql+psycopg://user:password@localhost:5432/rolodex
    DATABASE_URL: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/rolodex"
    )

    # --- Gemini (Google GenAI) ---
    GEMINI_API_KEY: str = Field(default="")
    # Current GA production models as of July 2026. If Google deprecates
    # either of these, update the environment variable - no code change
    # needed. See _validate_gemini_models_on_startup() in app/main.py, which
    # checks these against the live API at boot and fails clearly (not with
    # an obscure runtime exception) if either is no longer available.
    GEMINI_TEXT_MODEL: str = Field(default="gemini-3.5-flash")
    GEMINI_EMBEDDING_MODEL: str = Field(default="gemini-embedding-2")
    # Both gemini-embedding-001 and its replacement gemini-embedding-2 default
    # to 3072 dims but support configurable output_dimensionality via
    # Matryoshka truncation; 1536 is one of Google's own recommended tiers
    # (alongside 3072/768) and keeps the pgvector column size/ivfflat index
    # unchanged regardless of which embedding model generation is in use.
    GEMINI_EMBEDDING_DIMENSIONS: int = Field(default=1536)

    # --- CORS ---
    CORS_ORIGINS: str = Field(default="http://localhost:3000")

    # --- Duplicate detection ---
    DUPLICATE_SIMILARITY_THRESHOLD: float = Field(default=0.90)
    DUPLICATE_NAME_FUZZ_THRESHOLD: int = Field(default=88)

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        """
        Catch the single most common real-world Supabase deployment mistake:
        a password containing special characters (@, #, %, /, :) pasted
        straight from the Supabase dashboard without percent-encoding.
        SQLAlchemy still "parses" such a URL, but silently misreads where the
        password ends and the host begins - e.g. a password of `p@ss` turns
        `...://user:p@ss@host/db` into host `ss@host`, which then fails much
        later with a confusing DNS/auth error instead of a clear one now.
        """
        try:
            url = make_url(value)
        except Exception as exc:
            raise ValueError(
                f"DATABASE_URL could not be parsed: {exc}. Expected format: "
                "postgresql+psycopg://user:password@host:port/dbname"
            ) from exc

        if url.host and "@" in url.host:
            raise ValueError(
                "DATABASE_URL looks malformed: the parsed host "
                f"({url.host!r}) still contains '@', which means the password "
                "portion likely has an un-encoded special character (common "
                "with Supabase passwords containing @, #, %, /, or :). "
                "Percent-encode the password, e.g. with Python's "
                "urllib.parse.quote_plus(password), before building the URL."
            )

        if url.drivername in ("postgresql", "postgres"):
            raise ValueError(
                f"DATABASE_URL uses the bare {url.drivername!r} scheme, which SQLAlchemy "
                "will try to load via psycopg2 - but this project only installs psycopg3 "
                "(see requirements.txt), so it will fail at connection time with "
                "'ModuleNotFoundError: No module named psycopg2'. This is the exact "
                "format Supabase's and Render's dashboards hand out by default. Fix: "
                "change the scheme prefix from "
                f"'{url.drivername}://' to 'postgresql+psycopg://' (same host/user/"
                "password/db, just the scheme changes)."
            )

        if url.drivername not in ("postgresql+psycopg", "postgresql+psycopg2"):
            raise ValueError(
                f"DATABASE_URL uses driver {url.drivername!r}, but this app is "
                "built for psycopg3 with SQLAlchemy 2.x. Use the "
                "'postgresql+psycopg://' scheme."
            )

        return value

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
