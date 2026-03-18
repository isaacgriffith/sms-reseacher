"""API v1 router — assembles all sub-routers."""

from fastapi import APIRouter

from backend.api.v1 import health
from backend.api.v1.admin import router as admin_router
from backend.api.v1.audit import router as audit_router
from backend.api.v1.auth import router as auth_router
from backend.api.v1.criteria import router as criteria_router
from backend.api.v1.extractions import router as extractions_router
from backend.api.v1.groups import router as groups_router
from backend.api.v1.jobs import router as jobs_router
from backend.api.v1.me.password import router as me_password_router
from backend.api.v1.me.preferences import router as me_preferences_router
from backend.api.v1.me.totp import router as me_totp_router
from backend.api.v1.metrics import router as metrics_router
from backend.api.v1.openapi_route import router as openapi_router
from backend.api.v1.paper_markdown import router as paper_markdown_router
from backend.api.v1.papers import router as papers_router
from backend.api.v1.pico import router as pico_router
from backend.api.v1.quality import router as quality_router
from backend.api.v1.results import router as results_router
from backend.api.v1.search_strings import router as search_strings_router
from backend.api.v1.searches import router as searches_router
from backend.api.v1.seeds import router as seeds_router
from backend.api.v1.studies import router as studies_router
from backend.api.v1.studies.database_selection import router as database_selection_router
from backend.api.v1.validity import router as validity_router

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
api_router.include_router(extractions_router)
api_router.include_router(results_router)
api_router.include_router(quality_router)
api_router.include_router(validity_router)
api_router.include_router(audit_router)
api_router.include_router(admin_router)
api_router.include_router(me_password_router, prefix="/me")
api_router.include_router(me_preferences_router, prefix="/me")
api_router.include_router(me_totp_router, prefix="/me")
api_router.include_router(openapi_router)
api_router.include_router(database_selection_router)
api_router.include_router(paper_markdown_router)
