"""
企业服务主逻辑（重构版） - 协调各个处理器完成企业信息处理

职责：
- 企业信息处理的主要业务流程控制
- 协调企业处理器、数据增强器、分析器
- 处理有本地数据和无本地数据的不同情况
- 统一的错误处理和结果返回

重构改进（阶段四）：
- 按职责拆分为多个专门的处理器
- 企业处理器：负责基础信息提取和清洗
- 数据增强器：负责数据补充和优化
- 分析器：负责LLM分析和报告生成
- 主服务：协调各处理器完成业务流程
"""

import logging
from typing import Dict, Optional

from .enterprise_processor import EnterpriseProcessor
from .enterprise_enhancer import EnterpriseEnhancer
from .enterprise_analyzer import EnterpriseAnalyzer
from .search_service import SearchService
from .data_enhancement_service import DataEnhancementService
from .analysis_service import AnalysisService

logger = logging.getLogger(__name__)


class EnterpriseServiceRefactored:
    """企业服务主逻辑类（重构版 - 使用处理器模式）"""

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
        # 保存原始服务
        self.search_service = search_service
        self.data_enhancement_service = data_enhancement_service
        self.analysis_service = analysis_service
        self.customer_repository = customer_repository

        # 初始化处理器
        self.processor = EnterpriseProcessor(search_service)
        self.enhancer = EnterpriseEnhancer(data_enhancement_service)
        self.analyzer = EnterpriseAnalyzer(analysis_service)

    def process_company_info(self, user_input: str) -> Dict:
        """
        处理用户输入的企业信息（主入口）

        Args:
            user_input: 用户输入的企业信息

        Returns:
            dict: 处理结果，包含企业信息和分析报告
        """
        try:
            # 1. 提取公司名称
            name_result = self.processor.extract_company_name(user_input)

            if name_result.get('status') == 'error':
                return name_result

            company_name = name_result['name']
            is_complete = name_result.get('is_complete', False)

            # 2. 查询本地数据库
            local_data = self.customer_repository.find_by_name(company_name)

            if not local_data and is_complete:
                # 如果完整名称没找到，可以在这里添加更多查询策略
                pass

            # 3. 根据是否有本地数据选择处理流程
            if local_data:
                return self.process_with_local_data(local_data)
            else:
                return self.process_without_local_data(company_name)

        except Exception as e:
            logger.error(f"处理企业信息时出错: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"处理企业信息时出错: {str(e)}"
            }

    def process_with_local_data(self, local_data) -> Dict:
        """
        处理存在本地数据的情况

        Args:
            local_data: 本地数据库中的企业数据（Customer对象或字典）

        Returns:
            dict: 处理结果
        """
        try:
            # 转换Customer对象为字典
            if hasattr(local_data, 'to_dict'):
                local_data_dict = local_data.to_dict()
            else:
                local_data_dict = local_data

            # 1. 数据增强
            enhanced_data = self.enhancer.enhance_all(local_data_dict)

            # 2. 生成分析报告
            result = self.analyzer.analyze_with_local_data(local_data_dict, enhanced_data)

            # 3. 数据库同步
            self.enhancer.sync_to_database(enhanced_data, local_data_dict)

            return result

        except Exception as e:
            logger.error(f"处理本地数据时出错: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"处理本地数据时出错: {str(e)}"
            }

    def process_without_local_data(self, company_name: str) -> Dict:
        """
        处理不存在本地数据的情况

        Args:
            company_name: 企业名称

        Returns:
            dict: 处理结果
        """
        try:
            # 1. 从搜索构建基础信息
            basic_info = self.processor.build_basic_info_from_search(company_name)

            # 2. 补充行业信息（如果缺失）
            if not basic_info.get('industry'):
                inferred_industry = self.processor.infer_industry(
                    basic_info['name'],
                    basic_info.get('address', '')
                )
                if inferred_industry:
                    basic_info['industry'] = inferred_industry

            # 3. 构建增强数据结构
            enhanced_data = {
                "customer_name": basic_info['name'],
                "district_name": basic_info.get('district', ''),
                "address": basic_info.get('address', ''),
                "industry_name": basic_info.get('industry', ''),
                "brain_name": '',
                "chain_status": '',
                "revenue_info": '暂无营收数据',
                "company_status": '暂无排名信息',
                "data_source": basic_info.get('source', 'web_search')
            }

            # 4. 从外部数据源增强（营收、排名）
            external_enhancement = self.enhancer.enhance_from_external(
                enhanced_data["customer_name"],
                enhanced_data.get("industry_name", '')
            )
            enhanced_data.update(external_enhancement)

            # 5. 生成分析报告
            result = self.analyzer.analyze_with_search_data(enhanced_data)

            return result

        except Exception as e:
            logger.error(f"处理网络搜索数据时出错: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"处理网络搜索数据时出错: {str(e)}"
            }

    def get_company_basic_info(self, company_name: str) -> Dict:
        """
        获取企业基础信息（简化版本）

        Args:
            company_name: 企业名称

        Returns:
            dict: 企业基础信息
        """
        try:
            # 查询本地数据库
            local_data = self.customer_repository.find_by_name(company_name)

            if local_data:
                # 转换Customer对象为字典
                if hasattr(local_data, 'to_dict'):
                    local_data_dict = local_data.to_dict()
                else:
                    local_data_dict = local_data

                # 进行基础数据增强
                enhanced = self.enhancer.enhance_location_info(local_data_dict)
                enhanced = self.enhancer.enhance_industry_info(enhanced)

                return {
                    "status": "success",
                    "data": {
                        "name": enhanced.get('customer_name', ''),
                        "region": enhanced.get('district_name', ''),
                        "address": enhanced.get('address', ''),
                        "industry": enhanced.get('industry_name', ''),
                        "source": "local_database"
                    }
                }
            else:
                # 从搜索获取基础信息
                basic_info = self.processor.build_basic_info_from_search(company_name)

                # 补充行业信息
                if not basic_info.get('industry'):
                    inferred = self.processor.infer_industry(
                        basic_info['name'],
                        basic_info.get('address', '')
                    )
                    if inferred:
                        basic_info['industry'] = inferred

                return {
                    'status': 'success',
                    'data': {
                        'name': basic_info['name'],
                        'region': basic_info.get('district', ''),
                        'address': basic_info.get('address', ''),
                        'industry': basic_info.get('industry', ''),
                        'source': basic_info.get('source', 'web_search')
                    }
                }

        except Exception as e:
            logger.error(f"获取企业基础信息时出错: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"获取企业基础信息时出错: {str(e)}"
            }

    def search_local_database(self, company_name: str) -> Dict:
        """
        搜索本地数据库

        Args:
            company_name: 企业名称

        Returns:
            dict: 搜索结果
        """
        try:
            local_data = self.customer_repository.find_by_name(company_name)

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

    def update_company_info(self, customer_id: int, updates: Dict) -> Dict:
        """
        更新企业信息

        Args:
            customer_id: 客户ID
            updates: 更新数据

        Returns:
            dict: 更新结果
        """
        try:
            result = self.customer_repository.update(customer_id, updates)

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

    def update_chain_leader_info(self, company_name: str, updates: Dict) -> Dict:
        """
        更新链主企业信息

        Args:
            company_name: 企业名称
            updates: 更新数据

        Returns:
            dict: 更新结果
        """
        try:
            # 先查询企业
            customer_data = self.customer_repository.find_by_name(company_name)

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

            result = self.customer_repository.update(customer_id, chain_leader_updates)

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
