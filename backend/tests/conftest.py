import os

os.environ.setdefault("GEMINI_API_KEY", "test-gemini-key-not-real")
os.environ.setdefault(
    "DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/rolodex_test"
)
