"""
文本处理工具
重构自原有的 utils/text_extractor.py，增强文本提取和处理功能
"""
import re
from typing import Optional, Dict, Any, List


class CompanyNameExtractor:
    """企业名称提取器"""
    
    def __init__(self):
        """初始化企业名称提取器"""
        # 完整的公司名称模式（带有公司后缀）
        self.complete_patterns = [
            r'([\u4e00-\u9fa5]{2,20}(?:股份有限公司|有限责任公司|有限公司|股份公司|集团有限公司|集团股份有限公司|集团公司|公司|集团|企业|厂|店|中心|协会|学会))',
            r'((?:阿里巴巴|腾讯|百度|京东|华为|小米|美团|滴滴|字节跳动)[\u4e00-\u9fa5]{0,10}(?:股份有限公司|有限责任公司|有限公司|股份公司|集团有限公司|集团股份有限公司|集团公司|公司|集团))'
        ]
        
        # 不完整的公司名称模式（简称或品牌名）
        self.incomplete_patterns = [
            # 知名品牌名称（不带后缀，被认为是不完整的）
            r'(青岛啤酒|茅台|五粮液|中国平安|招商银行|工商银行|建设银行|中国银行|农业银行|中国石油|中国石化|中国移动|中国联通|中国电信|格力电器|美的集团|海尔智家|比亚迪|长城汽车|吉利汽车|万科|恒大|碧桂园|中国建筑|中国中铁|中国铁建)',
            # 通用中文企业名称（2-10个汉字，不带公司后缀）
            r'([\u4e00-\u9fa5]{2,10})'
        ]
        
        # 排除词汇
        self.exclude_words = [
            '查询', '信息', '请问', '什么', '怎么', '哪里', '为什么', '如何', 
            '谢谢', '你好', '公司', '企业', '集团', '分析', '报告', '数据'
        ]
        
        # 完整公司名称后缀
        self.complete_suffixes = [
            '股份有限公司', '有限责任公司', '有限公司', '股份公司', '集团有限公司', 
            '集团股份有限公司', '集团公司', '公司', '集团', '企业', '厂', '店', 
            '中心', '协会', '学会'
        ]
    
    def extract_company_name(self, text: str) -> Optional[Dict[str, Any]]:
        """
        从文本中提取公司名称
        优先提取完整的公司名称，如果只能提取到简称则标记为不完整
        
        Args:
            text: 输入文本
            
        Returns:
            包含企业名称和完整性标识的字典，如果未找到返回None
        """
        if not text or not isinstance(text, str):
            return None
        
        # 先尝试匹配完整的公司名称
        for pattern in self.complete_patterns:
            match = re.search(pattern, text)
            if match:
                return {
                    'name': match.group(1),
                    'is_complete': True,
                    'confidence': 0.9
                }
        
        # 如果没有找到完整名称，尝试匹配简称或品牌名
        for i, pattern in enumerate(self.incomplete_patterns):
            match = re.search(pattern, text)
            if match:
                company_name = match.group(1)
                
                # 如果是通用模式匹配的，需要进一步验证
                if i == len(self.incomplete_patterns) - 1:  # 最后一个是通用模式
                    if company_name in self.exclude_words:
                        continue
                    
                    return {
                        'name': company_name,
                        'is_complete': False,
                        'confidence': 0.5
                    }
                else:
                    return {
                        'name': company_name,
                        'is_complete': False,
                        'confidence': 0.7
                    }
        
        return None
    
    def is_complete_company_name(self, company_name: str) -> bool:
        """
        判断公司名称是否完整（是否包含公司后缀）
        
        Args:
            company_name: 企业名称
            
        Returns:
            是否为完整的企业名称
        """
        if not company_name:
            return False
        
        for suffix in self.complete_suffixes:
            if company_name.endswith(suffix):
                return True
        
        return False
    
    def normalize_company_name(self, company_name: str) -> str:
        """
        标准化企业名称
        
        Args:
            company_name: 原始企业名称
            
        Returns:
            标准化后的企业名称
        """
        if not company_name:
            return ""
        
        # 去除首尾空格
        normalized = company_name.strip()
        
        # 去除多余的空格
        normalized = re.sub(r'\s+', '', normalized)
        
        # 统一括号格式
        normalized = normalized.replace('（', '(').replace('）', ')')
        
        return normalized
    
    def extract_multiple_companies(self, text: str) -> List[Dict[str, Any]]:
        """
        从文本中提取多个企业名称
        
        Args:
            text: 输入文本
            
        Returns:
            企业名称列表
        """
        companies = []
        
        # 使用所有模式进行匹配
        all_patterns = self.complete_patterns + self.incomplete_patterns
        
        for pattern in all_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                company_name = match.group(1)
                
                # 检查是否已经存在
                if not any(c['name'] == company_name for c in companies):
                    is_complete = self.is_complete_company_name(company_name)
                    companies.append({
                        'name': company_name,
                        'is_complete': is_complete,
                        'confidence': 0.9 if is_complete else 0.6
                    })
        
        return companies


