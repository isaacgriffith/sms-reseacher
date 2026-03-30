"""FastAPI router package for the Rapid Review workflow (feature 008).

All Rapid Review routes are mounted under ``/api/v1/rapid/`` and require
JWT authentication.  Study-membership enforcement is applied per-endpoint
via :func:`backend.core.auth.require_study_member`.

Sub-routers added here as they are implemented:
- ``protocol`` — protocol CRUD and validation.
- ``stakeholders`` — practitioner stakeholder CRUD.
- ``threats`` — threat-to-validity read-only listing.
- ``search_config`` — search restriction and single-reviewer mode.
- ``quality`` — quality appraisal mode selection.
- ``synthesis`` — narrative synthesis sections and AI drafting.
- ``briefing`` — Evidence Briefing versioning, export, and share tokens.
"""

from fastapi import APIRouter

from backend.api.v1.rapid.briefing import router as briefing_router
from backend.api.v1.rapid.protocol import router as protocol_router
from backend.api.v1.rapid.quality import router as quality_router
from backend.api.v1.rapid.search_config import router as search_config_router
from backend.api.v1.rapid.stakeholders import router as stakeholders_router
from backend.api.v1.rapid.synthesis import router as synthesis_router
from backend.api.v1.rapid.threats import router as threats_router

router = APIRouter(prefix="/rapid", tags=["rapid-review"])
router.include_router(protocol_router)
router.include_router(stakeholders_router)
router.include_router(threats_router)
router.include_router(search_config_router)
router.include_router(quality_router)
router.include_router(synthesis_router)
router.include_router(briefing_router)
