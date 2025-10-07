from fastapi import APIRouter, HTTPException
from services.company_service import process_company_info
from database.queries import update_customer_info, get_customer_by_name, get_customer_by_id
from pydantic import BaseModel
from typing import Optional, Dict, Any

router = APIRouter(prefix="/api/v1")

class CompanyRequest(BaseModel):
    input_text: str

class CompanyResponse(BaseModel):
    status: str
    message: str = None
    data: dict = None
    summary: str = None
    source: str = None

class UpdateCompanyRequest(BaseModel):
    customer_id: int
    updates: Dict[str, Any]

class UpdateCompanyResponse(BaseModel):
    status: str
    message: str
    data: dict = None

@router.post("/process-company", response_model=CompanyResponse)
async def process_company(request: CompanyRequest):
    """
    处理用户输入的企业信息
    """
    try:
        result = process_company_info(request.input_text)
        return CompanyResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update-company", response_model=UpdateCompanyResponse)
async def update_company(request: UpdateCompanyRequest):
    """
    更新企业信息（用户修正数据）
    """
    try:
        # 验证customer_id是否存在
        existing_data = get_customer_by_id(request.customer_id)
        if not existing_data:
            raise HTTPException(status_code=404, detail="企业信息不存在")
        
        # 更新数据库
        success = update_customer_info(request.customer_id, request.updates)
        
        if success:
            # 重新查询更新后的数据
            updated_data = get_customer_by_id(request.customer_id)
            
            return UpdateCompanyResponse(
                status="success",
                message="企业信息更新成功",
                data=updated_data
            )
        else:
            raise HTTPException(status_code=500, detail="数据更新失败")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新企业信息时出错: {str(e)}")

@router.post("/update-chain-leader-company")
async def update_chain_leader_company(request: dict):
    """
    更新链主企业信息（用户修正数据）
    """
    try:
        company_name = request.get('company_name')
        updates = request.get('updates', {})
        
        if not company_name:
            raise HTTPException(status_code=400, detail="企业名称不能为空")
        
        if not updates:
            raise HTTPException(status_code=400, detail="更新数据不能为空")
        
        # 记录链主企业数据修正请求
        from utils.logger import city_brain_logger
        city_brain_logger.log_company_query(
            company_name,
            "链主企业数据修正",
            f"用户提交修正数据: {list(updates.keys())}"
        )
        
        # 这里可以实现具体的链主企业数据更新逻辑
        # 目前先记录到日志中，后续可以扩展为实际的数据库更新
        
        return {
            "status": "success",
            "message": f"链主企业 {company_name} 的数据修正请求已记录",
            "data": {
                "company_name": company_name,
                "updates": updates,
                "note": "链主企业数据修正已记录到系统日志中"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新链主企业信息时出错: {str(e)}")

@router.get("/health")
async def health_check():
    """
    健康检查接口
    """
    return {"status": "healthy"}