"""Unit tests for the upgraded get_references and get_citations tools (T042).

Covers:
- Semantic Scholar primary path for get_references.
- CrossRef fallback when Semantic Scholar returns empty for get_references.
- Empty result for unknown DOI returns empty list.
- Semantic Scholar primary path for get_citations.
- CrossRef fallback when Semantic Scholar returns empty for get_citations.
- ReferenceRecord has intent field; CitationRecord has citation_source field.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestGetReferences:
    """Tests for the upgraded get_references tool."""

    @pytest.mark.asyncio
    async def test_semantic_scholar_primary_path(self) -> None:
        """When S2 returns references, CrossRef is not called."""
        from researcher_mcp.tools.snowball import get_references

        s2_refs = [
            {"title": "Ref A", "doi": "10.1/a", "intent": "methodology", "citation_source": "semantic_scholar"},
            {"title": "Ref B", "doi": "10.1/b", "intent": "background", "citation_source": "semantic_scholar"},
        ]
        crossref_mock = AsyncMock()
        with (
            patch("researcher_mcp.tools.snowball._get_references_semantic_scholar", new=AsyncMock(return_value=s2_refs)),
            patch("researcher_mcp.tools.snowball._get_references_crossref", new=crossref_mock),
        ):
            result = await get_references(doi="10.1145/test")
            assert len(result) == 2
            assert result[0]["title"] == "Ref A"
            # CrossRef should NOT be called since S2 returned results
            crossref_mock.assert_not_called()

    @pytest.mark.asyncio
    async def test_crossref_fallback_when_s2_returns_empty(self) -> None:
        """When S2 returns no references, CrossRef fallback is used."""
        from researcher_mcp.tools.snowball import get_references

        cr_refs = [{"title": "CrossRef Ref", "doi": "10.1/cr", "intent": "unknown", "citation_source": "crossref"}]
        with (
            patch("researcher_mcp.tools.snowball._get_references_semantic_scholar", new=AsyncMock(return_value=[])),
            patch("researcher_mcp.tools.snowball._get_references_crossref", new=AsyncMock(return_value=cr_refs)),
        ):
            result = await get_references(doi="10.1145/test")
            assert len(result) == 1
            assert result[0]["citation_source"] == "crossref"

    @pytest.mark.asyncio
    async def test_empty_result_for_unknown_doi(self) -> None:
        """Unknown DOI returns empty list without error."""
        from researcher_mcp.tools.snowball import get_references

        with (
            patch("researcher_mcp.tools.snowball._get_references_semantic_scholar", new=AsyncMock(return_value=[])),
            patch("researcher_mcp.tools.snowball._get_references_crossref", new=AsyncMock(return_value=[])),
        ):
            result = await get_references(doi="10.9999/unknown")
            assert result == []

    @pytest.mark.asyncio
    async def test_reference_record_has_intent_field(self) -> None:
        """Each returned reference has an 'intent' field."""
        from researcher_mcp.tools.snowball import get_references

        s2_refs = [{"title": "Ref A", "doi": "10.1/a", "intent": "result", "citation_source": "semantic_scholar"}]
        with (
            patch("researcher_mcp.tools.snowball._get_references_semantic_scholar", new=AsyncMock(return_value=s2_refs)),
        ):
            result = await get_references(doi="10.1145/test")
            assert "intent" in result[0]
            assert result[0]["intent"] == "result"

    @pytest.mark.asyncio
    async def test_max_results_respected(self) -> None:
        """max_results parameter limits the returned count."""
        from researcher_mcp.tools.snowball import get_references

        s2_refs = [{"title": f"Ref {i}", "doi": f"10.1/{i}", "intent": "unknown", "citation_source": "semantic_scholar"} for i in range(20)]
        with (
            patch("researcher_mcp.tools.snowball._get_references_semantic_scholar", new=AsyncMock(return_value=s2_refs[:5])),
        ):
            result = await get_references(doi="10.1145/test", max_results=5)
            assert len(result) <= 5


class TestGetCitations:
    """Tests for the upgraded get_citations tool."""

    @pytest.mark.asyncio
    async def test_semantic_scholar_primary_path(self) -> None:
        """When S2 returns citations, CrossRef is not called."""
        from researcher_mcp.tools.snowball import get_citations

        s2_cites = [
            {"title": "Cite A", "doi": "10.1/ca", "citation_source": "semantic_scholar"},
        ]
        crossref_mock = AsyncMock()
        with (
            patch("researcher_mcp.tools.snowball._get_citations_semantic_scholar", new=AsyncMock(return_value=s2_cites)),
            patch("researcher_mcp.tools.snowball._get_citations_crossref", new=crossref_mock),
        ):
            result = await get_citations(doi="10.1145/test")
            assert len(result) == 1
            assert result[0]["citation_source"] == "semantic_scholar"
            crossref_mock.assert_not_called()

    @pytest.mark.asyncio
    async def test_crossref_fallback_when_s2_returns_empty(self) -> None:
        """When S2 returns no citations, CrossRef fallback is used."""
        from researcher_mcp.tools.snowball import get_citations

        cr_cites = [{"title": "CR Cite", "doi": "10.1/cr", "citation_source": "crossref"}]
        with (
            patch("researcher_mcp.tools.snowball._get_citations_semantic_scholar", new=AsyncMock(return_value=[])),
            patch("researcher_mcp.tools.snowball._get_citations_crossref", new=AsyncMock(return_value=cr_cites)),
        ):
            result = await get_citations(doi="10.1145/test")
            assert len(result) == 1
            assert result[0]["citation_source"] == "crossref"

    @pytest.mark.asyncio
    async def test_citation_record_has_citation_source_field(self) -> None:
        """Each returned citation has a 'citation_source' field."""
        from researcher_mcp.tools.snowball import get_citations

        s2_cites = [{"title": "Cite A", "doi": "10.1/ca", "citation_source": "semantic_scholar"}]
        with (
            patch("researcher_mcp.tools.snowball._get_citations_semantic_scholar", new=AsyncMock(return_value=s2_cites)),
        ):
            result = await get_citations(doi="10.1145/test")
            assert "citation_source" in result[0]

    @pytest.mark.asyncio
    async def test_empty_result_for_unknown_doi(self) -> None:
        """Unknown DOI returns empty list without error."""
        from researcher_mcp.tools.snowball import get_citations

        with (
            patch("researcher_mcp.tools.snowball._get_citations_semantic_scholar", new=AsyncMock(return_value=[])),
            patch("researcher_mcp.tools.snowball._get_citations_crossref", new=AsyncMock(return_value=[])),
        ):
            result = await get_citations(doi="10.9999/unknown")
            assert result == []

    @pytest.mark.asyncio
    async def test_max_results_respected(self) -> None:
        """max_results parameter limits the returned count for citations."""
        from researcher_mcp.tools.snowball import get_citations

        s2_cites = [
            {"title": f"Cite {i}", "doi": f"10.1/{i}", "citation_source": "semantic_scholar"}
            for i in range(20)
        ]
        with (
            patch("researcher_mcp.tools.snowball._get_citations_semantic_scholar", new=AsyncMock(return_value=s2_cites[:5])),
        ):
            result = await get_citations(doi="10.1145/test", max_results=5)
            assert len(result) <= 5


class TestGetReferencesSemantic:
    """Tests for the _get_references_semantic_scholar helper."""

    @pytest.mark.asyncio
    async def test_s2_references_with_intents(self) -> None:
        """_get_references_semantic_scholar maps intents correctly."""
        from researcher_mcp.tools.snowball import _get_references_semantic_scholar

        mock_ss = MagicMock()
        mock_ss._get = AsyncMock(
            return_value={
                "data": [
                    {
                        "citedPaper": {
                            "title": "Cited Paper",
                            "externalIds": {"DOI": "10.1/cited"},
                            "year": 2020,
                            "authors": [{"name": "Alice"}],
                        },
                        "intents": ["methodology"],
                    }
                ]
            }
        )

        with patch("researcher_mcp.tools.snowball._get_ss", return_value=mock_ss):
            result = await _get_references_semantic_scholar("10.1/source", 10)

        assert len(result) == 1
        assert result[0]["intent"] == "methodology"
        assert result[0]["citation_source"] == "semantic_scholar"

    @pytest.mark.asyncio
    async def test_s2_references_returns_empty_on_http_error(self) -> None:
        """_get_references_semantic_scholar returns [] on HTTPStatusError."""
        import httpx
        from researcher_mcp.tools.snowball import _get_references_semantic_scholar

        mock_ss = MagicMock()
        mock_ss._get = AsyncMock(
            side_effect=httpx.HTTPStatusError("404", request=MagicMock(), response=MagicMock())
        )

        with patch("researcher_mcp.tools.snowball._get_ss", return_value=mock_ss):
            result = await _get_references_semantic_scholar("10.9/missing", 10)

        assert result == []

    @pytest.mark.asyncio
    async def test_s2_references_intent_unknown_fallback(self) -> None:
        """_get_references_semantic_scholar maps unknown intents to 'unknown'."""
        from researcher_mcp.tools.snowball import _get_references_semantic_scholar

        mock_ss = MagicMock()
        mock_ss._get = AsyncMock(
            return_value={
                "data": [
                    {
                        "citedPaper": {
                            "title": "No Intent Paper",
                            "externalIds": {},
                            "year": None,
                            "authors": [],
                        },
                        "intents": [],
                    }
                ]
            }
        )

        with patch("researcher_mcp.tools.snowball._get_ss", return_value=mock_ss):
            result = await _get_references_semantic_scholar("10.1/test", 10)

        assert result[0]["intent"] == "unknown"


class TestGetCitationsSemantic:
    """Tests for the _get_citations_semantic_scholar and _get_citations_crossref helpers."""

    @pytest.mark.asyncio
    async def test_s2_citations_returns_records(self) -> None:
        """_get_citations_semantic_scholar parses citing papers correctly."""
        from researcher_mcp.tools.snowball import _get_citations_semantic_scholar

        mock_ss = MagicMock()
        mock_ss._get = AsyncMock(
            return_value={
                "data": [
                    {
                        "citingPaper": {
                            "title": "Citing Paper",
                            "externalIds": {"DOI": "10.1/citing"},
                            "year": 2023,
                            "authors": [{"name": "Bob"}],
                        }
                    }
                ]
            }
        )

        with patch("researcher_mcp.tools.snowball._get_ss", return_value=mock_ss):
            result = await _get_citations_semantic_scholar("10.1/source", 10)

        assert len(result) == 1
        assert result[0]["citation_source"] == "semantic_scholar"
        assert result[0]["title"] == "Citing Paper"

    @pytest.mark.asyncio
    async def test_s2_citations_returns_empty_on_transport_error(self) -> None:
        """_get_citations_semantic_scholar returns [] on TransportError."""
        import httpx
        from researcher_mcp.tools.snowball import _get_citations_semantic_scholar

        mock_ss = MagicMock()
        mock_ss._get = AsyncMock(side_effect=httpx.TransportError("network error"))

        with patch("researcher_mcp.tools.snowball._get_ss", return_value=mock_ss):
            result = await _get_citations_semantic_scholar("10.9/missing", 10)

        assert result == []

    @pytest.mark.asyncio
    async def test_crossref_references_fallback(self) -> None:
        """_get_references_crossref returns records from CrossRef works API."""
        import httpx
        from unittest.mock import MagicMock, AsyncMock
        from researcher_mcp.tools.snowball import _get_references_crossref

        mock_resp = MagicMock(spec=httpx.Response)
        mock_resp.status_code = 200
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {
            "message": {
                "reference": [
                    {
                        "article-title": "CrossRef Ref Paper",
                        "DOI": "10.1/cr-ref",
                        "year": "2021",
                    }
                ]
            }
        }

        mock_client = MagicMock(spec=httpx.AsyncClient)
        mock_client.get = AsyncMock(return_value=mock_resp)

        with patch("researcher_mcp.tools.snowball._get_client", return_value=mock_client):
            result = await _get_references_crossref("10.1/source", 10)

        assert len(result) == 1
        assert result[0]["title"] == "CrossRef Ref Paper"
        assert result[0]["citation_source"] == "crossref"

    @pytest.mark.asyncio
    async def test_crossref_references_returns_empty_on_error(self) -> None:
        """_get_references_crossref returns [] on HTTP error."""
        import httpx
        from researcher_mcp.tools.snowball import _get_references_crossref

        mock_client = MagicMock(spec=httpx.AsyncClient)
        mock_client.get = AsyncMock(
            side_effect=httpx.HTTPStatusError("404", request=MagicMock(), response=MagicMock())
        )

        with patch("researcher_mcp.tools.snowball._get_client", return_value=mock_client):
            result = await _get_references_crossref("10.9/missing", 10)

        assert result == []

    @pytest.mark.asyncio
    async def test_crossref_citations_fallback_from_openalex(self) -> None:
        """_get_citations_crossref returns records via OpenAlex API."""
        import httpx
        from researcher_mcp.tools.snowball import _get_citations_crossref

        mock_resp = MagicMock(spec=httpx.Response)
        mock_resp.status_code = 200
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {
            "results": [
                {
                    "id": "W99",
                    "title": "OA Citing Paper",
                    "doi": "https://doi.org/10.1/oa-citing",
                    "publication_year": 2022,
                    "authorships": [
                        {"author": {"display_name": "Alice Smith"}}
                    ],
                }
            ]
        }

        mock_client = MagicMock(spec=httpx.AsyncClient)
        mock_client.get = AsyncMock(return_value=mock_resp)

        with patch("researcher_mcp.tools.snowball._get_client", return_value=mock_client):
            result = await _get_citations_crossref("10.1/source", 10)

        assert len(result) == 1
        assert result[0]["title"] == "OA Citing Paper"
        assert result[0]["citation_source"] == "crossref"
        assert result[0]["doi"] == "10.1/oa-citing"

    @pytest.mark.asyncio
    async def test_crossref_citations_returns_empty_on_error(self) -> None:
        """_get_citations_crossref returns [] on HTTP error."""
        import httpx
        from researcher_mcp.tools.snowball import _get_citations_crossref

        mock_client = MagicMock(spec=httpx.AsyncClient)
        mock_client.get = AsyncMock(
            side_effect=httpx.TransportError("network error")
        )

        with patch("researcher_mcp.tools.snowball._get_client", return_value=mock_client):
            result = await _get_citations_crossref("10.9/missing", 10)

        assert result == []


class TestIntentMapping:
    """Tests for _intent_from_category helper."""

    def test_methodology_intent(self) -> None:
        """'methodology' maps to 'methodology'."""
        from researcher_mcp.tools.snowball import _intent_from_category

        assert _intent_from_category("methodology") == "methodology"

    def test_extends_maps_to_methodology(self) -> None:
        """'extends' maps to 'methodology'."""
        from researcher_mcp.tools.snowball import _intent_from_category

        assert _intent_from_category("extends") == "methodology"

    def test_background_intent(self) -> None:
        """'background' maps to 'background'."""
        from researcher_mcp.tools.snowball import _intent_from_category

        assert _intent_from_category("background") == "background"

    def test_result_intent(self) -> None:
        """'result' maps to 'result'."""
        from researcher_mcp.tools.snowball import _intent_from_category

        assert _intent_from_category("result") == "result"

    def test_unknown_maps_to_unknown(self) -> None:
        """Unknown category maps to 'unknown'."""
        from researcher_mcp.tools.snowball import _intent_from_category

        assert _intent_from_category("something_else") == "unknown"

    def test_none_maps_to_unknown(self) -> None:
        """None input maps to 'unknown'."""
        from researcher_mcp.tools.snowball import _intent_from_category

        assert _intent_from_category(None) == "unknown"
