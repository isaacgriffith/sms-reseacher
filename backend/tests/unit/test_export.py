"""Unit tests for backend.services.export.

Key assertions:
- No Settings-derived field names appear in any export payload (_REDACTED_FIELDS check)
- _sanitise_payload removes sensitive keys recursively
- _extractions_to_csv produces valid CSV bytes
- build_export raises ValueError for unknown format
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch


# ---------------------------------------------------------------------------
# _REDACTED_FIELDS is populated correctly
# ---------------------------------------------------------------------------


def test_redacted_fields_contains_required_keys():
    """_REDACTED_FIELDS must include the four mandated Settings fields."""
    from backend.services.export import _REDACTED_FIELDS

    required = {"database_url", "secret_key", "anthropic_api_key", "redis_url"}
    assert required <= _REDACTED_FIELDS, (
        f"Missing redacted fields: {required - _REDACTED_FIELDS}"
    )


# ---------------------------------------------------------------------------
# _sanitise_payload
# ---------------------------------------------------------------------------


def test_sanitise_payload_removes_top_level_sensitive_keys():
    """_sanitise_payload strips all _REDACTED_FIELDS from a flat dict."""
    from backend.services.export import _sanitise_payload

    payload = {
        "database_url": "postgresql://user:pass@host/db",
        "secret_key": "s3cr3t",
        "anthropic_api_key": "sk-ant-xxx",
        "redis_url": "redis://localhost:6379",
        "study_title": "Safe value",
    }
    result = _sanitise_payload(payload)
    assert "database_url" not in result
    assert "secret_key" not in result
    assert "anthropic_api_key" not in result
    assert "redis_url" not in result
    assert result["study_title"] == "Safe value"


def test_sanitise_payload_removes_nested_sensitive_keys():
    """_sanitise_payload strips _REDACTED_FIELDS at any nesting depth."""
    from backend.services.export import _sanitise_payload

    payload = {
        "config": {
            "database_url": "postgresql://...",
            "name": "Safe",
        },
        "data": [
            {"secret_key": "leak", "value": 42},
        ],
    }
    result = _sanitise_payload(payload)
    assert "database_url" not in result["config"]
    assert result["config"]["name"] == "Safe"
    assert "secret_key" not in result["data"][0]
    assert result["data"][0]["value"] == 42


def test_sanitise_payload_preserves_non_sensitive_content():
    """_sanitise_payload leaves non-sensitive fields untouched."""
    from backend.services.export import _sanitise_payload

    payload = {"title": "Study A", "extractions": [{"research_type": "evaluation"}]}
    result = _sanitise_payload(payload)
    assert result == payload


def test_sanitise_payload_handles_empty_dict():
    """_sanitise_payload returns empty dict for empty input."""
    from backend.services.export import _sanitise_payload

    assert _sanitise_payload({}) == {}


def test_sanitise_payload_handles_list():
    """_sanitise_payload handles a top-level list."""
    from backend.services.export import _sanitise_payload

    result = _sanitise_payload([{"secret_key": "x", "value": 1}])
    assert isinstance(result, list)
    assert "secret_key" not in result[0]
    assert result[0]["value"] == 1


# ---------------------------------------------------------------------------
# _extractions_to_csv
# ---------------------------------------------------------------------------


def test_extractions_to_csv_returns_bytes():
    """_extractions_to_csv returns bytes."""
    from backend.services.export import _extractions_to_csv

    result = _extractions_to_csv([])
    assert isinstance(result, bytes)


def test_extractions_to_csv_header_row_for_empty_input():
    """_extractions_to_csv returns a header row even for empty list."""
    from backend.services.export import _extractions_to_csv

    csv_bytes = _extractions_to_csv([])
    header = csv_bytes.decode("utf-8").splitlines()[0]
    assert "id" in header
    assert "research_type" in header


def test_extractions_to_csv_includes_data_rows():
    """_extractions_to_csv encodes extraction data correctly."""
    from backend.services.export import _extractions_to_csv

    extractions = [
        {
            "id": 1,
            "candidate_paper_id": 10,
            "research_type": "evaluation",
            "venue_type": "journal",
            "venue_name": "TSE",
            "extraction_status": "ai_complete",
            "summary": "A study of TDD.",
            "keywords": ["TDD", "testing"],
        }
    ]
    csv_bytes = _extractions_to_csv(extractions)
    decoded = csv_bytes.decode("utf-8")
    assert "evaluation" in decoded
    assert "TSE" in decoded
    # Keywords list should be joined
    assert "TDD" in decoded


def test_extractions_to_csv_no_sensitive_fields():
    """_extractions_to_csv output must not contain any _REDACTED_FIELDS values."""
    from backend.services.export import _REDACTED_FIELDS, _extractions_to_csv

    extractions = [
        {
            "id": 1,
            "candidate_paper_id": 10,
            "research_type": "evaluation",
            "venue_type": "journal",
            "venue_name": "TSE",
            "extraction_status": "ai_complete",
            "summary": None,
            "keywords": [],
            # These would be an unexpected injection; CSV must not output them
        }
    ]
    csv_text = _extractions_to_csv(extractions).decode("utf-8")
    for field in _REDACTED_FIELDS:
        assert field not in csv_text, f"Sensitive field name '{field}' found in CSV output"


# ---------------------------------------------------------------------------
# build_export — format validation
# ---------------------------------------------------------------------------


def test_build_export_raises_for_unknown_format():
    """build_export raises ValueError for an unrecognised format string."""
    import asyncio
    from unittest.mock import AsyncMock, patch

    async def _run():
        with patch("backend.services.export._load_study_data", AsyncMock(return_value={})):
            from backend.services.export import build_export
            try:
                await build_export(study_id=1, format="invalid_format")
                assert False, "Expected ValueError"
            except ValueError as exc:
                assert "invalid_format" in str(exc)

    asyncio.run(_run())


# ---------------------------------------------------------------------------
# JSON export — no settings fields in output
# ---------------------------------------------------------------------------


def test_json_export_contains_no_redacted_field_names():
    """The JSON-only export payload must not contain any _REDACTED_FIELDS key names."""
    import asyncio
    from unittest.mock import AsyncMock, patch

    safe_study_data = {
        "study": {"id": 1, "title": "Safe Study"},
        "extractions": [],
        "domain_model": {},
        "charts": [],
    }

    async def _run():
        with patch("backend.services.export._load_study_data", AsyncMock(return_value=safe_study_data)):
            from backend.services.export import _build_json_only
            payload_bytes = await _build_json_only(study_id=1)
            decoded = json.loads(payload_bytes)

            from backend.services.export import _REDACTED_FIELDS, _collect_keys
            all_keys = _collect_keys(decoded)
            leaked = all_keys & _REDACTED_FIELDS
            assert not leaked, f"Redacted field names found in JSON export: {leaked}"

    asyncio.run(_run())
