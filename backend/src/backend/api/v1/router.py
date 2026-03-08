"""API v1 router — assembles all sub-routers."""

from fastapi import APIRouter

from backend.api.v1 import health

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
