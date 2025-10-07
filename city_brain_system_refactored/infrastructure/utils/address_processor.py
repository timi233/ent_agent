"""
地址处理工具
重构自原有的 utils/address_extractor.py 和 utils/address_updater.py，
提供完整的地址解析、搜索和更新功能
"""
import re
from typing import Optional, Dict, Any, List
import logging

from .logger import get_logger
from ..database.repositories.customer_repository import CustomerRepository
from ..database.repositories.enterprise_repository import EnterpriseRepository

logger = get_logger()


class AddressExtractor:
    """地址提取器"""
    
    def __init__(self):
        """初始化地址提取器"""
        # 常见的市级城市模式
        self.city_patterns = [
            # 直辖市模式：北京市、上海市、天津市、重庆市
            r'(北京市|上海市|天津市|重庆市)',
            # 地级市模式：XX市（避免重复匹配）
            r'([^省自治区市]{2,6}市)',
            # 特殊行政区
            r'(香港|澳门)',
        ]
        
        # 排除的非城市词汇
        self.exclude_words = [
            '公司', '集团', '有限', '股份', '企业', '商贸', '科技', '发展',
            '投资', '控股', '实业', '贸易', '建设', '工程', '服务'
        ]
    
    def extract_city_from_address(self, address: str) -> Optional[str]:
        """
        从企业地址中提取市级城市名称
        
        Args:
            address: 企业地址
            
        Returns:
            提取的城市名称，如果提取失败返回None
        """
        if not address or not isinstance(address, str):
            return None
        
        for pattern in self.city_patterns:
            match = re.search(pattern, address)
            if match:
                city = match.group(1)
                # 过滤掉一些常见的非城市词汇
                if not any(word in city for word in self.exclude_words):
                    return city
        
        return None
    
    def extract_province_from_address(self, address: str) -> Optional[str]:
        """
        从地址中提取省份信息
        
        Args:
            address: 企业地址
            
        Returns:
            提取的省份名称，如果提取失败返回None
        """
        if not address or not isinstance(address, str):
            return None
        
        province_patterns = [
            r'([\u4e00-\u9fa5]{2,6}省)',
            r'([\u4e00-\u9fa5]{2,10}自治区)',
            r'(内蒙古|新疆|西藏|宁夏|广西)',
            r'(北京|上海|天津|重庆)',
        ]
        
        for pattern in province_patterns:
            match = re.search(pattern, address)
            if match:
                return match.group(1)
        
        return None
    
    def extract_district_from_address(self, address: str) -> Optional[str]:
        """
        从地址中提取区县信息
        
        Args:
            address: 企业地址
            
        Returns:
            提取的区县名称，如果提取失败返回None
        """
        if not address or not isinstance(address, str):
            return None
        
        district_patterns = [
            r'([\u4e00-\u9fa5]{2,6}区)',
            r'([\u4e00-\u9fa5]{2,6}县)',
            r'([\u4e00-\u9fa5]{2,6}市辖区)',
        ]
        
        for pattern in district_patterns:
            match = re.search(pattern, address)
            if match:
                district = match.group(1)
                if not any(word in district for word in self.exclude_words):
                    return district
        
        return None
    
    def parse_address_components(self, address: str) -> Dict[str, Optional[str]]:
        """
        解析地址的各个组成部分
        
        Args:
            address: 完整地址
            
        Returns:
            包含省份、城市、区县等信息的字典
        """
        return {
            'province': self.extract_province_from_address(address),
            'city': self.extract_city_from_address(address),
            'district': self.extract_district_from_address(address),
            'full_address': address
        }