class SearchResultProcessor:
    """搜索结果处理器"""
    
    def extract_company_info_from_search_results(self, search_results: Dict[str, Any]) -> Dict[str, str]:
        """
        从搜索结果中提取公司信息
        
        Args:
            search_results: 搜索结果数据
            
        Returns:
            提取的企业信息字典
        """
        company_info = {
            'name': '',
            'description': '',
            'website': '',
            'industry': '',
            'address': ''
        }
        
        if not search_results:
            return company_info
        
        try:
            # 处理博查AI搜索结果格式
            if 'data' in search_results:
                data = search_results['data']
                
                # 处理网页搜索结果
                if 'webPages' in data and 'value' in data['webPages']:
                    web_pages = data['webPages']['value']
                    if web_pages:
                        first_result = web_pages[0]
                        company_info['name'] = first_result.get('name', '')
                        company_info['description'] = first_result.get('snippet', '')
                        company_info['website'] = first_result.get('url', '')
                
                # 处理文本内容
                if 'content' in data:
                    content = data['content']
                    company_info['description'] = content[:500] if content else ''
                    
                    # 尝试从内容中提取行业信息
                    industry = self._extract_industry_from_text(content)
                    if industry:
                        company_info['industry'] = industry
                    
                    # 尝试从内容中提取地址信息
                    address = self._extract_address_from_text(content)
                    if address:
                        company_info['address'] = address
        
        except Exception as e:
            # 记录错误但不抛出异常
            pass
        
        return company_info
    
    def _extract_industry_from_text(self, text: str) -> Optional[str]:
        """从文本中提取行业信息"""
        if not text:
            return None
        
        industry_patterns = [
            r'(?:行业|产业|领域)[:：]\s*([^。\n，,]{2,20})',
            r'(?:从事|经营|主营)[:：]?\s*([^。\n，,]{2,30})',
            r'(?:属于|隶属)[:：]?\s*([^。\n，,]{2,20})(?:行业|产业)'
        ]
        
        for pattern in industry_patterns:
            match = re.search(pattern, text)
            if match:
                industry = match.group(1).strip()
                if len(industry) > 1 and industry not in ['业务', '服务', '产品']:
                    return industry
        
        return None
    
    def _extract_address_from_text(self, text: str) -> Optional[str]:
        """从文本中提取地址信息"""
        if not text:
            return None
        
        address_patterns = [
            r'(?:地址|位于|坐落于)[:：]\s*([^。\n]+(?:市|区|县|镇|街道|路|号)[^。\n]*)',
            r'(?:注册地|总部|办公地)[:：]\s*([^。\n]+(?:市|区|县|镇|街道|路|号)[^。\n]*)'
        ]
        
        for pattern in address_patterns:
            match = re.search(pattern, text)
            if match:
                address = match.group(1).strip()
                if len(address) > 5:
                    return address
        
        return None


# 全局实例
company_name_extractor = CompanyNameExtractor()
search_result_processor = SearchResultProcessor()

# 向后兼容的函数
def extract_company_name(text: str) -> Optional[Dict[str, Any]]:
    """向后兼容的企业名称提取函数"""
    return company_name_extractor.extract_company_name(text)

def is_complete_company_name(company_name: str) -> bool:
    """向后兼容的企业名称完整性检查函数"""
    return company_name_extractor.is_complete_company_name(company_name)

def extract_company_info_from_search_results(search_results: Dict[str, Any]) -> Dict[str, str]:
    """向后兼容的搜索结果处理函数"""
    return search_result_processor.extract_company_info_from_search_results(search_results)


def get_company_industry(company_name: str, address: str = None) -> Optional[str]:
    """
    获取企业行业信息的主函数
    
    Args:
        company_name: 企业名称
        address: 企业地址（可选）
        
    Returns:
        企业行业信息，如果获取失败返回None
    """
    try:
        # 首先尝试从公司名称直接推断
        if '啤酒' in company_name:
            return '食品饮料制造业'
        
        # 如果无法直接推断，进行联网搜索
        from infrastructure.external import search_web, generate_summary
        
        search_query = f"{company_name} 行业 主营业务"
        search_results = search_web(search_query)
        
        if search_results and 'data' in search_results:
            web_pages = search_results['data'].get('webPages', {})
            if 'value' in web_pages and web_pages['value']:
                # 提取前几个搜索结果的内容
                content_parts = []
                for result in web_pages['value'][:3]:
                    title = result.get('name', '')
                    snippet = result.get('snippet', '')
                    content_parts.append(f"{title} {snippet}")
                
                combined_content = " ".join(content_parts)
                
                # 使用LLM分析行业信息
                prompt = f"""
                请从以下内容中提取"{company_name}"的所属行业：
                
                内容：{combined_content}
                
                请只返回具体的行业名称，例如："制造业"、"金融业"、"互联网服务业"等。
                如果无法确定，请返回"未知行业"。
                不要返回其他解释性文字。
                """
                
                industry = generate_summary(prompt)
                if industry and industry != "未知行业":
                    print(f"通过联网搜索获取行业信息: {industry}")
                    return industry.strip()
        
        return None
        
    except Exception as e:
        print(f"获取企业行业信息失败: {e}")
        return None