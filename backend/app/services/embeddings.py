"""
Generates a single embedding per contact from a concatenation of the fields
that matter for semantic search: summary, capabilities, relevance, skills.
"""
from google.genai import types

from app.core.ai_client import get_gemini_client
from app.core.config import settings
from app.schemas.contact import ExtractionResult


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


def embed_text(text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> list[float]:
    """
    Embed a piece of text via Gemini's embedding model.

    task_type distinguishes how the embedding will be used - "RETRIEVAL_DOCUMENT"
    for text being stored (a contact's profile), "RETRIEVAL_QUERY" for a search
    query being matched against stored embeddings. Gemini's embedding model
    optimizes the vector differently for each, which improves semantic search
    quality over using a single symmetric embedding for both sides.
    """
    client = get_gemini_client()
    response = client.models.embed_content(
        model=settings.GEMINI_EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(
            output_dimensionality=settings.GEMINI_EMBEDDING_DIMENSIONS,
            task_type=task_type,
        ),
    )
    return response.embeddings[0].values
