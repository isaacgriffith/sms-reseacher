"""Service layer for Evidence Briefing versioning, export, and share tokens (feature 008).

Provides functions to:
- Create a new briefing version auto-populated from the protocol and synthesis sections.
- Atomically promote a draft to published status.
- Render the Jinja2 HTML template and convert to PDF via WeasyPrint.
- Create and revoke opaque share tokens for unauthenticated public access.
- Resolve a share token to the currently published briefing.
"""

from __future__ import annotations

import secrets
from datetime import UTC, datetime
from pathlib import Path

import structlog
from db.models import Study
from db.models.rapid_review import (
    BriefingStatus,
    EvidenceBriefing,
    EvidenceBriefingShareToken,
    RRThreatToValidity,
)
from fastapi import HTTPException, status
from jinja2 import Environment, FileSystemLoader
from sqlalchemy import func as sqlfunc
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services import narrative_synthesis_service, rr_protocol_service

logger = structlog.get_logger(__name__)

_TEMPLATE_DIR = Path(__file__).parent.parent / "templates"
_jinja_env = Environment(loader=FileSystemLoader(str(_TEMPLATE_DIR)), autoescape=False)

# Add a built-in enumerate filter so templates can use {{ list | enumerate }}
_jinja_env.filters["enumerate"] = enumerate  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Core CRUD
# ---------------------------------------------------------------------------


async def get_briefings_for_study(
    study_id: int,
    db: AsyncSession,
) -> list[EvidenceBriefing]:
    """Return all briefing versions for a study ordered by version_number descending.

    Args:
        study_id: The Rapid Review study to query.
        db: Active async database session.

    Returns:
        List of :class:`EvidenceBriefing` records, newest first.

    """
    result = await db.execute(
        select(EvidenceBriefing)
        .where(EvidenceBriefing.study_id == study_id)
        .order_by(EvidenceBriefing.version_number.desc())
    )
    return list(result.scalars().all())


async def create_new_version(
    study_id: int,
    db: AsyncSession,
) -> EvidenceBriefing:
    """Create a new Evidence Briefing version for a study.

    Auto-increments ``version_number`` per study (1, 2, 3…).  Populates
    ``title``, ``summary``, ``findings``, and ``target_audience`` from the
    validated protocol and completed narrative synthesis sections.

    Args:
        study_id: The Rapid Review study to create the briefing for.
        db: Active async database session.

    Returns:
        The newly committed :class:`EvidenceBriefing` record.

    """
    bound = logger.bind(study_id=study_id)

    # Determine next version number
    max_version_result = await db.execute(
        select(sqlfunc.max(EvidenceBriefing.version_number)).where(
            EvidenceBriefing.study_id == study_id
        )
    )
    max_version: int | None = max_version_result.scalar_one_or_none()
    next_version = (max_version or 0) + 1

    # Fetch study name
    study_result = await db.execute(select(Study).where(Study.id == study_id))
    study = study_result.scalar_one_or_none()
    study_name: str = study.name if study is not None else f"Study {study_id}"

    # Fetch protocol
    protocol = await rr_protocol_service.get_or_create_protocol(study_id, db)

    # Title: prefer a protocol-derived title, fall back to study name
    title = f"Evidence Briefing: {study_name}"

    # Fetch synthesis sections
    sections = await narrative_synthesis_service.get_or_create_sections(study_id, db)

    # Summary: use the first completed section's narrative text
    summary = ""
    for section in sections:
        if section.is_complete and section.narrative_text:
            summary = section.narrative_text
            break
    if not summary:
        summary = (
            "This evidence briefing summarises findings from a Rapid Review "
            f"for the study '{study_name}'. See individual research question "
            "findings below for details."
        )

    # Findings: one entry per RQ index
    findings: dict[str, str] = {}
    for section in sections:
        findings[str(section.rq_index)] = section.narrative_text or ""

    # Target audience: generated from protocol fields
    stakeholders_text = protocol.practical_problem or "practitioners"
    target_audience = (
        f"This briefing is intended for {stakeholders_text}. "
        "It summarises evidence relevant to the stated practical problem "
        "and is designed to be accessible to non-specialist readers."
    )

    briefing = EvidenceBriefing(
        study_id=study_id,
        version_number=next_version,
        status=BriefingStatus.DRAFT,
        title=title,
        summary=summary,
        findings=findings,
        target_audience=target_audience,
        generated_at=datetime.now(UTC),
    )
    db.add(briefing)
    await db.commit()
    await db.refresh(briefing)

    bound.info("evidence_briefing_created", version=next_version, briefing_id=briefing.id)
    return briefing


