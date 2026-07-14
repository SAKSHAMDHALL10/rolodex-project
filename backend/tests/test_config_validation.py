import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_accepts_correct_psycopg3_url():
    s = Settings(DATABASE_URL="postgresql+psycopg://user:pass@host:5432/db")
    assert s.DATABASE_URL.startswith("postgresql+psycopg://")


def test_rejects_bare_postgresql_scheme():
    """This is exactly what Supabase's dashboard hands out by default."""
    with pytest.raises(ValidationError, match="postgresql\\+psycopg"):
        Settings(DATABASE_URL="postgresql://user:pass@host:5432/db")


def test_rejects_bare_postgres_scheme():
    """This is exactly what Render/Heroku commonly hand out by default."""
    with pytest.raises(ValidationError, match="postgresql\\+psycopg"):
        Settings(DATABASE_URL="postgres://user:pass@host:5432/db")


def test_rejects_unencoded_special_character_in_password():
    """An '@' in the password shifts the host/user split, e.g. 'p@ss' -> host 'ss@host'."""
    with pytest.raises(ValidationError, match="un-encoded special character"):
        Settings(DATABASE_URL="postgresql+psycopg://user:p@ss@host:5432/db")


def test_rejects_unparseable_url():
    with pytest.raises(ValidationError, match="could not be parsed"):
        Settings(DATABASE_URL="not-a-url-at-all")


def test_accepts_percent_encoded_special_character_password():
    """The correct fix for the above: percent-encode the password first."""
    from urllib.parse import quote_plus

    encoded = quote_plus("p@ss")
    s = Settings(DATABASE_URL=f"postgresql+psycopg://user:{encoded}@host:5432/db")
    assert s.DATABASE_URL == f"postgresql+psycopg://user:{encoded}@host:5432/db"