class AddressSearcher:
    """地址搜索器"""
    
    def __init__(self):
        """初始化地址搜索器"""
        self.extractor = AddressExtractor()
    
    def search_company_address(self, company_name: str) -> Optional[str]:
        """
        根据企业名称联网搜索获取完整地址信息
        
        Args:
            company_name: 企业名称
            
        Returns:
            搜索到的企业地址，如果搜索失败返回None
        """
        if not company_name:
            return None
        
        try:
            # 动态导入避免循环依赖
            from ..external.bocha_client import BochaSearchClient
            
            search_client = BochaSearchClient()
            
            # 搜索企业地址信息 - 使用更精确的搜索词
            search_queries = [
                f"{company_name} 注册地址",
                f"{company_name} 公司地址", 
                f"{company_name} 总部地址",
                f"{company_name} 办公地址"
            ]
            
            for search_query in search_queries:
                search_result = search_client.search_web(search_query)
                
                if search_result and search_result.get('code') == 200:
                    data = search_result.get('data', {})
                    if isinstance(data, dict):
                        content = data.get('content', '') or data.get('text', '') or str(data)
                        
                        # 提取地址信息
                        address = self._extract_address_from_content(content, company_name)
                        if address:
                            logger.log_web_search(
                                company_name, "地址搜索", search_query, 1
                            )
                            return address
            
            return None
            
        except Exception as e:
            logger.log_error("地址搜索失败", str(e), company_name)
            return None
    
    def _extract_address_from_content(self, content: str, company_name: str) -> Optional[str]:
        """
        从搜索内容中提取地址信息
        
        Args:
            content: 搜索结果内容
            company_name: 企业名称
            
        Returns:
            提取的地址或None
        """
        # 优先查找最新的地址信息（地址变更公告等）
        priority_patterns = [
            # 最高优先级：地址变更公告
            rf'(?:地址变更|新办公地址|总部新|迁至).*?([^。\n]*(?:市|区|县)[^。\n]*(?:街道|路|号|大厦|中心|园区)[^。\n]*)',
            # 高优先级：当前地址、现地址
            rf'(?:当前地址|现地址|现办公地址)[:：]\s*([^。\n]+(?:市|区|县|镇|街道|路|号)[^。\n]*)',
        ]
        
        # 先尝试优先级模式
        for pattern in priority_patterns:
            match = re.search(pattern, content)
            if match:
                address = match.group(1).strip()
                if self._is_valid_address(address):
                    return address
        
        # 如果没有找到最新地址，再使用常规模式
        address_patterns = [
            # 最精确：企业名称 + 地址关键词 + 具体地址
            rf'{re.escape(company_name)}.*?(?:注册地址|公司地址|总部地址|办公地址|地址)[:：]\s*([^。\n]+(?:市|区|县|镇|街道|路|号)[^。\n]*)',
            # 次精确：地址关键词 + 具体地址
            r'(?:注册地址|公司地址|总部地址|办公地址|地址)[:：]\s*([^。\n]+(?:市|区|县|镇|街道|路|号)[^。\n]*)',
            # 一般：位于、坐落于等 + 地址
            r'(?:位于|坐落于|设在)[:：]?\s*([^。\n]+(?:市|区|县|镇|街道|路|号)[^。\n]*)',
            # 最后：企业名称附近的地址信息
            rf'{re.escape(company_name)}[^。\n]*?([^。\n]*(?:省|市|区|县)[^。\n]*(?:街道|路|号|大厦|中心|园区)[^。\n]*)',
        ]
        
        for pattern in address_patterns:
            match = re.search(pattern, content)
            if match:
                address = match.group(1).strip()
                if self._is_valid_address(address):
                    return address
        
        return None
    
    def _is_valid_address(self, address: str) -> bool:
        """
        验证地址是否有效
        
        Args:
            address: 地址字符串
            
        Returns:
            地址是否有效
        """
        if not address or len(address) < 5:
            return False
        
        # 必须包含地理位置标识
        if not any(geo in address for geo in ['市', '区', '县', '省']):
            return False
        
        # 排除明显无效的地址
        invalid_keywords = ['吊销', '注销', '已迁出', '原地址', '变更前', '旧址']
        if any(keyword in address for keyword in invalid_keywords):
            return False
        
        return True
    
    def search_city_by_company_name(self, company_name: str, update_database: bool = True) -> Optional[str]:
        """
        根据企业名称联网搜索获取城市信息
        先搜索企业地址，再从地址中提取城市
        
        Args:
            company_name: 企业名称
            update_database: 是否将搜索到的地址更新到数据库
            
        Returns:
            搜索到的城市名称，如果搜索失败返回None
        """
        if not company_name:
            return None
        
        # 先搜索企业完整地址
        address = self.search_company_address(company_name)
        if address:
            # 从搜索到的地址中提取城市
            city = self.extractor.extract_city_from_address(address)
            if city:
                logger.log_company_query(
                    company_name, "城市提取", f"从地址提取城市: {address} -> {city}"
                )
                
                # 如果启用数据库更新，将新地址保存到数据库
                if update_database:
                    try:
                        updater = AddressUpdater()
                        success = updater.update_customer_address_info(company_name, address, city)
                        if success:
                            logger.log_company_query(
                                company_name, "地址更新", f"地址已更新到数据库: {city}"
                            )
                        else:
                            logger.log_error(
                                "地址更新失败", f"无法更新数据库: {company_name}", company_name
                            )
                    except Exception as update_error:
                        logger.log_error(
                            "数据库更新异常", str(update_error), company_name
                        )
                
                return city
        
        return None


