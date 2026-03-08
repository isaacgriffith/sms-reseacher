"""Export service: builds study export payloads in multiple formats."""

from __future__ import annotations

import csv
import io
import json
import zipfile
from typing import TYPE_CHECKING, Any

from backend.core.config import get_logger

logger = get_logger(__name__)

# Fields derived from Settings that must never appear in exported payloads.
_REDACTED_FIELDS: frozenset[str] = frozenset(
    {"database_url", "secret_key", "anthropic_api_key", "redis_url"}
)

if TYPE_CHECKING:
    pass


async def build_export(study_id: int, format: str) -> bytes:
    """Build an export payload for the given study and format.

    Supported formats:
    - ``svg_only``: ZIP archive containing all generated SVG chart files.
    - ``json_only``: Single JSON file with full study data.
    - ``csv_json``: ZIP containing tabular CSV of extractions + full JSON.
    - ``full_archive``: ZIP containing all SVGs, CSV, and JSON.

    Args:
        study_id: The study to export.
        format: One of ``svg_only``, ``json_only``, ``csv_json``,
            ``full_archive``.

    Returns:
        Raw bytes of the export payload (ZIP or JSON).

    Raises:
        ValueError: If the format is not recognised.
    """
    builders = {
        "svg_only": _build_svg_only,
        "json_only": _build_json_only,
        "csv_json": _build_csv_json,
        "full_archive": _build_full_archive,
    }
    builder = builders.get(format)
    if builder is None:
        raise ValueError(f"Unknown export format: {format!r}. Expected one of {list(builders)}")
    return await builder(study_id)


async def _load_study_data(study_id: int) -> dict[str, Any]:
    """Load all study data needed for export from the database.

    Args:
        study_id: Study to load.

    Returns:
        A dict with keys ``study``, ``extractions``, ``domain_model``,
        ``charts``.  Settings-derived values are excluded.
    """
    from sqlalchemy import select

    from backend.core.database import _session_maker  # noqa: PLC2701 — internal
    from db.models import Study
    from db.models.candidate import CandidatePaper, CandidatePaperStatus
    from db.models.extraction import DataExtraction, ExtractionStatus
    from db.models.results import ClassificationScheme, DomainModel

    async with _session_maker() as db:
        study_result = await db.execute(select(Study).where(Study.id == study_id))
        study = study_result.scalar_one_or_none()

        extractions_result = await db.execute(
            select(DataExtraction)
            .join(CandidatePaper, CandidatePaper.id == DataExtraction.candidate_paper_id)
            .where(
                CandidatePaper.study_id == study_id,
                CandidatePaper.current_status == CandidatePaperStatus.ACCEPTED,
                DataExtraction.extraction_status.in_(
                    [
                        ExtractionStatus.AI_COMPLETE,
                        ExtractionStatus.VALIDATED,
                        ExtractionStatus.HUMAN_REVIEWED,
                    ]
                ),
            )
        )
        extractions = extractions_result.scalars().all()

        dm_result = await db.execute(
            select(DomainModel)
            .where(DomainModel.study_id == study_id)
            .order_by(DomainModel.version.desc())
            .limit(1)
        )
        domain_model = dm_result.scalar_one_or_none()

        charts_result = await db.execute(
            select(ClassificationScheme)
            .where(ClassificationScheme.study_id == study_id)
            .order_by(ClassificationScheme.chart_type)
        )
        charts = charts_result.scalars().all()

    study_dict: dict[str, Any] = {}
    if study:
        study_dict = {
            "id": study.id,
            "title": study.title,
            "description": study.description,
            "status": study.status.value if study.status else None,
        }

    extraction_list = [
        {
            "id": e.id,
            "candidate_paper_id": e.candidate_paper_id,
            "research_type": e.research_type,
            "venue_type": e.venue_type,
            "venue_name": e.venue_name,
            "author_details": e.author_details,
            "summary": e.summary,
            "open_codings": e.open_codings,
            "keywords": e.keywords,
            "question_data": e.question_data,
            "extraction_status": e.extraction_status.value if e.extraction_status else None,
        }
        for e in extractions
    ]

    dm_dict: dict[str, Any] = {}
    if domain_model:
        dm_dict = {
            "id": domain_model.id,
            "version": domain_model.version,
            "concepts": domain_model.concepts,
            "relationships": domain_model.relationships,
        }

    charts_list = [
        {
            "id": c.id,
            "chart_type": c.chart_type.value if c.chart_type else None,
            "version": c.version,
            "chart_data": c.chart_data,
        }
        for c in charts
    ]

    return {
        "study": study_dict,
        "extractions": extraction_list,
        "domain_model": dm_dict,
        "charts": charts_list,
    }


def _load_charts_svg(study_id: int) -> dict[str, str]:
    """Return SVG content keyed by chart_type for a study (sync helper).

    This function re-uses the async session inside the caller's event loop
    via the async helper below.

    Args:
        study_id: Study to load SVGs for.

    Returns:
        Dict mapping chart_type string to SVG string.
    """
    raise NotImplementedError("use _async_load_charts_svg instead")


async def _async_load_charts_svg(study_id: int) -> dict[str, str]:
    """Return SVG content keyed by chart_type for a study.

    Args:
        study_id: Study to load SVGs for.

    Returns:
        Dict mapping chart_type string to SVG string.
    """
    from sqlalchemy import select

    from backend.core.database import _session_maker  # noqa: PLC2701 — internal
    from db.models.results import ClassificationScheme

    async with _session_maker() as db:
        result = await db.execute(
            select(ClassificationScheme).where(ClassificationScheme.study_id == study_id)
        )
        charts = result.scalars().all()

    return {
        c.chart_type.value: (c.svg_content or "")
        for c in charts
        if c.svg_content
    }


