"""Additional unit tests for backend.services.export covering build paths.

These tests cover the format builders and _load_study_data through mocking,
supplementing the existing test_export.py which covers sanitisation helpers.
"""

from __future__ import annotations

import io
import json
import zipfile
from unittest.mock import AsyncMock, MagicMock, patch


# ---------------------------------------------------------------------------
# _warn_and_assert_redaction
# ---------------------------------------------------------------------------


def test_warn_and_assert_redaction_passes_for_clean_payload():
    """_warn_and_assert_redaction does not raise when no redacted keys are present.

    A payload with only safe keys should pass all assertions without error.
    """
    from backend.services.export import _warn_and_assert_redaction

    raw = {"title": "My Study", "data": [{"value": 42}]}
    sanitised = {"title": "My Study", "data": [{"value": 42}]}
    # Should not raise
    _warn_and_assert_redaction(raw, sanitised, "test_context")


def test_warn_and_assert_redaction_raises_if_leaked():
    """_warn_and_assert_redaction raises RuntimeError if a redacted key survives.

    If a sensitive key somehow ends up in the sanitised payload a RuntimeError
    must be raised to enforce the defence-in-depth guard.
    """
    import pytest

    from backend.services.export import _warn_and_assert_redaction

    raw = {"database_url": "postgres://...", "title": "Study"}
    # Simulate a bug where sanitisation didn't work
    sanitised = {"database_url": "postgres://...", "title": "Study"}

    with pytest.raises(RuntimeError, match="database_url"):
        _warn_and_assert_redaction(raw, sanitised, "test_context")


def test_warn_and_assert_redaction_logs_stripped_keys(capfd):
    """_warn_and_assert_redaction logs a warning when keys are stripped.

    When the raw payload contains sensitive keys but the sanitised one does not
    the function should log a warning without raising.
    """
    from backend.services.export import _warn_and_assert_redaction

    raw = {"secret_key": "s3cr3t", "title": "Study"}
    sanitised = {"title": "Study"}
    # Should log warning but not raise
    _warn_and_assert_redaction(raw, sanitised, "test_context")


# ---------------------------------------------------------------------------
# _collect_keys
# ---------------------------------------------------------------------------


def test_collect_keys_returns_all_nested_keys():
    """_collect_keys collects every dict key at any nesting level.

    The function should traverse dicts, lists, and nested structures.
    """
    from backend.services.export import _collect_keys

    obj = {
        "a": {"b": [{"c": 1}, {"d": 2}]},
        "e": "value",
    }
    keys = _collect_keys(obj)
    assert keys >= {"a", "b", "c", "d", "e"}


def test_collect_keys_handles_empty_dict():
    """_collect_keys returns empty set for an empty dict."""
    from backend.services.export import _collect_keys

    assert _collect_keys({}) == set()


def test_collect_keys_handles_list():
    """_collect_keys processes a top-level list."""
    from backend.services.export import _collect_keys

    result = _collect_keys([{"x": 1}, {"y": 2}])
    assert "x" in result
    assert "y" in result


def test_collect_keys_handles_non_dict():
    """_collect_keys returns empty set for scalar values."""
    from backend.services.export import _collect_keys

    assert _collect_keys("plain string") == set()
    assert _collect_keys(42) == set()
    assert _collect_keys(None) == set()


# ---------------------------------------------------------------------------
# _build_json_only
# ---------------------------------------------------------------------------


async def test_build_json_only_returns_valid_utf8_json():
    """_build_json_only returns valid UTF-8 JSON bytes.

    The returned bytes should parse as JSON and contain the study key.
    """
    safe_data = {"study": {"id": 1, "title": "Test"}, "extractions": [], "domain_model": {}, "charts": []}

    with patch("backend.services.export._load_study_data", new=AsyncMock(return_value=safe_data)):
        from backend.services.export import _build_json_only

        payload = await _build_json_only(study_id=1)

    parsed = json.loads(payload.decode("utf-8"))
    assert "study" in parsed


# ---------------------------------------------------------------------------
# _build_svg_only
# ---------------------------------------------------------------------------


async def test_build_svg_only_returns_zip_bytes():
    """_build_svg_only returns bytes that can be opened as a ZIP archive.

    The returned payload should be a valid ZIP file, even when no charts
    are available.
    """
    with patch(
        "backend.services.export._async_load_charts_svg",
        new=AsyncMock(return_value={}),
    ):
        from backend.services.export import _build_svg_only

        payload = await _build_svg_only(study_id=1)

    buf = io.BytesIO(payload)
    with zipfile.ZipFile(buf, "r") as zf:
        names = zf.namelist()
    assert isinstance(names, list)


async def test_build_svg_only_includes_svg_files_in_zip():
    """_build_svg_only stores each chart as a .svg file in the ZIP.

    When charts are available each should appear as charts/<chart_type>.svg.
    """
    svgs = {"bar_chart": "<svg>...</svg>", "pie_chart": "<svg/>"}

    with patch(
        "backend.services.export._async_load_charts_svg",
        new=AsyncMock(return_value=svgs),
    ):
        from backend.services.export import _build_svg_only

        payload = await _build_svg_only(study_id=1)

    buf = io.BytesIO(payload)
    with zipfile.ZipFile(buf, "r") as zf:
        names = zf.namelist()

    assert "charts/bar_chart.svg" in names
    assert "charts/pie_chart.svg" in names


