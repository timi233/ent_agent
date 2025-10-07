"""
API端点模块
"""

from .company import router as company_router
from .company_v2 import router as company_v2_router
from .health import router as health_router
from .crm import router as crm_router
from .industry_mapping import router as industry_router

__all__ = ["company_router", "company_v2_router", "health_router", "crm_router", "industry_router"]