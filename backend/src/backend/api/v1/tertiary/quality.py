"""Quality assessment routes for Tertiary Studies (TFIX7 part 3).

``07-quality-assessment.md`` assigns **DARE** to tertiary studies, and notes the
reversal that makes it matter: "tertiary studies about SR methodology **do**
require primary-study quality assessment, unlike most mapping studies".  Until
this module existed, a tertiary study had nowhere to record one — the only
quality field it had was a single ``reviewer_quality_rating`` float hanging off
the extraction form, which the same chapter rejects as a shape.

Only one route lives here: ``POST /studies/{id}/quality-checklist/dare``, which
seeds the instrument.  Reading the checklist and submitting scores reuse the
endpoints under ``/api/v1/slr/`` — those handlers are study-scoped rather than
SLR-specific (they authorise on ``require_study_member`` alone), so a tertiary
study drives them unchanged.

Mounting a second copy of them under ``/tertiary`` was tried and removed: the
frontend calls the ``/slr`` paths, so the duplicate answered nobody.  An
endpoint no caller reaches is the same defect this feature exists to close,
and adding one to tidy a prefix would be a poor trade.  The genuine fix is to
move those routes out of the ``/slr`` prefix altogether, which breaks existing
callers and belongs in its own change.

Seeding is an explicit action rather than something that happens quietly when
the study is created.  A checklist is the study's own methodological choice,
recorded in its protocol; materialising one behind the team's back would put
questions in their report that nobody chose to ask.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.v1.slr.quality import ChecklistResponse
from backend.core.auth import CurrentUser, get_current_user, require_study_member
from backend.core.database import get_db
from backend.services.dare_instrument import seed_dare_checklist

router = APIRouter(tags=["tertiary-quality"])


@router.post(
    "/studies/{study_id}/quality-checklist/dare",
    response_model=ChecklistResponse,
    status_code=status.HTTP_200_OK,
    summary="Seed the DARE quality instrument for a Tertiary study",
)
async def seed_dare(
    study_id: int,
    include_synthesis: bool = Query(
        False,
        description=(
            "Also seed the fifth (synthesis) criterion. CRD scored it as mandatory "
            "and the SE community dropped it; scores that include it are not "
            "comparable with the out-of-4 totals SE tertiary studies report."
        ),
    ),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChecklistResponse:
    """Create the study's DARE checklist, or return the one it already has.

    Idempotent and non-destructive: a study that already has a checklist — DARE
    or one the team wrote themselves — gets it back untouched.  Overwriting
    would cascade-delete its items and every score recorded against them.

    Args:
        study_id: The Tertiary study to seed.
        include_synthesis: Seed the optional fifth question as well.
        current_user: JWT-authenticated user.
        db: Async database session.

    Returns:
        The study's :class:`ChecklistResponse`.

    Raises:
        HTTPException: 403 if the caller is not a member of the study.

    """
    await require_study_member(study_id, current_user, db)
    checklist = await seed_dare_checklist(study_id, db, include_synthesis=include_synthesis)
    return ChecklistResponse.model_validate(checklist)