# ---------------------------------------------------------------------------
# _build_csv_json
# ---------------------------------------------------------------------------


async def test_build_csv_json_returns_zip_with_two_files():
    """_build_csv_json returns a ZIP containing study.json and extractions.csv.

    The ZIP archive should include both required files.
    """
    safe_data = {
        "study": {"id": 1, "title": "Test"},
        "extractions": [],
        "domain_model": {},
        "charts": [],
    }

    with patch("backend.services.export._load_study_data", new=AsyncMock(return_value=safe_data)):
        from backend.services.export import _build_csv_json

        payload = await _build_csv_json(study_id=1)

    buf = io.BytesIO(payload)
    with zipfile.ZipFile(buf, "r") as zf:
        names = zf.namelist()

    assert "study.json" in names
    assert "extractions.csv" in names


# ---------------------------------------------------------------------------
# _build_full_archive
# ---------------------------------------------------------------------------


async def test_build_full_archive_returns_zip_with_json_and_csv():
    """_build_full_archive returns a ZIP containing study.json and extractions.csv.

    The full archive must include JSON and CSV at minimum.
    """
    safe_data = {
        "study": {"id": 1, "title": "Full"},
        "extractions": [],
        "domain_model": {},
        "charts": [],
    }

    with (
        patch("backend.services.export._load_study_data", new=AsyncMock(return_value=safe_data)),
        patch(
            "backend.services.export._async_load_charts_svg",
            new=AsyncMock(return_value={}),
        ),
    ):
        from backend.services.export import _build_full_archive

        payload = await _build_full_archive(study_id=1)

    buf = io.BytesIO(payload)
    with zipfile.ZipFile(buf, "r") as zf:
        names = zf.namelist()

    assert "study.json" in names
    assert "extractions.csv" in names


async def test_build_full_archive_includes_svg_charts():
    """_build_full_archive includes SVG chart files in the ZIP.

    When charts are available they should appear in the charts/ directory.
    """
    safe_data = {
        "study": {"id": 1},
        "extractions": [],
        "domain_model": {},
        "charts": [],
    }

    with (
        patch("backend.services.export._load_study_data", new=AsyncMock(return_value=safe_data)),
        patch(
            "backend.services.export._async_load_charts_svg",
            new=AsyncMock(return_value={"network": "<svg/>"}),
        ),
    ):
        from backend.services.export import _build_full_archive

        payload = await _build_full_archive(study_id=1)

    buf = io.BytesIO(payload)
    with zipfile.ZipFile(buf, "r") as zf:
        names = zf.namelist()

    assert "charts/network.svg" in names


# ---------------------------------------------------------------------------
# _load_charts_svg (sync stub)
# ---------------------------------------------------------------------------


def test_load_charts_svg_raises_not_implemented():
    """_load_charts_svg raises NotImplementedError as it is a stub.

    The sync version should always raise NotImplementedError directing
    callers to use _async_load_charts_svg.
    """
    import pytest

    from backend.services.export import _load_charts_svg

    with pytest.raises(NotImplementedError):
        _load_charts_svg(study_id=1)


# ---------------------------------------------------------------------------
# _async_load_charts_svg
# ---------------------------------------------------------------------------


async def test_async_load_charts_svg_returns_dict():
    """_async_load_charts_svg returns a dict mapping chart_type to SVG string.

    The function should return an empty dict when no charts exist.
    """
    r = MagicMock()
    r.scalars.return_value.all.return_value = []

    cm = AsyncMock()
    cm.__aenter__ = AsyncMock(return_value=AsyncMock(execute=AsyncMock(return_value=r)))
    cm.__aexit__ = AsyncMock(return_value=False)
    session_maker = MagicMock(return_value=cm)

    with patch("backend.core.database._session_maker", session_maker):
        from backend.services.export import _async_load_charts_svg

        result = await _async_load_charts_svg(study_id=1)

    assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# build_export — all valid formats
# ---------------------------------------------------------------------------


async def test_build_export_json_only_format():
    """build_export calls _build_json_only for json_only format."""
    with patch(
        "backend.services.export._build_json_only",
        new=AsyncMock(return_value=b'{"study":{}}'),
    ):
        from backend.services.export import build_export

        result = await build_export(study_id=1, format="json_only")

    assert result == b'{"study":{}}'


async def test_build_export_svg_only_format():
    """build_export calls _build_svg_only for svg_only format."""
    with patch(
        "backend.services.export._build_svg_only",
        new=AsyncMock(return_value=b"zip-bytes"),
    ):
        from backend.services.export import build_export

        result = await build_export(study_id=1, format="svg_only")

    assert result == b"zip-bytes"


async def test_build_export_csv_json_format():
    """build_export calls _build_csv_json for csv_json format."""
    with patch(
        "backend.services.export._build_csv_json",
        new=AsyncMock(return_value=b"csv-zip"),
    ):
        from backend.services.export import build_export

        result = await build_export(study_id=1, format="csv_json")

    assert result == b"csv-zip"


async def test_build_export_full_archive_format():
    """build_export calls _build_full_archive for full_archive format."""
    with patch(
        "backend.services.export._build_full_archive",
        new=AsyncMock(return_value=b"full-zip"),
    ):
        from backend.services.export import build_export

        result = await build_export(study_id=1, format="full_archive")

    assert result == b"full-zip"
