from fastapi import APIRouter, Query
from typing import Optional, Dict, Any
from infrastructure.database.repositories.industry_mapping_repository import IndustryMappingRepository
from infrastructure.utils.address_processor import search_city_by_company_name

router = APIRouter(tags=["industry"])

@router.get("/industry/brain-chain")
def get_brain_chain(
    company_name: str = Query(..., description="企业名称"),
    region: Optional[str] = Query(None, description="企业所在地区（可选）"),
    industry: Optional[str] = Query(None, description="企业行业（可选）")
) -> Dict[str, Any]:
    """
    根据企业名称优先解析地区，再按地区匹配产业大脑、按行业匹配产业链。
    优先使用传入的 region/industry；若缺失，尝试从地址解析模块获取地区，从现有详情中获取行业。
    """
    repo = IndustryMappingRepository()

    # 若未提供地区，尝试通过企业名称检索（使用已有地址解析模块）
    if not region:
        try:
            region = search_city_by_company_name(company_name, update_database=False)
        except Exception:
            region = None

    # TODO: 若未提供行业，可考虑从已有公司详情（customer/enterprise）中补充，这里先保留 industry 为空
    data = repo.find_brain_chain(company_name=company_name, region=region, industry=industry)

    return {
        "status": "success",
        "data": data
    }

@router.get("/industry/brain-chain/health")
def get_brain_chain_health():
    """
    健康检查：用于确认接口可用、数据库连接存在
    """
    try:
        repo = IndustryMappingRepository()
        # 简单尝试取一个不存在地区的空查询，确认不抛异常
        _ = repo.find_brain_chain(company_name="测试企业", region=None, industry=None)
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "error", "message": str(e)}