def _sanitise_payload(obj: Any) -> Any:
    """Recursively remove any dict keys that match _REDACTED_FIELDS.

    Args:
        obj: Arbitrary JSON-serialisable value.

    Returns:
        The sanitised value with sensitive keys removed.
    """
    if isinstance(obj, dict):
        return {
            k: _sanitise_payload(v)
            for k, v in obj.items()
            if k not in _REDACTED_FIELDS
        }
    if isinstance(obj, list):
        return [_sanitise_payload(item) for item in obj]
    return obj


def _warn_and_assert_redaction(raw: Any, sanitised: Any, context: str) -> None:
    """Warn if sensitive keys were present and assert none remain post-sanitisation.

    Emits a structlog warning for each stripped key, then raises ``RuntimeError``
    if any ``_REDACTED_FIELDS`` key is still detectable in the sanitised payload.
    This is a defence-in-depth guard against accidental re-introduction of sensitive
    fields (FR-046 / NFR-003).

    Args:
        raw: The un-sanitised payload (used to detect what was stripped).
        sanitised: The sanitised payload to assert is clean.
        context: A label identifying which export function called this (for logging).

    Raises:
        RuntimeError: If any ``_REDACTED_FIELDS`` key survives sanitisation.
    """
    raw_keys = _collect_keys(raw)
    stripped = raw_keys & _REDACTED_FIELDS
    if stripped:
        logger.warning(
            "build_export: redacted settings keys from export",
            context=context,
            keys=sorted(stripped),
        )
    leaked = _collect_keys(sanitised) & _REDACTED_FIELDS
    if leaked:
        raise RuntimeError(
            f"export.{context}: settings field(s) {sorted(leaked)} survived sanitisation"
        )


async def _build_json_only(study_id: int) -> bytes:
    """Build a JSON-only export payload.

    Args:
        study_id: Study to export.

    Returns:
        UTF-8 encoded JSON bytes.
    """
    data = await _load_study_data(study_id)
    sanitised = _sanitise_payload(data)
    _warn_and_assert_redaction(data, sanitised, "json_only")
    return json.dumps(sanitised, default=str, indent=2).encode("utf-8")


def _collect_keys(obj: Any) -> set[str]:
    """Recursively collect all dict keys from a nested structure.

    Args:
        obj: Arbitrary JSON-serialisable value.

    Returns:
        Set of all string keys encountered.
    """
    keys: set[str] = set()
    if isinstance(obj, dict):
        keys.update(obj.keys())
        for v in obj.values():
            keys.update(_collect_keys(v))
    elif isinstance(obj, list):
        for item in obj:
            keys.update(_collect_keys(item))
    return keys


async def _build_svg_only(study_id: int) -> bytes:
    """Build a ZIP archive containing all generated SVG charts.

    Args:
        study_id: Study to export.

    Returns:
        ZIP bytes.
    """
    svgs = await _async_load_charts_svg(study_id)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for chart_type, svg_content in svgs.items():
            zf.writestr(f"charts/{chart_type}.svg", svg_content.encode("utf-8"))
    return buf.getvalue()


async def _build_csv_json(study_id: int) -> bytes:
    """Build a ZIP archive with a tabular CSV of extractions plus full JSON.

    Args:
        study_id: Study to export.

    Returns:
        ZIP bytes.
    """
    data = await _load_study_data(study_id)
    sanitised = _sanitise_payload(data)
    _warn_and_assert_redaction(data, sanitised, "csv_json")

    json_bytes = json.dumps(sanitised, default=str, indent=2).encode("utf-8")
    csv_bytes = _extractions_to_csv(sanitised.get("extractions", []))

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("study.json", json_bytes)
        zf.writestr("extractions.csv", csv_bytes)
    return buf.getvalue()


def _extractions_to_csv(extractions: list[dict[str, Any]]) -> bytes:
    """Serialise a list of extraction dicts to CSV bytes.

    Args:
        extractions: List of extraction dicts.

    Returns:
        UTF-8 CSV bytes.
    """
    if not extractions:
        return b"id,candidate_paper_id,research_type,venue_type,venue_name,extraction_status\n"

    fieldnames = [
        "id",
        "candidate_paper_id",
        "research_type",
        "venue_type",
        "venue_name",
        "extraction_status",
        "summary",
        "keywords",
    ]
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for ext in extractions:
        row = dict(ext)
        # Flatten list fields for CSV
        if isinstance(row.get("keywords"), list):
            row["keywords"] = "; ".join(row["keywords"])
        writer.writerow(row)
    return buf.getvalue().encode("utf-8")


async def _build_full_archive(study_id: int) -> bytes:
    """Build a full ZIP archive with all SVGs, CSV, and JSON.

    Args:
        study_id: Study to export.

    Returns:
        ZIP bytes.
    """
    data = await _load_study_data(study_id)
    sanitised = _sanitise_payload(data)
    _warn_and_assert_redaction(data, sanitised, "full_archive")
    svgs = await _async_load_charts_svg(study_id)

    json_bytes = json.dumps(sanitised, default=str, indent=2).encode("utf-8")
    csv_bytes = _extractions_to_csv(sanitised.get("extractions", []))

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("study.json", json_bytes)
        zf.writestr("extractions.csv", csv_bytes)
        for chart_type, svg_content in svgs.items():
            zf.writestr(f"charts/{chart_type}.svg", svg_content.encode("utf-8"))
    return buf.getvalue()