async def publish_version(
    briefing_id: int,
    db: AsyncSession,
) -> EvidenceBriefing:
    """Atomically promote a briefing to PUBLISHED status.

    Demotes any currently published version for the same study to DRAFT
    before promoting the target version.

    Args:
        briefing_id: Primary key of the :class:`EvidenceBriefing` to publish.
        db: Active async database session.

    Returns:
        The updated :class:`EvidenceBriefing` with ``status=PUBLISHED``.

    Raises:
        HTTPException: 404 if the briefing is not found.

    """
    result = await db.execute(select(EvidenceBriefing).where(EvidenceBriefing.id == briefing_id))
    briefing = result.scalar_one_or_none()
    if briefing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evidence Briefing {briefing_id} not found.",
        )

    study_id = briefing.study_id

    # Demote any currently published version
    await db.execute(
        update(EvidenceBriefing)
        .where(
            EvidenceBriefing.study_id == study_id,
            EvidenceBriefing.status == BriefingStatus.PUBLISHED,
            EvidenceBriefing.id != briefing_id,
        )
        .values(status=BriefingStatus.DRAFT)
        .execution_options(synchronize_session="fetch")
    )

    # Promote target
    briefing.status = BriefingStatus.PUBLISHED
    await db.commit()
    await db.refresh(briefing)

    logger.info(
        "evidence_briefing_published",
        briefing_id=briefing_id,
        version=briefing.version_number,
        study_id=study_id,
    )
    return briefing


# ---------------------------------------------------------------------------
# HTML / PDF generation
# ---------------------------------------------------------------------------


async def generate_html(
    briefing_id: int,
    db: AsyncSession,
) -> EvidenceBriefing:
    """Render the Jinja2 HTML template and write to disk.

    Fetches the briefing, protocol threats, and research questions, then
    renders ``backend/templates/rapid/evidence_briefing.html.j2`` and
    writes the output to ``/tmp/briefings/{briefing_id}/evidence_briefing.html``.

    Args:
        briefing_id: Primary key of the :class:`EvidenceBriefing` to render.
        db: Active async database session.

    Returns:
        The updated :class:`EvidenceBriefing` with ``html_path`` set.

    Raises:
        HTTPException: 404 if the briefing is not found.

    """
    result = await db.execute(select(EvidenceBriefing).where(EvidenceBriefing.id == briefing_id))
    briefing = result.scalar_one_or_none()
    if briefing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evidence Briefing {briefing_id} not found.",
        )

    study_id = briefing.study_id

    # Fetch threats
    threats_result = await db.execute(
        select(RRThreatToValidity).where(RRThreatToValidity.study_id == study_id)
    )
    threats: list[RRThreatToValidity] = list(threats_result.scalars().all())

    # Fetch research questions from protocol
    protocol = await rr_protocol_service.get_or_create_protocol(study_id, db)
    rqs: list[str] = protocol.research_questions or []

    # Render template
    template = _jinja_env.get_template("rapid/evidence_briefing.html.j2")
    html_content = template.render(briefing=briefing, threats=threats, rqs=rqs)

    # Write to disk
    out_dir = Path(f"/tmp/briefings/{briefing_id}")
    out_dir.mkdir(parents=True, exist_ok=True)
    html_path = out_dir / "evidence_briefing.html"
    html_path.write_text(html_content, encoding="utf-8")

    briefing.html_path = str(html_path)
    await db.commit()
    await db.refresh(briefing)

    logger.info(
        "evidence_briefing_html_generated",
        briefing_id=briefing_id,
        html_path=str(html_path),
    )
    return briefing


async def generate_pdf(
    briefing_id: int,
    db: AsyncSession,
) -> EvidenceBriefing:
    """Convert the rendered HTML to PDF via WeasyPrint.

    Requires ``html_path`` to be set on the briefing (call :func:`generate_html`
    first).  Writes the PDF to
    ``/tmp/briefings/{briefing_id}/evidence_briefing.pdf``.

    Args:
        briefing_id: Primary key of the :class:`EvidenceBriefing` to convert.
        db: Active async database session.

    Returns:
        The updated :class:`EvidenceBriefing` with ``pdf_path`` set.

    Raises:
        HTTPException: 404 if the briefing is not found.
        HTTPException: 422 if ``html_path`` is not set.

    """
    import weasyprint  # type: ignore[import-untyped]  # lazy import — no stubs

    result = await db.execute(select(EvidenceBriefing).where(EvidenceBriefing.id == briefing_id))
    briefing = result.scalar_one_or_none()
    if briefing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evidence Briefing {briefing_id} not found.",
        )

    if not briefing.html_path:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Evidence Briefing {briefing_id} has no HTML path set. Call generate_html first."
            ),
        )

    out_dir = Path(f"/tmp/briefings/{briefing_id}")
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = out_dir / "evidence_briefing.pdf"

    weasyprint.HTML(filename=briefing.html_path).write_pdf(str(pdf_path))

    briefing.pdf_path = str(pdf_path)
    await db.commit()
    await db.refresh(briefing)

    logger.info(
        "evidence_briefing_pdf_generated",
        briefing_id=briefing_id,
        pdf_path=str(pdf_path),
    )
    return briefing


