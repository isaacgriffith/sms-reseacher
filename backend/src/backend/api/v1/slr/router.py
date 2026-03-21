"""SLR workflow router — aggregates all SLR sub-routers."""

from fastapi import APIRouter

from backend.api.v1.slr.grey_literature import router as grey_literature_router
from backend.api.v1.slr.inter_rater import router as inter_rater_router
from backend.api.v1.slr.phases import router as phases_router
from backend.api.v1.slr.protocol import router as protocol_router
from backend.api.v1.slr.quality import router as quality_router
from backend.api.v1.slr.report import router as report_router
from backend.api.v1.slr.synthesis import router as synthesis_router

router = APIRouter(prefix="/slr", tags=["slr"])
router.include_router(protocol_router)
router.include_router(phases_router)
router.include_router(inter_rater_router)
router.include_router(quality_router)
router.include_router(synthesis_router)
router.include_router(report_router)
router.include_router(grey_literature_router)
