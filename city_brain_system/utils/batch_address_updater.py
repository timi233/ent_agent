"""
批量地址更新工具
"""
from typing import Dict, Any
from .address_updater import update_customer_address_info
from .address_extractor import search_company_address, extract_city_from_address
from utils.logger import city_brain_logger


def batch_update_addresses_from_search(companies_with_wrong_addresses: list) -> Dict[str, Any]:
    """
    批量更新有错误地址的企业信息
    
    Args:
        companies_with_wrong_addresses: 需要更新的企业列表
        
    Returns:
        Dict: 更新结果统计
    """
    results = {
        "total": len(companies_with_wrong_addresses),
        "success": 0,
        "failed": 0,
        "details": []
    }
    
    for company_name in companies_with_wrong_addresses:
        try:
            print(f"正在处理: {company_name}")
            
            # 搜索最新地址
            new_address = search_company_address(company_name)
            
            if new_address and new_address.strip():
                # 从地址中提取城市
                new_city = extract_city_from_address(new_address)
                
                if new_city:
                    # 更新到数据库
                    success = update_customer_address_info(company_name, new_address, new_city)
                    
                    if success:
                        results["success"] += 1
                        results["details"].append({
                            "company": company_name,
                            "status": "success",
                            "new_address": new_address[:100] + "..." if len(new_address) > 100 else new_address,
                            "new_city": new_city
                        })
                        print(f"✅ {company_name} -> {new_city}")
                    else:
                        results["failed"] += 1
                        results["details"].append({
                            "company": company_name,
                            "status": "failed",
                            "reason": "数据库更新失败"
                        })
                        print(f"❌ {company_name} -> 数据库更新失败")
                else:
                    results["failed"] += 1
                    results["details"].append({
                        "company": company_name,
                        "status": "failed",
                        "reason": "无法从搜索结果中提取城市信息"
                    })
                    print(f"❌ {company_name} -> 无法提取城市")
            else:
                results["failed"] += 1
                results["details"].append({
                    "company": company_name,
                    "status": "failed",
                    "reason": "搜索未找到有效地址信息"
                })
                print(f"❌ {company_name} -> 搜索无结果")
                
        except Exception as e:
            results["failed"] += 1
            results["details"].append({
                "company": company_name,
                "status": "failed",
                "reason": f"处理异常: {str(e)}"
            })
            print(f"❌ {company_name} -> 异常: {str(e)}")
    
    city_brain_logger.log_info(
        f"批量地址更新完成",
        {
            "total": results["total"],
            "success": results["success"],
            "failed": results["failed"]
        }
    )
    
    return results