# ---------------------------------------------------------------------------
# Share tokens
# ---------------------------------------------------------------------------


async def create_share_token(
    briefing_id: int,
    created_by_user_id: int,
    db: AsyncSession,
) -> EvidenceBriefingShareToken:
    """Generate a new share token for the published briefing of a study.

    Raises HTTP 422 if no published version exists for the study yet.

    Args:
        briefing_id: Primary key of the :class:`EvidenceBriefing` associated
            with the token (used to look up ``study_id``).
        created_by_user_id: The user creating the token.
        db: Active async database session.

    Returns:
        The newly committed :class:`EvidenceBriefingShareToken`.

    Raises:
        HTTPException: 404 if the briefing is not found.
        HTTPException: 422 if no published version exists for the study.

    """
    result = await db.execute(select(EvidenceBriefing).where(EvidenceBriefing.id == briefing_id))
    briefing = result.scalar_one_or_none()
    if briefing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evidence Briefing {briefing_id} not found.",
        )

    study_id = briefing.study_id

    # Verify a published version exists for the study
    published_result = await db.execute(
        select(EvidenceBriefing).where(
            EvidenceBriefing.study_id == study_id,
            EvidenceBriefing.status == BriefingStatus.PUBLISHED,
        )
    )
    published = published_result.scalar_one_or_none()
    if published is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "A share token can only be created when at least one "
                "Evidence Briefing version is published for this study."
            ),
        )

    token_str = secrets.token_urlsafe(32)
    token_record = EvidenceBriefingShareToken(
        briefing_id=briefing_id,
        study_id=study_id,
        created_by_user_id=created_by_user_id,
        token=token_str,
    )
    db.add(token_record)
    await db.commit()
    await db.refresh(token_record)

    logger.info(
        "share_token_created",
        briefing_id=briefing_id,
        study_id=study_id,
        token_id=token_record.id,
    )
    return token_record


async def revoke_token(
    token: str,
    db: AsyncSession,
) -> None:
    """Revoke a share token by setting ``revoked_at``.

    Args:
        token: The raw token string to revoke.
        db: Active async database session.

    Raises:
        HTTPException: 404 if the token is not found.

    """
    result = await db.execute(
        select(EvidenceBriefingShareToken).where(EvidenceBriefingShareToken.token == token)
    )
    token_record = result.scalar_one_or_none()
    if token_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Share token not found.",
        )

    token_record.revoked_at = datetime.now(UTC)
    await db.commit()
    logger.info("share_token_revoked", token_id=token_record.id)


async def resolve_token(
    token: str,
    db: AsyncSession,
) -> EvidenceBriefing:
    """Validate a share token and return the currently published briefing.

    A token is valid if ``revoked_at IS NULL`` and either ``expires_at IS NULL``
    or ``expires_at`` is in the future.  Resolves to the currently published
    briefing for the study (not the specific version recorded on the token).

    Args:
        token: The raw share token string from the URL.
        db: Active async database session.

    Returns:
        The currently published :class:`EvidenceBriefing` for the study.

    Raises:
        HTTPException: 404 if the token is invalid, revoked, expired, or no
            published briefing exists for the study.

    """
    now = datetime.now(UTC)

    result = await db.execute(
        select(EvidenceBriefingShareToken).where(
            EvidenceBriefingShareToken.token == token,
            EvidenceBriefingShareToken.revoked_at.is_(None),
        )
    )
    token_record = result.scalar_one_or_none()

    if token_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Share token not found, revoked, or expired.",
        )

    if token_record.expires_at is not None and token_record.expires_at <= now:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Share token has expired.",
        )

    # Resolve to the currently published briefing for the study
    briefing_result = await db.execute(
        select(EvidenceBriefing).where(
            EvidenceBriefing.study_id == token_record.study_id,
            EvidenceBriefing.status == BriefingStatus.PUBLISHED,
        )
    )
    briefing = briefing_result.scalar_one_or_none()
    if briefing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No published Evidence Briefing found for this study.",
        )

    return briefing
