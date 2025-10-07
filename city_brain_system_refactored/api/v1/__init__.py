"""API v1 router configuration."""
from fastapi import APIRouter

from .endpoints import (
    company_router,
    company_v2_router,
    health_router,
    crm_router,
    crm_sync_router,
    industry_router,
    enterprise_qd_router,
    opportunities_router
)

router = APIRouter(prefix="/v1")
router.include_router(company_router)
router.include_router(company_v2_router)
router.include_router(health_router)
router.include_router(crm_router)
router.include_router(crm_sync_router, prefix="/crm-sync", tags=["crm-sync"])
router.include_router(industry_router)
router.include_router(enterprise_qd_router, prefix="/enterprise-qd", tags=["enterprise-qd"])
router.include_router(opportunities_router, prefix="/opportunities", tags=["opportunities"])

__all__ = ["router"]
