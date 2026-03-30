"""FastAPI router package for the Tertiary Studies Workflow (feature 009).

All Tertiary Study routes are mounted under ``/api/v1/tertiary/`` and require
JWT authentication.  Study-membership enforcement is applied per-endpoint
via :func:`backend.core.auth.require_study_member`.

Sub-routers registered here (implemented in later phases):
- ``protocol`` — protocol CRUD and validation (Phase 3, T014–T015).
- ``seed_imports`` — seed import list and trigger (Phase 4, T021).
- ``extractions`` — extraction CRUD and AI-assist (Phase 6, T027).
- ``report`` — report generation and export (Phase 7, T037).
"""

from fastapi import APIRouter

from backend.api.v1.tertiary.extractions import router as extractions_router
from backend.api.v1.tertiary.protocol import router as protocol_router
from backend.api.v1.tertiary.report import router as report_router
from backend.api.v1.tertiary.seed_imports import router as seed_imports_router

router = APIRouter(prefix="/tertiary", tags=["tertiary"])
router.include_router(protocol_router)
router.include_router(seed_imports_router)
router.include_router(extractions_router)
router.include_router(report_router)
