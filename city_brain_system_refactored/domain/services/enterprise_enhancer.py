"""
企业数据增强器 - 负责补充和优化企业数据

职责：
- 地址信息增强
- 行业信息增强
- 营收信息增强
- 企业排名状态增强
- 产业链信息增强
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class EnterpriseEnhancer:
    """企业数据增强器"""

    def __init__(self, data_enhancement_service):
        """
        初始化企业数据增强器

        Args:
            data_enhancement_service: 数据增强服务
        """
        self.data_enhancement_service = data_enhancement_service

    def enhance_location_info(self, enterprise_data: Dict) -> Dict:
        """
        增强地址信息

        Args:
            enterprise_data: 企业数据

        Returns:
            dict: 增强后的企业数据
        """
        try:
            return self.data_enhancement_service.enhance_location_info(enterprise_data)
        except Exception as e:
            logger.error(f"增强地址信息失败: {e}", exc_info=True)
            return enterprise_data

    def enhance_industry_info(self, enterprise_data: Dict) -> Dict:
        """
        增强行业信息

        Args:
            enterprise_data: 企业数据

        Returns:
            dict: 增强后的企业数据
        """
        try:
            return self.data_enhancement_service.enhance_industry_info(enterprise_data)
        except Exception as e:
            logger.error(f"增强行业信息失败: {e}", exc_info=True)
            return enterprise_data

    def enhance_revenue_info(self, enterprise_data: Dict) -> Dict:
        """
        增强营收信息

        Args:
            enterprise_data: 企业数据

        Returns:
            dict: 增强后的企业数据
        """
        try:
            return self.data_enhancement_service.enhance_revenue_info(enterprise_data)
        except Exception as e:
            logger.error(f"增强营收信息失败: {e}", exc_info=True)
            return enterprise_data

    def enhance_ranking_status(self, enterprise_data: Dict) -> Dict:
        """
        增强企业排名状态

        Args:
            enterprise_data: 企业数据

        Returns:
            dict: 增强后的企业数据
        """
        try:
            return self.data_enhancement_service.enhance_ranking_status(enterprise_data)
        except Exception as e:
            logger.error(f"增强排名状态失败: {e}", exc_info=True)
            return enterprise_data

    def enhance_chain_info(self, enterprise_data: Dict) -> Dict:
        """
        增强产业链信息

        Args:
            enterprise_data: 企业数据

        Returns:
            dict: 增强后的企业数据
        """
        try:
            return self.data_enhancement_service.enhance_chain_info(enterprise_data)
        except Exception as e:
            logger.error(f"增强产业链信息失败: {e}", exc_info=True)
            return enterprise_data

    def enhance_all(self, enterprise_data: Dict) -> Dict:
        """
        执行所有数据增强

        Args:
            enterprise_data: 企业数据

        Returns:
            dict: 全面增强后的企业数据
        """
        try:
            return self.data_enhancement_service.enhance_all_data(enterprise_data)
        except Exception as e:
            logger.error(f"全面数据增强失败: {e}", exc_info=True)
            return enterprise_data

    def sync_to_database(self, enhanced_data: Dict, original_data: Dict) -> bool:
        """
        将增强的数据同步到数据库

        Args:
            enhanced_data: 增强后的数据
            original_data: 原始数据

        Returns:
            bool: 同步是否成功
        """
        try:
            self.data_enhancement_service.sync_database_updates(enhanced_data, original_data)
            return True
        except Exception as e:
            logger.error(f"同步数据库失败: {e}", exc_info=True)
            return False

    def enhance_from_external(self, company_name: str, industry: str = '') -> Dict:
        """
        从外部数据源增强企业信息（用于无本地数据的情况）

        Args:
            company_name: 企业名称
            industry: 企业行业（可选）

        Returns:
            dict: 外部数据增强结果
                {
                    'revenue_info': str,
                    'company_status': str
                }
        """
        result = {
            'revenue_info': '暂无营收数据',
            'company_status': '暂无排名信息'
        }

        # 尝试获取营收信息
        try:
            revenue_data = self._get_revenue_from_external(company_name)
            if revenue_data:
                result['revenue_info'] = revenue_data
        except Exception as e:
            logger.warning(f"获取外部营收信息失败: {e}")

        # 尝试获取排名信息
        try:
            ranking_data = self._get_ranking_from_external(company_name, industry)
            if ranking_data:
                result['company_status'] = ranking_data
        except Exception as e:
            logger.warning(f"获取外部排名信息失败: {e}")

        return result

    def _get_revenue_from_external(self, company_name: str) -> Optional[str]:
        """
        从外部获取营收信息

        Args:
            company_name: 企业名称

        Returns:
            str: 营收信息，失败返回None
        """
        try:
            # 调用外部营收服务
            from infrastructure.external.revenue_service import get_company_revenue_info
            revenue_info = get_company_revenue_info(company_name)
            return revenue_info if revenue_info else None
        except Exception as e:
            logger.debug(f"外部营收服务调用失败: {e}")
            return None

    def _get_ranking_from_external(self, company_name: str, industry: str = '') -> Optional[str]:
        """
        从外部获取排名信息

        Args:
            company_name: 企业名称
            industry: 企业行业

        Returns:
            str: 排名信息，失败返回None
        """
        try:
            # 调用外部排名服务
            from infrastructure.external.ranking_service import get_company_ranking_status
            ranking_status = get_company_ranking_status(company_name, industry)
            return ranking_status if ranking_status else None
        except Exception as e:
            logger.debug(f"外部排名服务调用失败: {e}")
            return None
