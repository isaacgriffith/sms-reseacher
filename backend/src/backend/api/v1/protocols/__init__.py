"""Protocol API router package for Research Protocol Definition (feature 010)."""

from __future__ import annotations

from fastapi import APIRouter

from backend.api.v1.protocols.assignment import router as assignment_router
from backend.api.v1.protocols.execution_state import router as execution_state_router
from backend.api.v1.protocols.library import router as library_router

router = APIRouter()
router.include_router(library_router)
router.include_router(assignment_router)
router.include_router(execution_state_router)
