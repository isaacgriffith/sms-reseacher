"""FastAPI router package for unauthenticated public endpoints (feature 008).

Routes in this package do NOT require JWT authentication.  They are mounted
under ``/api/v1/public/`` and are accessible without a bearer token.

Currently provides:
- ``briefings`` — public Evidence Briefing access via share tokens.

Security note: access control is enforced by the token mechanism rather
than by standard JWT middleware.  Each token is cryptographically random
and revocable by any study team member.
"""

from fastapi import APIRouter

from backend.api.v1.public.briefings import router as briefings_router

router = APIRouter(prefix="/public", tags=["public"])
router.include_router(briefings_router)
