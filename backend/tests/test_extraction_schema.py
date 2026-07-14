from app.schemas.contact import ExtractionResult
from app.services.extraction import _extraction_json_schema, _lock_down_schema


def test_extraction_result_requires_core_fields():
    result = ExtractionResult(
        full_name="Jane Doe",
        summary="A software engineer.",
        relevance_summary="Worth knowing for backend architecture reviews.",
    )
    assert result.full_name == "Jane Doe"
    assert result.relevance_tags == []


def test_schema_lockdown_sets_additional_properties_false_recursively():
    schema = _extraction_json_schema()
    assert schema["additionalProperties"] is False

    # Nested $defs (e.g. ExperienceItem, EducationItem) must also be locked down.
    for _, sub_schema in schema.get("$defs", {}).items():
        if sub_schema.get("type") == "object":
            assert sub_schema["additionalProperties"] is False


def test_lock_down_schema_is_idempotent():
    schema = {"type": "object", "properties": {"a": {"type": "string"}}}
    _lock_down_schema(schema)
    _lock_down_schema(schema)
    assert schema["additionalProperties"] is False
    assert schema["required"] == ["a"]
