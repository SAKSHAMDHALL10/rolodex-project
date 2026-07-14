from app.schemas.contact import ExtractionResult
from app.services.extraction import _NL_QUERY_JSON_SCHEMA


def test_extraction_result_requires_core_fields():
    result = ExtractionResult(
        full_name="Jane Doe",
        summary="A software engineer.",
        relevance_summary="Worth knowing for backend architecture reviews.",
    )
    assert result.full_name == "Jane Doe"
    assert result.relevance_tags == []


def test_extraction_result_is_a_valid_pydantic_model_for_gemini_response_schema():
    """
    Gemini's response_schema accepts a Pydantic model class directly - just
    confirm ExtractionResult is a plain BaseModel subclass the SDK can convert.
    """
    from pydantic import BaseModel

    assert issubclass(ExtractionResult, BaseModel)


def test_nl_query_json_schema_is_well_formed():
    assert _NL_QUERY_JSON_SCHEMA["type"] == "object"
    expected_fields = {
        "role",
        "company",
        "industry",
        "location",
        "skills",
        "technologies",
        "tags",
        "semantic_phrase",
    }
    assert set(_NL_QUERY_JSON_SCHEMA["properties"].keys()) == expected_fields
    assert "semantic_phrase" in _NL_QUERY_JSON_SCHEMA["required"]
