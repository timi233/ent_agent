"""
企业信息处理器 - 负责企业基础信息的提取、清洗和标准化

职责：
- 从用户输入中提取企业名称
- 标准化和清洗企业名称
- 从搜索结果中解析企业基础信息
- 构建企业基础信息领域模型
"""

import logging
import re
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class EnterpriseProcessor:
    """企业信息处理器"""

    def __init__(self, search_service):
        """
        初始化企业信息处理器

        Args:
            search_service: 搜索服务
        """
        self.search_service = search_service

    def extract_company_name(self, user_input: str) -> Dict:
        """
        从用户输入中提取企业名称

        Args:
            user_input: 用户输入文本

        Returns:
            dict: 包含企业名称和提取状态的字典
                {
                    'status': 'success'/'error',
                    'name': str,
                    'is_complete': bool,
                    'source': str,
                    'message': str (如果有错误)
                }
        """
        try:
            result = self.search_service.extract_company_name_from_input(user_input)
            return result
        except Exception as e:
            logger.error(f"提取企业名称失败: {e}", exc_info=True)
            return {
                'status': 'error',
                'message': f'提取企业名称失败: {str(e)}'
            }

    def normalize_company_name(self, company_name: str) -> str:
        """
        标准化企业名称

        Args:
            company_name: 原始企业名称

        Returns:
            str: 标准化后的企业名称
        """
        try:
            from infrastructure.utils.text_processor import company_name_extractor
            return company_name_extractor.normalize_company_name(company_name)
        except Exception as e:
            logger.warning(f"标准化企业名称失败，返回原始名称: {e}")
            return company_name

    def clean_company_name(self, company_name: str) -> str:
        """
        清洗企业名称，去除常见噪声后缀

        Args:
            company_name: 企业名称

        Returns:
            str: 清洗后的企业名称
        """
        # 先标准化
        cleaned = self.normalize_company_name(company_name)

        # 移除常见噪声后缀
        cleaned = re.sub(r"(企业信息|电话|公司地址|品牌网)(?:$|[-—·|])", "", cleaned)

        # 去除尾部特殊字符
        cleaned = cleaned.strip("-— ·|")

        return cleaned

    def extract_core_company_name(self, company_name: str) -> str:
        """
        提取核心企业名称

        Args:
            company_name: 企业名称

        Returns:
            str: 核心企业名称
        """
        try:
            from infrastructure.utils.text_processor import company_name_extractor

            # 先清洗
            cleaned = self.clean_company_name(company_name)

            # 提取核心名称
            result = company_name_extractor.extract_company_name(cleaned)

            # extract_company_name 可能返回字典或字符串
            if isinstance(result, dict):
                core_name = result.get('name', cleaned)
            else:
                core_name = result or cleaned

            return core_name.strip("-— ·|")

        except Exception as e:
            logger.warning(f"提取核心企业名称失败，返回清洗后名称: {e}")
            return self.clean_company_name(company_name)

    def parse_search_result(self, search_result: Dict) -> Dict:
        """
        从搜索结果中解析企业基础信息

        Args:
            search_result: 搜索服务返回的结果

        Returns:
            dict: 解析后的企业信息
                {
                    'name': str,
                    'industry': str,
                    'address': str,
                    'district': str
                }
        """
        default_info = {
            'name': '',
            'industry': '',
            'address': '',
            'district': ''
        }

        if not search_result or search_result.get('status') != 'success':
            return default_info

        try:
            from infrastructure.utils.text_processor import search_result_processor

            data = search_result.get('data', {}) or {}
            parsed = search_result_processor.extract_company_info_from_search_results({'data': data})

            return {
                'name': parsed.get('name', ''),
                'industry': parsed.get('industry', '') or data.get('industry', ''),
                'address': parsed.get('address', '') or data.get('address', ''),
                'district': data.get('district_name', '') or data.get('region', '')
            }
        except Exception as e:
            logger.error(f"解析搜索结果失败: {e}", exc_info=True)
            return default_info

    def build_basic_info_from_search(self, company_name: str) -> Dict:
        """
        从搜索构建企业基础信息

        Args:
            company_name: 企业名称

        Returns:
            dict: 企业基础信息
                {
                    'name': str,
                    'normalized_name': str,
                    'industry': str,
                    'address': str,
                    'district': str,
                    'source': 'web_search'
                }
        """
        # 标准化名称
        norm_name = self.normalize_company_name(company_name)

        # 搜索企业信息
        search_result = self.search_service.search_company_info(norm_name)

        # 解析搜索结果
        parsed_info = self.parse_search_result(search_result)

        # 处理企业名称
        final_name = norm_name
        if parsed_info['name']:
            # 提取核心名称
            core_name = self.extract_core_company_name(parsed_info['name'])
            if core_name:
                final_name = core_name

        return {
            'name': final_name,
            'normalized_name': norm_name,
            'industry': parsed_info['industry'],
            'address': parsed_info['address'],
            'district': parsed_info['district'],
            'source': 'web_search'
        }

    def infer_industry(self, company_name: str, address: str = '') -> Optional[str]:
        """
        推断企业所属行业

        Args:
            company_name: 企业名称
            address: 企业地址

        Returns:
            str: 推断的行业，如果推断失败返回None
        """
        try:
            from infrastructure.utils.text_processor import get_company_industry
            inferred = get_company_industry(company_name, address)
            return inferred if inferred else None
        except Exception as e:
            logger.warning(f"推断行业失败: {e}")
            return None
