"""
Generates a single embedding per contact from a concatenation of the fields
that matter for semantic search: summary, capabilities, relevance, skills.
"""
from openai import OpenAI

from app.core.config import settings
from app.schemas.contact import ExtractionResult


def _client() -> OpenAI:
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def build_embedding_text(data: ExtractionResult) -> str:
    """Concatenate the fields worth embedding into one text blob."""
    parts = [
        data.summary or "",
        "Relevance: " + (data.relevance_summary or ""),
        "Tags: " + ", ".join(data.relevance_tags),
        "Skills: " + ", ".join(data.skills),
        "Technologies: " + ", ".join(data.technologies),
        "Domains: " + ", ".join(data.domains),
        "Capabilities: " + ", ".join(data.capabilities),
    ]
    return "\n".join(p for p in parts if p.strip())


def embed_text(text: str) -> list[float]:
    client = _client()
    response = client.embeddings.create(
        model=settings.OPENAI_EMBEDDING_MODEL,
        input=text,
        dimensions=settings.OPENAI_EMBEDDING_DIMENSIONS,
    )
    return response.data[0].embedding
