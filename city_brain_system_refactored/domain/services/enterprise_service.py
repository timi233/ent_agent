"""
企业服务主逻辑 - 协调各个服务完成企业信息处理（重构版）

负责：
- 企业信息处理的主要业务流程控制
- 协调搜索服务、数据增强服务、分析服务
- 处理有本地数据和无本地数据的不同情况
- 统一的错误处理和结果返回

重构改进（Day 1-4）：
- Day1-2: 使用构造函数依赖注入，符合依赖倒置原则
- Day1-2: 通过Repository接口访问数据，而非直接调用standalone_queries
- Day3-4: 使用领域模型替代Dict，提升类型安全
"""

import sys
import os
import logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from .search_service import SearchService
from .data_enhancement_service import DataEnhancementService
from .analysis_service import AnalysisService
from ..models.enterprise import (
    EnterpriseBasicInfo,
    EnterpriseNewsInfo,
    EnterpriseComprehensiveInfo,
    DataSource
)


logger = logging.getLogger(__name__)

class EnterpriseService:
    """企业服务主逻辑类（使用依赖注入）"""

    def __init__(
        self,
        search_service: SearchService,
        data_enhancement_service: DataEnhancementService,
        analysis_service: AnalysisService,
        customer_repository
    ):
        """
        初始化企业服务（通过构造函数注入依赖）

        Args:
            search_service: 搜索服务
            data_enhancement_service: 数据增强服务
            analysis_service: 分析服务
            customer_repository: 客户Repository（ICustomerRepository接口）
        """
        self.search_service = search_service
        self.data_enhancement_service = data_enhancement_service
        self.analysis_service = analysis_service
        self.customer_repository = customer_repository
    
    def process_company_info(self, user_input):
        """
        处理用户输入的企业信息
        
        Args:
            user_input (str): 用户输入的企业信息
            
        Returns:
            dict: 处理结果，包含企业信息和分析报告
        """
        try:
            # 1. 提取公司名称
            name_extraction_result = self.search_service.extract_company_name_from_input(user_input)
            
            if name_extraction_result['status'] == 'error':
                return name_extraction_result
            
            company_name = name_extraction_result['name']
            is_complete = name_extraction_result['is_complete']

            # 2. 查询本地数据库（通过Repository接口）
            local_data = self.customer_repository.find_by_name(company_name)
            if not local_data and is_complete:
                # 如果完整名称没找到，尝试用原始提取的名称查询
                if name_extraction_result.get('source') in ['search_completion', 'search_inference']:
                    # 如果是通过搜索获得的完整名称，可能需要用更简短的名称查询
                    # 这里可以进一步优化查询策略
                    pass
            
            if local_data:
                # 存在本地数据
                return self.process_with_local_data(local_data)
            else:
                # 不存在本地数据
                return self.process_without_local_data(company_name)
                
        except Exception as e:
            logger.error(f"处理企业信息时出错: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"处理企业信息时出错: {str(e)}"
            }
    
    def process_with_local_data(self, local_data):
        """
        处理存在本地数据的情况 - 分阶段返回数据
        
        Args:
            local_data (dict): 本地数据库中的企业数据
            
        Returns:
            dict: 处理结果
        """
        try:
            # 第一阶段：数据增强
            enhanced_data = self.data_enhancement_service.enhance_all_data(local_data)
            
            # 第二阶段：获取企业新闻
            company_name = enhanced_data.get('customer_name', '')
            news_data = self.analysis_service.get_company_news(company_name)
            
            # 数据库同步
            self.data_enhancement_service.sync_database_updates(enhanced_data, local_data)
            
            # 使用LLM进行最终分析
            llm_analysis = self.analysis_service.generate_comprehensive_company_analysis(
                enhanced_data, news_data
            )
            
            # 返回完整结果
            result = self.analysis_service.format_analysis_result(
                enhanced_data, news_data, llm_analysis
            )
            
            return result
            
        except Exception as e:
            logger.error(f"处理本地数据时出错: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"处理本地数据时出错: {str(e)}"
            }
    
    def process_without_local_data(self, company_name):
        """
        处理不存在本地数据的情况
        - 标准化公司名
        - 解析搜索结果尽量填充基础信息
        """
        try:
            from infrastructure.utils.text_processor import company_name_extractor, search_result_processor, get_company_industry
            import re

            norm_name = company_name_extractor.normalize_company_name(company_name)
            search_result = self.search_service.search_company_info(norm_name)

            # 默认增强数据
            enhanced = {
                "customer_name": norm_name,
                "district_name": "",
                "address": "",
                "industry_name": "",
                "brain_name": "",
                "chain_status": "",
                "revenue_info": "暂无营收数据",
                "company_status": "暂无排名信息",
                "data_source": "unknown",
            }

            if search_result.get("status") == "success":
                data = search_result.get("data", {}) or {}
                parsed = search_result_processor.extract_company_info_from_search_results({"data": data})

                # 先标准化并移除常见噪声后缀
                cleaned_name = company_name_extractor.normalize_company_name(parsed.get("name") or norm_name)
                cleaned_name = re.sub(r"(企业信息|电话|公司地址|品牌网)(?:$|[-—·|])", "", cleaned_name)
                # 提取核心企业名，避免后缀污染
                # 提取核心企业名（extract_company_name 返回字典，需取 'name'）
                _res1 = company_name_extractor.extract_company_name(cleaned_name)
                _res2 = company_name_extractor.extract_company_name(norm_name)
                core_name = (_res1.get('name') if isinstance(_res1, dict) else _res1) or (_res2.get('name') if isinstance(_res2, dict) else _res2) or cleaned_name
                core_name = (core_name or "").strip("-— ·|")

                enhanced.update({
                    "customer_name": (core_name or cleaned_name or norm_name),
                    "industry_name": parsed.get("industry") or data.get("industry", ""),
                    "address": parsed.get("address") or data.get("address", ""),
                    "district_name": data.get("district_name", "") or data.get("region", ""),
                    "data_source": "web_search",
                })

                if not enhanced["industry_name"]:
                    try:
                        inferred = get_company_industry(enhanced["customer_name"], enhanced["address"])
                        if inferred:
                            enhanced["industry_name"] = inferred
                    except Exception:
                        pass

            # 生成新闻数据（轻量）
            news_data = {"summary": "暂无最新商业资讯", "references": []}
            try:
                news_data = self.analysis_service.get_company_news(enhanced["customer_name"])
            except Exception:
                pass

            # 生成综合/备用分析
            summary_text = self.analysis_service.generate_comprehensive_company_analysis(enhanced, news_data)

            final_result = {
                "company_name": enhanced["customer_name"],
                "summary": summary_text,
                "details": {
                    "name": enhanced["customer_name"],
                    "region": enhanced["district_name"],
                    "address": enhanced["address"],
                    "industry": enhanced["industry_name"],
                    "industry_brain": enhanced["brain_name"],
                    "chain_status": enhanced["chain_status"],
                    "revenue_info": enhanced["revenue_info"],
                    "company_status": enhanced["company_status"],
                    "data_source": enhanced["data_source"],
                },
                "news": news_data
            }

            return {"status": "success", "data": final_result, "source": enhanced["data_source"]}

        except Exception as e:
            logger.error(f"处理网络搜索数据时出错: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"处理网络搜索数据时出错: {str(e)}"
            }
    
    def get_company_basic_info(self, company_name):
        """
        获取企业基础信息（简化版本）

        Args:
            company_name (str): 企业名称

        Returns:
            dict: 企业基础信息
        """
        try:
            # 查询本地数据库
            local_data = get_customer_by_name(company_name)

            if local_data:
                # 进行基础数据增强
                enhanced_data = self.data_enhancement_service.enhance_location_info(local_data)
                enhanced_data = self.data_enhancement_service.enhance_industry_info(enhanced_data)

                return {
                    "status": "success",
                    "data": {
                        "name": enhanced_data.get('customer_name', ''),
                        "region": enhanced_data.get('district_name', ''),
                        "address": enhanced_data.get('address', ''),
                        "industry": enhanced_data.get('industry_name', ''),
                        "source": "local_database"
                    }
                }
            else:
                # 使用搜索服务，解析并清洗基础信息
                try:
                    from infrastructure.utils.text_processor import company_name_extractor, search_result_processor, get_company_industry
                    import re
                    norm_name = company_name_extractor.normalize_company_name(company_name)
                    search_result = self.search_service.search_company_info(norm_name)
                    if search_result.get('status') == 'success':
                        data = search_result.get('data', {}) or {}
                        parsed = search_result_processor.extract_company_info_from_search_results({'data': data})
                        # 先标准化并移除常见噪声后缀
                        cleaned_name = company_name_extractor.normalize_company_name(parsed.get('name') or norm_name)
                        cleaned_name = re.sub(r'(企业信息|电话|公司地址|品牌网)(?:$|[-—·|])', '', cleaned_name)
                        # 提取核心企业名，避免后缀污染
                        # 提取核心企业名（extract_company_name 返回字典，需取 'name'）
                        _res1 = company_name_extractor.extract_company_name(cleaned_name)
                        _res2 = company_name_extractor.extract_company_name(norm_name)
                        core_name = (_res1.get('name') if isinstance(_res1, dict) else _res1) or (_res2.get('name') if isinstance(_res2, dict) else _res2) or cleaned_name
                        core_name = (core_name or '').strip('-— ·|')
                        company_info = {
                            'name': (core_name or cleaned_name or norm_name),
                            'region': data.get('region', '') or data.get('district_name', ''),
                            'address': parsed.get('address') or data.get('address', ''),
                            'industry': parsed.get('industry') or data.get('industry', ''),
                            'source': 'web_search'
                        }
                        if not company_info['industry']:
                            try:
                                inferred = get_company_industry(company_info['name'], company_info['address'])
                                if inferred:
                                    company_info['industry'] = inferred
                            except Exception:
                                pass
                        return {'status': 'success', 'data': company_info}
                    else:
                        return {'status': 'success', 'data': {'name': norm_name, 'region': '', 'address': '', 'industry': '', 'source': 'unknown'}}
                except Exception as e:
                    logger.error(f"基础信息搜索解析失败: {e}", exc_info=True)
                    return {'status': 'success', 'data': {'name': company_name, 'region': '', 'address': '', 'industry': '', 'source': 'unknown'}}

        except Exception as e:
            logger.error(f"获取企业基础信息时出错: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"获取企业基础信息时出错: {str(e)}"
            }

    def search_local_database(self, company_name):
        """
        搜索本地数据库

        Args:
            company_name (str): 企业名称

        Returns:
            dict: 搜索结果
        """
        try:
            local_data = get_customer_by_name(company_name)

            if local_data:
                return {
                    "found": True,
                    "data": local_data,
                    "message": f"在本地数据库中找到企业: {company_name}"
                }
            else:
                return {
                    "found": False,
                    "data": None,
                    "message": f"本地数据库中未找到企业: {company_name}"
                }

        except Exception as e:
            logger.error(f"搜索本地数据库时出错: {e}", exc_info=True)
            return {
                "found": False,
                "data": None,
                "message": f"搜索本地数据库时出错: {str(e)}"
            }

    def update_company_info(self, customer_id, updates):
        """
        更新企业信息

        Args:
            customer_id (int): 客户ID
            updates (dict): 更新数据

        Returns:
            dict: 更新结果
        """
        try:
            from infrastructure.database.standalone_queries import update_customer_by_id

            result = update_customer_by_id(customer_id, updates)

            if result:
                return {
                    "status": "success",
                    "data": result,
                    "message": f"企业信息更新成功: Customer ID {customer_id}"
                }
            else:
                return {
                    "status": "error",
                    "message": f"未找到客户: Customer ID {customer_id}"
                }

        except Exception as e:
            logger.error(f"更新企业信息时出错: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"更新企业信息时出错: {str(e)}"
            }

    def update_chain_leader_info(self, company_name, updates):
        """
        更新链主企业信息

        Args:
            company_name (str): 企业名称
            updates (dict): 更新数据

        Returns:
            dict: 更新结果
        """
        try:
            from infrastructure.database.standalone_queries import get_customer_by_name, update_customer_by_id

            # 先查询企业
            customer_data = get_customer_by_name(company_name)

            if not customer_data:
                return {
                    "status": "error",
                    "message": f"未找到企业: {company_name}"
                }

            customer_id = customer_data.get('customer_id')
            if not customer_id:
                return {
                    "status": "error",
                    "message": f"企业数据格式错误: {company_name}"
                }

            # 更新链主相关信息
            chain_leader_updates = {
                "is_chain_leader": updates.get("is_chain_leader", True),
                "chain_leader_level": updates.get("chain_leader_level", ""),
                "chain_leader_industry": updates.get("chain_leader_industry", ""),
                "chain_leader_description": updates.get("chain_leader_description", "")
            }

            result = update_customer_by_id(customer_id, chain_leader_updates)

            if result:
                return {
                    "status": "success",
                    "data": result,
                    "message": f"链主企业信息更新成功: {company_name}"
                }
            else:
                return {
                    "status": "error",
                    "message": f"更新链主企业信息失败: {company_name}"
                }

        except Exception as e:
            logger.error(f"更新链主企业信息时出错: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"更新链主企业信息时出错: {str(e)}"
            }

    # ==================== 新增方法（使用领域模型） ====================
    # Day3-4重构：使用领域模型替代Dict

    def process_company_info_v2(self, user_input: str) -> EnterpriseComprehensiveInfo:
        """
        处理企业信息（使用领域模型版本）

        Args:
            user_input: 用户输入的企业信息

        Returns:
            EnterpriseComprehensiveInfo: 企业综合信息领域模型

        Raises:
            ValueError: 输入验证失败
            RuntimeError: 处理过程中出现错误
        """
        if not user_input or not user_input.strip():
            raise ValueError("用户输入不能为空")

        try:
            # 1. 提取公司名称
            name_result = self.search_service.extract_company_name_from_input(user_input)

            if name_result.get('status') == 'error':
                raise RuntimeError(f"企业名称提取失败: {name_result.get('message')}")

            company_name = name_result['name']

            # 2. 查询本地数据库
            local_data = self.customer_repository.find_by_name(company_name)

            if local_data:
                # 有本地数据，使用本地数据构建
                return self._build_from_local_data(local_data)
            else:
                # 无本地数据，使用搜索数据构建
                return self._build_from_search(company_name)

        except Exception as e:
            logger.error(f"处理企业信息失败: {e}", exc_info=True)
            raise RuntimeError(f"处理企业信息失败: {str(e)}")

    def _build_from_local_data(self, local_data) -> EnterpriseComprehensiveInfo:
        """
        从本地数据构建企业综合信息

        Args:
            local_data: 本地数据库Customer对象

        Returns:
            EnterpriseComprehensiveInfo: 企业综合信息
        """
        # 提取基础信息
        basic_info = EnterpriseBasicInfo(
            name=local_data.customer_name,
            normalized_name=local_data.customer_name,
            industry=local_data.industry_name,
            address=local_data.address or "",
            district=local_data.district_name
        )

        # 获取新闻信息
        news_info = None
        try:
            news_data = self.analysis_service.get_company_news(local_data.customer_name)
            if news_data and news_data.get('summary'):
                news_info = EnterpriseNewsInfo(
                    summary=news_data.get('summary', ''),
                    references=news_data.get('references', []),
                    source="analysis_service"
                )
        except Exception as e:
            logger.warning(f"获取新闻失败: {e}")

        # 构建综合信息
        comprehensive = EnterpriseComprehensiveInfo(
            basic_info=basic_info,
            revenue_info="暂无营收数据",  # 可从数据增强服务获取
            ranking_status="暂无排名信息",
            industry_brain=local_data.brain_name or "",
            chain_status="链主企业" if local_data.chain_leader_id else "",
            news_info=news_info,
            data_source=DataSource.LOCAL_DB,
            confidence_score=0.9  # 本地数据可信度高
        )

        return comprehensive

    def _build_from_search(self, company_name: str) -> EnterpriseComprehensiveInfo:
        """
        从搜索��果构建企业综合信息

        Args:
            company_name: 企业名称

        Returns:
            EnterpriseComprehensiveInfo: 企业综合信息
        """
        from infrastructure.utils.text_processor import (
            company_name_extractor,
            search_result_processor
        )
        import re

        # 标准化名称
        norm_name = company_name_extractor.normalize_company_name(company_name)

        # 搜索企业信息
        search_result = self.search_service.search_company_info(norm_name)

        # 默认基础信息
        name = norm_name
        industry = ""
        address = ""
        district = ""

        # 解析搜索结果
        if search_result.get("status") == "success":
            data = search_result.get("data", {}) or {}
            parsed = search_result_processor.extract_company_info_from_search_results({"data": data})

            # 清洗名称
            cleaned_name = company_name_extractor.normalize_company_name(parsed.get("name") or norm_name)
            cleaned_name = re.sub(r"(企业信息|电话|公司地址|品牌网)(?:$|[-—·|])", "", cleaned_name)

            # 提取核心名称
            _res = company_name_extractor.extract_company_name(cleaned_name)
            core_name = _res.get('name') if isinstance(_res, dict) else _res
            name = (core_name or cleaned_name or norm_name).strip("-— ·|")

            industry = parsed.get("industry") or data.get("industry", "")
            address = parsed.get("address") or data.get("address", "")
            district = data.get("district_name", "") or data.get("region", "")

        # 创建基础信息
        basic_info = EnterpriseBasicInfo(
            name=name,
            normalized_name=norm_name,
            industry=industry if industry else None,
            address=address if address else None,
            district=district if district else None
        )

        # 获取新闻
        news_info = None
        try:
            news_data = self.analysis_service.get_company_news(name)
            if news_data and news_data.get('summary'):
                news_info = EnterpriseNewsInfo(
                    summary=news_data.get('summary', ''),
                    references=news_data.get('references', []),
                    source="analysis_service"
                )
        except Exception as e:
            logger.warning(f"获取新闻失败: {e}")

        # 构建综合信息
        comprehensive = EnterpriseComprehensiveInfo(
            basic_info=basic_info,
            revenue_info="暂无营收数据",
            ranking_status="暂无排名信息",
            industry_brain="",
            chain_status="",
            news_info=news_info,
            data_source=DataSource.SEARCH_ENGINE,
            confidence_score=0.6  # 搜索数据可信度中等
        )

        return comprehensive
