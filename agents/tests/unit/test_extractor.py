"""Unit tests for ExtractorAgent (extended structured-output version).

Mocks LLMClient to verify:
- ExtractionResult is returned with all expected fields
- research_type is a valid R1–R6 enum value (or 'unknown')
- invalid research_type from LLM is coerced to 'unknown'
- markdown code-fence stripping works
- all list/dict fields default to empty collections when absent
- research questions are populated in question_data
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from agents.services.extractor import ExtractionResult, ExtractorAgent

_VALID_RESEARCH_TYPES = {
    "evaluation",
    "solution_proposal",
    "validation",
    "philosophical",
    "opinion",
    "personal_experience",
    "unknown",
}

_PAPER_KWARGS = {
    "paper_text": "This paper presents an empirical study of TDD adoption.",
    "title": "TDD Adoption: A Field Study",
    "authors": [{"name": "Alice", "institution": "MIT", "locale": "US"}],
    "year": 2023,
    "venue": "ICSE",
    "doi": "10.1/tdd",
}


def _make_client(response: str) -> MagicMock:
    """Return a mock LLMClient whose complete() coroutine returns *response*."""
    client = MagicMock()
    client.complete = AsyncMock(return_value=response)
    return client


def _json_response(**kwargs) -> str:
    """Return a minimal valid extraction JSON string."""
    defaults = {
        "research_type": "evaluation",
        "venue_type": "conference",
        "venue_name": "ICSE 2023",
        "author_details": [{"name": "Alice", "institution": "MIT", "locale": "US"}],
        "summary": "An empirical field study of TDD.",
        "open_codings": [{"code": "productivity", "definition": "dev speed", "evidence_quote": "faster"}],
        "keywords": ["TDD", "empirical"],
        "question_data": {"RQ1": "Teams adopted TDD in 60% of cases"},
    }
    defaults.update(kwargs)
    return json.dumps(defaults)


class TestExtractionResultShape:
    """Verify ExtractionResult structure from mocked LLM output."""

    @pytest.mark.asyncio
    async def test_returns_extraction_result_type(self) -> None:
        """run() returns an ExtractionResult instance."""
        agent = ExtractorAgent(llm_client=_make_client(_json_response()))
        result = await agent.run(**_PAPER_KWARGS)
        assert isinstance(result, ExtractionResult)

    @pytest.mark.asyncio
    async def test_all_fields_present(self) -> None:
        """ExtractionResult exposes all required fields."""
        agent = ExtractorAgent(llm_client=_make_client(_json_response()))
        result = await agent.run(**_PAPER_KWARGS)
        assert hasattr(result, "research_type")
        assert hasattr(result, "venue_type")
        assert hasattr(result, "venue_name")
        assert hasattr(result, "author_details")
        assert hasattr(result, "summary")
        assert hasattr(result, "open_codings")
        assert hasattr(result, "keywords")
        assert hasattr(result, "question_data")

    @pytest.mark.asyncio
    async def test_research_type_is_valid_enum_value(self) -> None:
        """research_type is always one of the R1–R6 values."""
        agent = ExtractorAgent(llm_client=_make_client(_json_response(research_type="evaluation")))
        result = await agent.run(**_PAPER_KWARGS)
        assert result.research_type in _VALID_RESEARCH_TYPES

    @pytest.mark.asyncio
    async def test_all_research_types_accepted(self) -> None:
        """Each valid research_type string is accepted unchanged."""
        for rt in _VALID_RESEARCH_TYPES:
            agent = ExtractorAgent(llm_client=_make_client(_json_response(research_type=rt)))
            result = await agent.run(**_PAPER_KWARGS)
            assert result.research_type == rt

    @pytest.mark.asyncio
    async def test_invalid_research_type_coerced_to_unknown(self) -> None:
        """An unrecognised research_type from the LLM is coerced to 'unknown'."""
        agent = ExtractorAgent(llm_client=_make_client(_json_response(research_type="nonsense")))
        result = await agent.run(**_PAPER_KWARGS)
        assert result.research_type == "unknown"

    @pytest.mark.asyncio
    async def test_keywords_list(self) -> None:
        """keywords is a list of strings."""
        agent = ExtractorAgent(llm_client=_make_client(_json_response(keywords=["TDD", "agile"])))
        result = await agent.run(**_PAPER_KWARGS)
        assert isinstance(result.keywords, list)
        assert "TDD" in result.keywords

    @pytest.mark.asyncio
    async def test_open_codings_structure(self) -> None:
        """open_codings is a list of dicts with code/definition/evidence_quote keys."""
        codings = [{"code": "productivity", "definition": "speed increase", "evidence_quote": "faster output"}]
        agent = ExtractorAgent(llm_client=_make_client(_json_response(open_codings=codings)))
        result = await agent.run(**_PAPER_KWARGS)
        assert isinstance(result.open_codings, list)
        assert len(result.open_codings) == 1
        assert result.open_codings[0]["code"] == "productivity"

    @pytest.mark.asyncio
    async def test_question_data_populated(self) -> None:
        """question_data maps question IDs to extracted answers."""
        rqs = {"RQ1": "60% adoption", "RQ2": "Pair programming context"}
        agent = ExtractorAgent(llm_client=_make_client(_json_response(question_data=rqs)))
        result = await agent.run(
            **_PAPER_KWARGS,
            research_questions=[{"id": "RQ1", "text": "What is TDD adoption rate?"}],
        )
        assert isinstance(result.question_data, dict)
        assert result.question_data.get("RQ1") == "60% adoption"

    @pytest.mark.asyncio
    async def test_venue_name_nullable(self) -> None:
        """venue_name can be None when LLM returns null."""
        agent = ExtractorAgent(llm_client=_make_client(_json_response(venue_name=None)))
        result = await agent.run(**_PAPER_KWARGS)
        assert result.venue_name is None

    @pytest.mark.asyncio
    async def test_summary_nullable(self) -> None:
        """summary can be None when LLM returns null."""
        agent = ExtractorAgent(llm_client=_make_client(_json_response(summary=None)))
        result = await agent.run(**_PAPER_KWARGS)
        assert result.summary is None


class TestMarkdownFenceStripping:
    """JSON wrapped in markdown code fences is stripped before parsing."""

    @pytest.mark.asyncio
    async def test_strips_json_code_fence(self) -> None:
        """```json ... ``` fences are stripped and the payload parsed."""
        payload = _json_response()
        fenced = f"```json\n{payload}\n```"
        agent = ExtractorAgent(llm_client=_make_client(fenced))
        result = await agent.run(**_PAPER_KWARGS)
        assert isinstance(result, ExtractionResult)
        assert result.research_type == "evaluation"

    @pytest.mark.asyncio
    async def test_strips_generic_code_fence(self) -> None:
        """Generic ``` fences without language tag are also stripped."""
        payload = _json_response()
        fenced = f"```\n{payload}\n```"
        agent = ExtractorAgent(llm_client=_make_client(fenced))
        result = await agent.run(**_PAPER_KWARGS)
        assert isinstance(result, ExtractionResult)


class TestMissingFields:
    """LLM responses with missing optional fields fall back to defaults."""

    @pytest.mark.asyncio
    async def test_missing_keywords_defaults_to_empty_list(self) -> None:
        """Absent keywords field → empty list."""
        payload = {
            "research_type": "evaluation",
            "venue_type": "conference",
            "venue_name": None,
            "author_details": [],
            "summary": None,
            "open_codings": [],
            "question_data": {},
        }
        agent = ExtractorAgent(llm_client=_make_client(json.dumps(payload)))
        result = await agent.run(**_PAPER_KWARGS)
        assert result.keywords == []

    @pytest.mark.asyncio
    async def test_missing_open_codings_defaults_to_empty_list(self) -> None:
        """Absent open_codings field → empty list."""
        payload = {
            "research_type": "validation",
            "venue_type": "journal",
            "venue_name": None,
            "author_details": [],
            "summary": None,
            "keywords": [],
            "question_data": {},
        }
        agent = ExtractorAgent(llm_client=_make_client(json.dumps(payload)))
        result = await agent.run(**_PAPER_KWARGS)
        assert result.open_codings == []

    @pytest.mark.asyncio
    async def test_missing_question_data_defaults_to_empty_dict(self) -> None:
        """Absent question_data field → empty dict."""
        payload = {
            "research_type": "philosophical",
            "venue_type": "workshop",
            "venue_name": None,
            "author_details": [],
            "summary": None,
            "open_codings": [],
            "keywords": [],
        }
        agent = ExtractorAgent(llm_client=_make_client(json.dumps(payload)))
        result = await agent.run(**_PAPER_KWARGS)
        assert result.question_data == {}
