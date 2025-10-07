"""
API端点模块
"""

from .company import router as company_router
from .company_v2 import router as company_v2_router
from .health import router as health_router
from .crm import router as crm_router
from .crm_sync import router as crm_sync_router
from .industry_mapping import router as industry_router
from .enterprise_qd import router as enterprise_qd_router
from .opportunities import router as opportunities_router

__all__ = [
    "company_router",
    "company_v2_router",
    "health_router",
    "crm_router",
    "crm_sync_router",
    "industry_router",
    "enterprise_qd_router",
    "opportunities_router"
]