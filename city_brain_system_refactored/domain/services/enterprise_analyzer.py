"""
企业分析器 - 负责生成企业分析报告

职责：
- 生成LLM综合分析
- 获取企业新闻资讯
- 格式化分析结果
- 提供备用分析方案
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class EnterpriseAnalyzer:
    """企业分析器"""

    def __init__(self, analysis_service):
        """
        初始化企业分析器

        Args:
            analysis_service: 分析服务
        """
        self.analysis_service = analysis_service

    def get_company_news(self, company_name: str) -> Dict:
        """
        获取企业新闻资讯

        Args:
            company_name: 企业名称

        Returns:
            dict: 新闻数据
                {
                    'summary': str,
                    'references': list
                }
        """
        try:
            news_data = self.analysis_service.get_company_news(company_name)
            if news_data:
                return news_data
            return {
                'summary': '暂无最新商业资讯',
                'references': []
            }
        except Exception as e:
            logger.warning(f"获取企业新闻失败: {e}")
            return {
                'summary': '暂无最新商业资讯',
                'references': []
            }

    def generate_comprehensive_analysis(
        self,
        enterprise_data: Dict,
        news_data: Optional[Dict] = None
    ) -> str:
        """
        生成企业综合分析

        Args:
            enterprise_data: 企业数据
            news_data: 新闻数据（可选）

        Returns:
            str: 综合分析文本
        """
        try:
            if news_data is None:
                news_data = {
                    'summary': '暂无最新商业资讯',
                    'references': []
                }

            analysis = self.analysis_service.generate_comprehensive_company_analysis(
                enterprise_data,
                news_data
            )
            return analysis if analysis else self._generate_fallback_analysis(enterprise_data)
        except Exception as e:
            logger.error(f"生成综合分析失败: {e}", exc_info=True)
            return self._generate_fallback_analysis(enterprise_data)

    def _generate_fallback_analysis(self, enterprise_data: Dict) -> str:
        """
        生成备用分析（当LLM服务不可用时）

        Args:
            enterprise_data: 企业数据

        Returns:
            str: 备用分析文本
        """
        company_name = enterprise_data.get('customer_name', enterprise_data.get('name', '未知企业'))
        industry = enterprise_data.get('industry_name', enterprise_data.get('industry', ''))
        address = enterprise_data.get('address', '')
        district = enterprise_data.get('district_name', enterprise_data.get('region', ''))

        analysis_parts = [f"企业名称：{company_name}"]

        if industry:
            analysis_parts.append(f"所属行业：{industry}")

        if district:
            analysis_parts.append(f"所在地区：{district}")

        if address:
            analysis_parts.append(f"企业地址：{address}")

        # 添加链主状态
        chain_status = enterprise_data.get('chain_status', '')
        if chain_status:
            analysis_parts.append(f"产业链地位：{chain_status}")

        # 添加产业大脑
        brain_name = enterprise_data.get('brain_name', '')
        if brain_name and brain_name != '本城市暂无相关产业大脑':
            analysis_parts.append(f"产业大脑：{brain_name}")

        # 添加营收信息
        revenue_info = enterprise_data.get('revenue_info', '')
        if revenue_info and revenue_info != '暂无营收数据':
            analysis_parts.append(f"营收情况：{revenue_info}")

        # 添加排名信息
        company_status = enterprise_data.get('company_status', '')
        if company_status and company_status != '暂无排名信息':
            analysis_parts.append(f"企业地位：{company_status}")

        return '\n'.join(analysis_parts)

    def format_analysis_result(
        self,
        enterprise_data: Dict,
        news_data: Dict,
        llm_analysis: str
    ) -> Dict:
        """
        格式化分析结果

        Args:
            enterprise_data: 企业数据
            news_data: 新闻数据
            llm_analysis: LLM分析文本

        Returns:
            dict: 格式化后的分析结果
        """
        try:
            return self.analysis_service.format_analysis_result(
                enterprise_data,
                news_data,
                llm_analysis
            )
        except Exception as e:
            logger.error(f"格式化分析结果失败: {e}", exc_info=True)
            return self._format_fallback_result(enterprise_data, news_data, llm_analysis)

    def _format_fallback_result(
        self,
        enterprise_data: Dict,
        news_data: Dict,
        llm_analysis: str
    ) -> Dict:
        """
        格式化备用结果

        Args:
            enterprise_data: 企业数据
            news_data: 新闻数据
            llm_analysis: LLM分析文本

        Returns:
            dict: 备用格式化结果
        """
        company_name = enterprise_data.get('customer_name', enterprise_data.get('name', ''))
        data_source = enterprise_data.get('data_source', 'unknown')

        return {
            'status': 'success',
            'data': {
                'company_name': company_name,
                'summary': llm_analysis,
                'details': {
                    'name': company_name,
                    'region': enterprise_data.get('district_name', enterprise_data.get('region', '')),
                    'address': enterprise_data.get('address', ''),
                    'industry': enterprise_data.get('industry_name', enterprise_data.get('industry', '')),
                    'industry_brain': enterprise_data.get('brain_name', ''),
                    'chain_status': enterprise_data.get('chain_status', ''),
                    'revenue_info': enterprise_data.get('revenue_info', '暂无营收数据'),
                    'company_status': enterprise_data.get('company_status', '暂无排名信息'),
                    'data_source': data_source
                },
                'news': news_data
            },
            'source': data_source
        }

    def analyze_with_local_data(self, local_data: Dict, enhanced_data: Dict) -> Dict:
        """
        使用本地数据生成分析（完整流程）

        Args:
            local_data: 原始本地数据
            enhanced_data: 增强后的数据

        Returns:
            dict: 分析结果
        """
        # 获取企业新闻
        company_name = enhanced_data.get('customer_name', '')
        news_data = self.get_company_news(company_name)

        # 生成LLM分析
        llm_analysis = self.generate_comprehensive_analysis(enhanced_data, news_data)

        # 格式化结果
        result = self.format_analysis_result(enhanced_data, news_data, llm_analysis)

        return result

    def analyze_with_search_data(self, search_data: Dict) -> Dict:
        """
        使用搜索数据生成分析（轻量流程）

        Args:
            search_data: 搜索获得的数据

        Returns:
            dict: 分析结果
        """
        # 获取企业新闻（轻量）
        company_name = search_data.get('customer_name', search_data.get('name', ''))
        news_data = self.get_company_news(company_name)

        # 生成综合分析
        llm_analysis = self.generate_comprehensive_analysis(search_data, news_data)

        # 格式化结果
        result = {
            'status': 'success',
            'data': {
                'company_name': company_name,
                'summary': llm_analysis,
                'details': {
                    'name': company_name,
                    'region': search_data.get('district_name', search_data.get('region', '')),
                    'address': search_data.get('address', ''),
                    'industry': search_data.get('industry_name', search_data.get('industry', '')),
                    'industry_brain': search_data.get('brain_name', ''),
                    'chain_status': search_data.get('chain_status', ''),
                    'revenue_info': search_data.get('revenue_info', '暂无营收数据'),
                    'company_status': search_data.get('company_status', '暂无排名信息'),
                    'data_source': search_data.get('data_source', 'web_search')
                },
                'news': news_data
            },
            'source': search_data.get('data_source', 'web_search')
        }

        return result
