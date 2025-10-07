"""API v1 router configuration."""
from fastapi import APIRouter

from .endpoints import company_router, company_v2_router, health_router, crm_router, industry_router

router = APIRouter(prefix="/v1")
router.include_router(company_router)
router.include_router(company_v2_router)
router.include_router(health_router)
router.include_router(crm_router)
router.include_router(industry_router)

__all__ = ["router"]