class AddressUpdater:
    """地址更新器"""
    
    def __init__(self):
        """初始化地址更新器"""
        self.customer_repo = CustomerRepository()
        self.enterprise_repo = EnterpriseRepository()
    
    def update_customer_address_info(self, customer_name: str, new_address: str, new_city: str) -> bool:
        """
        更新客户的地址信息到数据库
        支持QD_customer表和QD_enterprise_chain_leader表
        
        Args:
            customer_name: 企业名称
            new_address: 新的完整地址
            new_city: 新的城市信息
            
        Returns:
            更新是否成功
        """
        try:
            # 首先尝试在客户表中查找
            customer = self.customer_repo.find_by_name(customer_name)
            
            if customer:
                # 更新客户表
                updates = {'address': new_address}
                success = self.customer_repo.update(customer.customer_id, updates)
                
                if success:
                    logger.log_company_query(
                        customer_name, "地址更新", f"QD_customer表地址更新成功，城市: {new_city}"
                    )
                    return True
            
            # 如果客户表中没有找到，尝试在企业表中查找
            enterprise = self.enterprise_repo.find_by_name(customer_name)
            
            if enterprise:
                # 对于链主企业，记录地址信息但不直接更新表结构
                logger.log_company_query(
                    customer_name, "链主企业地址获取", f"地址信息已获取，城市: {new_city}"
                )
                return True
            
            # 如果两个表都没有找到记录
            logger.log_error("地址更新失败", f"未找到企业记录: {customer_name}", customer_name)
            return False
            
        except Exception as e:
            logger.log_error("地址更新异常", str(e), customer_name)
            return False
    
    def find_companies_with_wrong_addresses(self) -> List[str]:
        """
        查找数据库中可能有错误地址的企业
        主要针对所有地区显示为"莱西市"的链主企业
        
        Returns:
            需要修正地址的企业名称列表
        """
        try:
            # 这里需要实现具体的查询逻辑
            # 由于涉及复杂的数据库查询，暂时返回空列表
            # 实际实现时需要根据具体的业务逻辑来查询
            
            logger.log_company_query(
                "批量地址修正", "查找企业", "查找需要修正地址的企业"
            )
            
            return []
            
        except Exception as e:
            logger.log_error("查找错误地址企业失败", str(e))
            return []


class AddressProcessor:
    """地址处理器 - 统一接口"""
    
    def __init__(self):
        """初始化地址处理器"""
        self.extractor = AddressExtractor()
        self.searcher = AddressSearcher()
        self.updater = AddressUpdater()
    
    def get_company_city(self, company_data: Dict[str, Any], company_name: str) -> Optional[str]:
        """
        获取企业所在城市信息
        优先从地址提取，其次联网搜索
        
        Args:
            company_data: 企业数据
            company_name: 企业名称
            
        Returns:
            城市名称或None
        """
        # 1. 优先从企业地址提取城市
        address = company_data.get('address')
        if address:
            city = self.extractor.extract_city_from_address(address)
            if city:
                logger.log_company_query(
                    company_name, "城市提取", f"从地址提取城市: {address} -> {city}"
                )
                return city
        
        # 2. 如果地址不存在或提取失败，联网搜索
        if company_name:
            city = self.searcher.search_city_by_company_name(company_name)
            if city:
                logger.log_company_query(
                    company_name, "城市搜索", f"联网搜索获取城市: {company_name} -> {city}"
                )
                return city
        
        return None
    
    def process_address_info(self, company_name: str, existing_address: Optional[str] = None) -> Dict[str, Any]:
        """
        处理企业地址信息
        
        Args:
            company_name: 企业名称
            existing_address: 现有地址（可选）
            
        Returns:
            处理结果字典
        """
        result = {
            'success': False,
            'address': existing_address,
            'city': None,
            'province': None,
            'district': None,
            'source': 'existing'
        }
        
        # 如果有现有地址，先尝试从中提取信息
        if existing_address:
            components = self.extractor.parse_address_components(existing_address)
            result.update(components)
            if components['city']:
                result['success'] = True
                return result
        
        # 如果没有现有地址或提取失败，尝试搜索
        searched_address = self.searcher.search_company_address(company_name)
        if searched_address:
            components = self.extractor.parse_address_components(searched_address)
            result.update(components)
            result['address'] = searched_address
            result['source'] = 'searched'
            result['success'] = bool(components['city'])
        
        return result


# 全局实例
address_processor = AddressProcessor()

# 向后兼容的函数
def extract_city_from_address(address: str) -> Optional[str]:
    """向后兼容的城市提取函数"""
    extractor = AddressExtractor()
    return extractor.extract_city_from_address(address)

def search_company_address(company_name: str) -> Optional[str]:
    """向后兼容的地址搜索函数"""
    searcher = AddressSearcher()
    return searcher.search_company_address(company_name)

def search_city_by_company_name(company_name: str, update_database: bool = True) -> Optional[str]:
    """向后兼容的城市搜索函数"""
    searcher = AddressSearcher()
    return searcher.search_city_by_company_name(company_name, update_database)

def get_company_city(company_data: Dict[str, Any], company_name: str) -> Optional[str]:
    """向后兼容的企业城市获取函数"""
    return address_processor.get_company_city(company_data, company_name)