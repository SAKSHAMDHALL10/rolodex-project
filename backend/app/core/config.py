"""
Application configuration.

All values are read from environment variables (see .env.example).
Nothing sensitive is hard-coded.
"""
from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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

    # --- OpenAI ---
    OPENAI_API_KEY: str = Field(default="")
    OPENAI_EXTRACTION_MODEL: str = Field(default="gpt-4.1")
    OPENAI_EMBEDDING_MODEL: str = Field(default="text-embedding-3-small")
    OPENAI_EMBEDDING_DIMENSIONS: int = Field(default=1536)

    # --- CORS ---
    CORS_ORIGINS: str = Field(default="http://localhost:3000")

    # --- Duplicate detection ---
    DUPLICATE_SIMILARITY_THRESHOLD: float = Field(default=0.90)
    DUPLICATE_NAME_FUZZ_THRESHOLD: int = Field(default=88)

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
