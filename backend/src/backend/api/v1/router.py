"""API v1 router — assembles all sub-routers."""

from fastapi import APIRouter

from backend.api.v1 import health
from backend.api.v1.auth import router as auth_router
from backend.api.v1.groups import router as groups_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(auth_router)
api_router.include_router(groups_router)
