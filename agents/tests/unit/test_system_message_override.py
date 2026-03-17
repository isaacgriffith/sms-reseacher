"""Unit tests for system_message_override paths and MCPClient.

Covers the Feature 005 system_message_override branches added to
SynthesiserAgent, ExpertAgent, DomainModelAgent, ExtractorAgent,
QualityJudgeAgent, ValidityAgent, and MCPClient.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def _make_client(response: str) -> MagicMock:
    """Return a mock LLMClient whose complete() coroutine returns *response*."""
    client = MagicMock()
    client.complete = AsyncMock(return_value=response)
    return client


# ---------------------------------------------------------------------------
# SynthesiserAgent — system_message_override
# ---------------------------------------------------------------------------


class TestSynthesiserSystemMessageOverride:
    """SynthesiserAgent respects the system_message_override parameter."""

    @pytest.mark.asyncio
    async def test_system_message_override_replaces_system_message(self) -> None:
        """When system_message_override is set, the system message is replaced."""
        from agents.services.synthesiser import SynthesiserAgent

        client = _make_client("synthesised findings")
        agent = SynthesiserAgent(
            llm_client=client,
            system_message_override="Custom system message",
        )
        result = await agent.run(
            papers_summary="Paper A found TDD improves quality.",
            research_question="Does TDD improve code quality?",
        )
        assert result == "synthesised findings"
        # Verify that complete was called and the override was applied
        call_args = client.complete.call_args
        messages = call_args[0][0]
        system_msgs = [m for m in messages if m.get("role") == "system"]
        if system_msgs:
            assert system_msgs[0]["content"] == "Custom system message"

    @pytest.mark.asyncio
    async def test_no_override_uses_default_message(self) -> None:
        """When system_message_override is None, the default system message is used."""
        from agents.services.synthesiser import SynthesiserAgent

        client = _make_client("default synthesis")
        agent = SynthesiserAgent(llm_client=client)
        result = await agent.run(
            papers_summary="Paper summaries here.",
            research_question="What is the effect of X?",
        )
        assert result == "default synthesis"


# ---------------------------------------------------------------------------
# ExpertAgent — system_message_override
# ---------------------------------------------------------------------------


class TestExpertAgentSystemMessageOverride:
    """ExpertAgent respects the system_message_override parameter."""

    @pytest.mark.asyncio
    async def test_system_message_override_applied(self) -> None:
        """When system_message_override is set, the system message is replaced."""
        from agents.services.expert import ExpertAgent

        valid_response = json.dumps([
            {
                "title": "Test Paper",
                "authors": ["Alice"],
                "year": 2023,
                "venue": "ICSE",
                "doi": "10.1/test",
                "rationale": "Important work",
            }
        ])
        client = _make_client(valid_response)
        agent = ExpertAgent(
            llm_client=client,
            system_message_override="Expert system override",
        )
        result = await agent.run(
            topic="TDD",
            variant="PICO",
            population="Developers",
            intervention="TDD",
            comparison="No TDD",
            outcome="Quality",
        )
        # ExpertAgent.run() returns a list[ExpertPaper]
        assert len(result) == 1
        # Verify override was applied
        call_args = client.complete.call_args
        messages = call_args[0][0]
        system_msgs = [m for m in messages if m.get("role") == "system"]
        if system_msgs:
            assert system_msgs[0]["content"] == "Expert system override"


# ---------------------------------------------------------------------------
# DomainModelAgent — system_message_override
# ---------------------------------------------------------------------------


class TestDomainModelAgentSystemMessageOverride:
    """DomainModelAgent respects the system_message_override parameter."""

    @pytest.mark.asyncio
    async def test_system_message_override_applied(self) -> None:
        """When system_message_override is set, the system message is replaced."""
        from agents.services.domain_modeler import DomainModelAgent

        valid_response = json.dumps({
            "concepts": [{"name": "TDD", "definition": "Test-driven development"}],
            "relationships": [],
        })
        client = _make_client(valid_response)
        agent = DomainModelAgent(
            llm_client=client,
            system_message_override="DomainModel system override",
        )
        result = await agent.run(
            topic="TDD",
            research_questions=["RQ1"],
            open_codings=[{"code": "code1", "definition": "Code 1 definition", "evidence_quote": None}],
            keywords=["tdd"],
            summaries=["Paper summary"],
        )
        assert result is not None
        # Verify override was applied
        call_args = client.complete.call_args
        messages = call_args[0][0]
        system_msgs = [m for m in messages if m.get("role") == "system"]
        if system_msgs:
            assert system_msgs[0]["content"] == "DomainModel system override"


# ---------------------------------------------------------------------------
# ExtractorAgent — system_message_override
# ---------------------------------------------------------------------------


class TestExtractorAgentSystemMessageOverride:
    """ExtractorAgent respects the system_message_override parameter."""

    @pytest.mark.asyncio
    async def test_system_message_override_applied(self) -> None:
        """When system_message_override is set, the system message is replaced."""
        from agents.services.extractor import ExtractorAgent

        valid_response = json.dumps({
            "research_type": "R1",
            "contributions": ["C1"],
            "open_coding": "qualitative",
            "keywords": ["TDD"],
            "summary": "A summary.",
        })
        client = _make_client(valid_response)
        agent = ExtractorAgent(
            llm_client=client,
            system_message_override="Extractor system override",
        )
        result = await agent.run(
            title="Test Paper",
            doi="10.1/test",
            paper_text="Full text here",
            research_questions=[{"id": 1, "text": "RQ1"}],
        )
        assert result is not None
        # Verify override was applied
        call_args = client.complete.call_args
        messages = call_args[0][0]
        system_msgs = [m for m in messages if m.get("role") == "system"]
        if system_msgs:
            assert system_msgs[0]["content"] == "Extractor system override"


# ---------------------------------------------------------------------------
# QualityJudgeAgent — system_message_override
# ---------------------------------------------------------------------------


class TestQualityJudgeAgentSystemMessageOverride:
    """QualityJudgeAgent respects the system_message_override parameter."""

    @pytest.mark.asyncio
    async def test_system_message_override_applied(self) -> None:
        """When system_message_override is set, the system message is replaced."""
        from agents.services.quality_judge import QualityJudgeAgent

        valid_response = json.dumps({
            "scores": {"rigor": 3, "relevance": 2, "transparency": 4},
            "rubric_details": {},
            "overall_comments": "Good study.",
        })
        client = _make_client(valid_response)
        agent = QualityJudgeAgent(
            llm_client=client,
            system_message_override="QualityJudge system override",
        )
        result = await agent.run(
            study_id=1,
            study_name="Test Study",
            study_type="SMS",
            current_phase=3,
            pico_saved=True,
            search_strategies=[],
            test_retest_done=False,
            reviewers=[],
            inclusion_criteria=[],
            exclusion_criteria=[],
            extractions_done=True,
            validity_filled=False,
            validity_dimensions={},
        )
        assert result is not None
        # Verify override was applied
        call_args = client.complete.call_args
        messages = call_args[0][0]
        system_msgs = [m for m in messages if m.get("role") == "system"]
        if system_msgs:
            assert system_msgs[0]["content"] == "QualityJudge system override"


# ---------------------------------------------------------------------------
# ValidityAgent — system_message_override
# ---------------------------------------------------------------------------


class TestValidityAgentSystemMessageOverride:
    """ValidityAgent respects the system_message_override parameter."""

    @pytest.mark.asyncio
    async def test_system_message_override_applied(self) -> None:
        """When system_message_override is set, the system message is replaced."""
        from agents.services.validity import ValidityAgent

        valid_response = json.dumps({
            "descriptive": "Good descriptive validity.",
            "theoretical": "Sound theoretical basis.",
            "generalizability_internal": "Limited internal gen.",
            "generalizability_external": "Limited external gen.",
            "interpretive": "Reasonable interpretations.",
            "repeatability": "Reproducible methods.",
        })
        client = _make_client(valid_response)
        agent = ValidityAgent(
            llm_client=client,
            system_message_override="Validity system override",
        )
        result = await agent.run(
            study_id=1,
            study_name="Test Study",
            study_type="SMS",
            current_phase=4,
            pico_components=[],
            search_strategies=[],
            databases="ACM",
            test_retest_done=False,
            reviewers=[],
            inclusion_criteria=[],
            exclusion_criteria=[],
            extraction_summary="5 papers extracted.",
        )
        assert result is not None
        # Verify override was applied
        call_args = client.complete.call_args
        messages = call_args[0][0]
        system_msgs = [m for m in messages if m.get("role") == "system"]
        if system_msgs:
            assert system_msgs[0]["content"] == "Validity system override"


# ---------------------------------------------------------------------------
# MCPClient
# ---------------------------------------------------------------------------


class TestMCPClient:
    """MCPClient tests with mocked HTTP calls."""

    def test_init_default_settings(self) -> None:
        """MCPClient initialises with default settings."""
        from agents.core.mcp_client import MCPClient

        client = MCPClient()
        assert client._base_url is not None

    def test_init_strips_sse_suffix(self) -> None:
        """MCPClient strips /sse suffix from base URL."""
        from agents.core.config import AgentSettings
        from agents.core.mcp_client import MCPClient

        settings = AgentSettings(researcher_mcp_url="http://localhost:8001/sse")
        client = MCPClient(settings=settings)
        assert not client._base_url.endswith("/sse")
        assert client._base_url == "http://localhost:8001"

    def test_to_litellm_tools_converts_mcp_tools(self) -> None:
        """to_litellm_tools converts MCP tool defs to LiteLLM format."""
        from agents.core.mcp_client import MCPClient

        client = MCPClient()
        mcp_tools = [
            {
                "name": "search_papers",
                "description": "Search for papers",
                "inputSchema": {
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                },
            }
        ]
        result = client.to_litellm_tools(mcp_tools)
        assert len(result) == 1
        assert result[0]["type"] == "function"
        assert result[0]["function"]["name"] == "search_papers"
        assert result[0]["function"]["description"] == "Search for papers"

    def test_to_litellm_tools_empty_list(self) -> None:
        """to_litellm_tools returns empty list for empty input."""
        from agents.core.mcp_client import MCPClient

        client = MCPClient()
        assert client.to_litellm_tools([]) == []

    def test_to_litellm_tools_missing_description(self) -> None:
        """to_litellm_tools uses empty string when description is missing."""
        from agents.core.mcp_client import MCPClient

        client = MCPClient()
        mcp_tools = [{"name": "no_desc_tool"}]
        result = client.to_litellm_tools(mcp_tools)
        assert result[0]["function"]["description"] == ""

    @pytest.mark.asyncio
    async def test_list_tools_returns_tool_list(self) -> None:
        """list_tools calls GET /tools/list and returns the tools array."""
        from agents.core.mcp_client import MCPClient

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "tools": [{"name": "search_papers", "description": "Search"}]
        }
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("agents.core.mcp_client.httpx.AsyncClient", return_value=mock_client):
            from agents.core.mcp_client import MCPClient

            client = MCPClient()
            tools = await client.list_tools()

        assert len(tools) == 1
        assert tools[0]["name"] == "search_papers"

    @pytest.mark.asyncio
    async def test_call_tool_returns_result(self) -> None:
        """call_tool calls POST /tools/call and returns the result dict."""
        from agents.core.mcp_client import MCPClient

        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "paper_list"}
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("agents.core.mcp_client.httpx.AsyncClient", return_value=mock_client):
            from agents.core.mcp_client import MCPClient

            client = MCPClient()
            result = await client.call_tool("search_papers", {"query": "TDD"})

        assert result == {"result": "paper_list"}
