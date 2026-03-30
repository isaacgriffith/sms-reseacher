"""Unit tests for export service."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# _sanitise_payload
# ---------------------------------------------------------------------------


class TestSanitisePayload:
    """_sanitise_payload removes _REDACTED_FIELDS keys."""

    def test_removes_secret_key(self) -> None:
        """Removes secret_key from top-level dict."""
        from backend.services.export import _sanitise_payload

        result = _sanitise_payload({"title": "My Study", "secret_key": "abc"})
        assert "secret_key" not in result
        assert result["title"] == "My Study"

    def test_removes_nested_redacted_field(self) -> None:
        """Removes database_url from nested dict."""
        from backend.services.export import _sanitise_payload

        result = _sanitise_payload({"outer": {"database_url": "postgres://...", "val": 1}})
        assert "database_url" not in result["outer"]
        assert result["outer"]["val"] == 1

    def test_preserves_list_values(self) -> None:
        """Removes redacted keys inside list elements."""
        from backend.services.export import _sanitise_payload

        result = _sanitise_payload([{"a": 1, "secret_key": "x"}, {"b": 2}])
        assert "secret_key" not in result[0]
        assert result[1]["b"] == 2

    def test_passthrough_scalar(self) -> None:
        """Returns scalars unchanged."""
        from backend.services.export import _sanitise_payload

        assert _sanitise_payload(42) == 42
        assert _sanitise_payload("hello") == "hello"


# ---------------------------------------------------------------------------
# _collect_keys
# ---------------------------------------------------------------------------


class TestCollectKeys:
    """_collect_keys recursively gathers dict keys."""

    def test_flat_dict(self) -> None:
        """Returns all keys in a flat dict."""
        from backend.services.export import _collect_keys

        keys = _collect_keys({"a": 1, "b": 2})
        assert keys == {"a", "b"}

    def test_nested_dict(self) -> None:
        """Returns keys from outer and inner dicts."""
        from backend.services.export import _collect_keys

        keys = _collect_keys({"outer": {"inner": 42}})
        assert "outer" in keys
        assert "inner" in keys

    def test_list_of_dicts(self) -> None:
        """Returns keys from all dicts in a list."""
        from backend.services.export import _collect_keys

        keys = _collect_keys([{"x": 1}, {"y": 2}])
        assert "x" in keys
        assert "y" in keys

    def test_non_dict_non_list(self) -> None:
        """Returns empty set for non-dict, non-list values."""
        from backend.services.export import _collect_keys

        assert _collect_keys("string") == set()
        assert _collect_keys(99) == set()


# ---------------------------------------------------------------------------
# _extractions_to_csv
# ---------------------------------------------------------------------------


class TestExtractionsToCSV:
    """_extractions_to_csv serialises extraction dicts."""

    def test_empty_list_returns_header(self) -> None:
        """Returns header row when extractions list is empty."""
        from backend.services.export import _extractions_to_csv

        result = _extractions_to_csv([])
        assert b"id,candidate_paper_id" in result

    def test_single_row(self) -> None:
        """Serialises a single extraction dict to CSV bytes."""
        from backend.services.export import _extractions_to_csv

        extractions = [{"id": 1, "candidate_paper_id": 2, "research_type": "empirical"}]
        result = _extractions_to_csv(extractions)
        assert b"1" in result
        assert b"empirical" in result

    def test_keywords_list_is_joined(self) -> None:
        """Joins keywords list into semicolon-separated string."""
        from backend.services.export import _extractions_to_csv

        extractions = [{"id": 1, "keywords": ["ml", "ai", "testing"]}]
        result = _extractions_to_csv(extractions)
        assert b"ml; ai; testing" in result

    def test_keywords_string_not_joined(self) -> None:
        """Passes through string keywords without modification."""
        from backend.services.export import _extractions_to_csv

        extractions = [{"id": 1, "keywords": "already-a-string"}]
        result = _extractions_to_csv(extractions)
        assert b"already-a-string" in result


# ---------------------------------------------------------------------------
# _warn_and_assert_redaction
# ---------------------------------------------------------------------------


class TestWarnAndAssertRedaction:
    """_warn_and_assert_redaction raises RuntimeError when keys leak."""

    def test_no_error_when_clean(self) -> None:
        """Does not raise when sanitised payload has no redacted keys."""
        from backend.services.export import _warn_and_assert_redaction

        raw = {"title": "test", "secret_key": "s"}
        sanitised = {"title": "test"}
        _warn_and_assert_redaction(raw, sanitised, "test_context")  # no exception

    def test_raises_when_key_survives(self) -> None:
        """Raises RuntimeError when a redacted key survives sanitisation."""
        from backend.services.export import _warn_and_assert_redaction

        raw = {"secret_key": "leaked"}
        sanitised = {"secret_key": "leaked"}  # improperly sanitised
        with pytest.raises(RuntimeError):
            _warn_and_assert_redaction(raw, sanitised, "test_context")


# ---------------------------------------------------------------------------
# build_export — invalid format
# ---------------------------------------------------------------------------


class TestBuildExport:
    """build_export raises ValueError for unknown format."""

    @pytest.mark.asyncio
    async def test_raises_for_unknown_format(self) -> None:
        """Raises ValueError for an unrecognised export format string."""
        from backend.services.export import build_export

        with pytest.raises(ValueError, match="Unknown export format"):
            await build_export(1, "unknown_format")


# ---------------------------------------------------------------------------
# _load_study_data — mocked DB
# ---------------------------------------------------------------------------


class TestLoadStudyData:
    """_load_study_data returns structured dict from DB query results."""

    @pytest.mark.asyncio
    async def test_returns_empty_dicts_when_study_missing(self) -> None:
        """When study is None, returns empty study/domain_model dicts."""
        from backend.services.export import _load_study_data

        mock_session = AsyncMock()
        study_result = MagicMock()
        study_result.scalar_one_or_none.return_value = None
        extractions_result = MagicMock()
        extractions_result.scalars.return_value.all.return_value = []
        dm_result = MagicMock()
        dm_result.scalar_one_or_none.return_value = None
        charts_result = MagicMock()
        charts_result.scalars.return_value.all.return_value = []

        mock_session.execute.side_effect = [
            study_result,
            extractions_result,
            dm_result,
            charts_result,
        ]

        mock_ctx = AsyncMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_session)
        mock_ctx.__aexit__ = AsyncMock(return_value=None)

        with patch("backend.core.database._session_maker", return_value=mock_ctx):
            result = await _load_study_data(42)

        assert result["study"] == {}
        assert result["extractions"] == []
        assert result["domain_model"] == {}
        assert result["charts"] == []

    @pytest.mark.asyncio
    async def test_returns_populated_dicts_when_data_exists(self) -> None:
        """When study and domain model exist, returns populated dicts."""
        from backend.services.export import _load_study_data

        mock_session = AsyncMock()

        mock_study = MagicMock()
        mock_study.id = 1
        mock_study.name = "Test Study"
        mock_study.description = "A test"
        mock_study.status = MagicMock()
        mock_study.status.value = "active"

        study_result = MagicMock()
        study_result.scalar_one_or_none.return_value = mock_study

        mock_ext = MagicMock()
        mock_ext.id = 10
        mock_ext.candidate_paper_id = 5
        mock_ext.research_type = "empirical"
        mock_ext.venue_type = "journal"
        mock_ext.venue_name = "ICSE"
        mock_ext.author_details = []
        mock_ext.summary = "summary"
        mock_ext.open_codings = {}
        mock_ext.keywords = ["ml"]
        mock_ext.question_data = {}
        mock_ext.extraction_status = MagicMock()
        mock_ext.extraction_status.value = "validated"

        extractions_result = MagicMock()
        extractions_result.scalars.return_value.all.return_value = [mock_ext]

        mock_dm = MagicMock()
        mock_dm.id = 3
        mock_dm.version = 2
        mock_dm.concepts = []
        mock_dm.relationships = []

        dm_result = MagicMock()
        dm_result.scalar_one_or_none.return_value = mock_dm

        mock_chart = MagicMock()
        mock_chart.id = 7
        mock_chart.version = 1
        mock_chart.chart_data = {}
        mock_chart.chart_type = MagicMock()
        mock_chart.chart_type.value = "venue"

        charts_result = MagicMock()
        charts_result.scalars.return_value.all.return_value = [mock_chart]

        mock_session.execute.side_effect = [
            study_result,
            extractions_result,
            dm_result,
            charts_result,
        ]

        mock_ctx = AsyncMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_session)
        mock_ctx.__aexit__ = AsyncMock(return_value=None)

        with patch("backend.core.database._session_maker", return_value=mock_ctx):
            result = await _load_study_data(1)

        assert result["study"]["title"] == "Test Study"
        assert len(result["extractions"]) == 1
        assert result["domain_model"]["version"] == 2
        assert len(result["charts"]) == 1
        assert result["charts"][0]["chart_type"] == "venue"


# ---------------------------------------------------------------------------
# _build_json_only / _build_svg_only / _build_csv_json / _build_full_archive
# ---------------------------------------------------------------------------


_EMPTY_STUDY_DATA = {
    "study": {"id": 1, "title": "T"},
    "extractions": [],
    "domain_model": {},
    "charts": [],
}


class TestBuildFunctions:
    """Tests for the top-level build_* functions via mocked helpers."""

    @pytest.mark.asyncio
    async def test_build_json_only_returns_bytes(self) -> None:
        """_build_json_only returns UTF-8 JSON bytes with study data."""
        import json

        with patch(
            "backend.services.export._load_study_data",
            new=AsyncMock(return_value=_EMPTY_STUDY_DATA),
        ):
            from backend.services.export import _build_json_only

            result = await _build_json_only(1)

        assert isinstance(result, bytes)
        parsed = json.loads(result)
        assert parsed["study"]["title"] == "T"

    @pytest.mark.asyncio
    async def test_build_svg_only_returns_zip(self) -> None:
        """_build_svg_only returns a ZIP archive containing chart SVG files."""
        import io
        import zipfile

        with patch(
            "backend.services.export._async_load_charts_svg",
            new=AsyncMock(return_value={"venue": "<svg/>"}),
        ):
            from backend.services.export import _build_svg_only

            result = await _build_svg_only(1)

        buf = io.BytesIO(result)
        zf = zipfile.ZipFile(buf)
        assert "charts/venue.svg" in zf.namelist()

    @pytest.mark.asyncio
    async def test_build_csv_json_returns_zip(self) -> None:
        """_build_csv_json returns a ZIP archive with study.json and extractions.csv."""
        import io
        import zipfile

        with patch(
            "backend.services.export._load_study_data",
            new=AsyncMock(return_value=_EMPTY_STUDY_DATA),
        ):
            from backend.services.export import _build_csv_json

            result = await _build_csv_json(1)

        buf = io.BytesIO(result)
        zf = zipfile.ZipFile(buf)
        assert "study.json" in zf.namelist()
        assert "extractions.csv" in zf.namelist()

    @pytest.mark.asyncio
    async def test_build_full_archive_returns_zip(self) -> None:
        """_build_full_archive returns a ZIP with JSON, CSV, and SVG files."""
        import io
        import zipfile

        with patch(
            "backend.services.export._load_study_data",
            new=AsyncMock(return_value=_EMPTY_STUDY_DATA),
        ), patch(
            "backend.services.export._async_load_charts_svg",
            new=AsyncMock(return_value={"venue": "<svg/>"}),
        ):
            from backend.services.export import _build_full_archive

            result = await _build_full_archive(1)

        buf = io.BytesIO(result)
        zf = zipfile.ZipFile(buf)
        assert "study.json" in zf.namelist()
        assert "extractions.csv" in zf.namelist()
        assert "charts/venue.svg" in zf.namelist()
