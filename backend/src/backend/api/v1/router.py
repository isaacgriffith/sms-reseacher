"""API v1 router — assembles all sub-routers."""

from fastapi import APIRouter

from backend.api.v1 import health
from backend.api.v1.auth import router as auth_router
from backend.api.v1.groups import router as groups_router
from backend.api.v1.studies import router as studies_router
from backend.api.v1.pico import router as pico_router
from backend.api.v1.seeds import router as seeds_router
from backend.api.v1.criteria import router as criteria_router
from backend.api.v1.search_strings import router as search_strings_router
from backend.api.v1.searches import router as searches_router
from backend.api.v1.jobs import router as jobs_router
from backend.api.v1.papers import router as papers_router
from backend.api.v1.metrics import router as metrics_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(auth_router)
api_router.include_router(groups_router)
api_router.include_router(studies_router)
api_router.include_router(pico_router)
api_router.include_router(seeds_router)
api_router.include_router(criteria_router)
api_router.include_router(search_strings_router)
api_router.include_router(searches_router)
api_router.include_router(jobs_router)
api_router.include_router(papers_router)
api_router.include_router(metrics_router)
