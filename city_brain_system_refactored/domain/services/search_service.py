"""
搜索服务 - 处理网络搜索和公司名称推断

负责：
- 网络搜索企业信息
- 公司名称推断和补全
- 搜索结果信息提取
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from infrastructure.external import search_web
from infrastructure.utils.text_processor import extract_company_name, extract_company_info_from_search_results


class SearchService:
    """搜索服务类"""
    
    def __init__(self):
        """初始化搜索服务"""
        pass
    
    def search_company_info(self, company_name):
        """
        搜索企业信息
        
        Args:
            company_name (str): 企业名称
            
        Returns:
            dict: 搜索结果和提取的企业信息
        """
        try:
            # 联网搜索公司信息
            search_query = f"{company_name} 公司信息"
            search_results = search_web(search_query)
            
            # 提取搜索结果中的信息
            company_info = extract_company_info_from_search_results(search_results)
            
            return {
                "status": "success",
                "data": company_info,
                "source": "web_search"
            }
        except Exception as e:
            print(f"搜索企业信息失败: {e}")
            return {
                "status": "error",
                "message": f"搜索企业信息失败: {str(e)}",
                "data": None
            }
    
    def infer_company_name_from_search(self, user_input):
        """
        通过网络搜索推断公司名称（当完全无法提取时使用）
        
        Args:
            user_input (str): 用户输入的文本
            
        Returns:
            str or None: 推断出的公司名称，如果失败返回None
        """
        try:
            # 尝试通过搜索用户输入来推断公司名称
            search_results = search_web(user_input)
            
            if search_results and 'data' in search_results and 'webPages' in search_results['data']:
                web_pages = search_results['data']['webPages']
                if 'value' in web_pages and len(web_pages['value']) > 0:
                    # 检查前几个搜索结果，看是否能提取公司名称
                    for result in web_pages['value'][:3]:  # 检查前3个结果
                        title = result.get('name', '')
                        snippet = result.get('snippet', '')
                        
                        # 尝试从标题中提取公司名称
                        title_extraction = extract_company_name(title)
                        if title_extraction and title_extraction['is_complete']:
                            return title_extraction['name']
                        
                        # 尝试从摘要中提取公司名称
                        snippet_extraction = extract_company_name(snippet)
                        if snippet_extraction and snippet_extraction['is_complete']:
                            return snippet_extraction['name']
            
            return None
        except Exception as e:
            print(f"通过搜索推断公司名称时出错: {e}")
            return None
    
    def infer_complete_company_name_from_search(self, incomplete_name):
        """
        通过网络搜索获取完整的公司名称（当提取到不完整名称时使用）
        
        Args:
            incomplete_name (str): 不完整的公司名称
            
        Returns:
            str or None: 完整的公司名称，如果失败返回None
        """
        try:
            # 搜索不完整的公司名称，尝试找到完整名称
            search_query = f"{incomplete_name} 公司 官网"
            search_results = search_web(search_query)
            
            if search_results and 'data' in search_results and 'webPages' in search_results['data']:
                web_pages = search_results['data']['webPages']
                if 'value' in web_pages and len(web_pages['value']) > 0:
                    # 检查前几个搜索结果，寻找完整的公司名称
                    for result in web_pages['value'][:5]:  # 检查前5个结果
                        title = result.get('name', '')
                        snippet = result.get('snippet', '')
                        url = result.get('url', '')
                        
                        # 优先从官网标题中提取
                        if '官网' in title or 'www.' in url:
                            title_extraction = extract_company_name(title)
                            if title_extraction and title_extraction['is_complete']:
                                # 验证是否包含原始名称
                                if incomplete_name in title_extraction['name']:
                                    return title_extraction['name']
                        
                        # 从摘要中提取
                        snippet_extraction = extract_company_name(snippet)
                        if snippet_extraction and snippet_extraction['is_complete']:
                            # 验证是否包含原始名称
                            if incomplete_name in snippet_extraction['name']:
                                return snippet_extraction['name']
            
            return None
        except Exception as e:
            print(f"通过搜索获取完整公司名称时出错: {e}")
            return None
    
    def extract_company_name_from_input(self, user_input):
        """
        从用户输入中提取公司名称
        
        Args:
            user_input (str): 用户输入的文本
            
        Returns:
            dict: 包含提取结果的字典
                - name: 公司名称
                - is_complete: 是否为完整名称
                - status: 提取状态
        """
        try:
            # 1. 尝试本地提取
            extraction_result = extract_company_name(user_input)
            
            if not extraction_result:
                # 如果本地无法提取公司名称，尝试通过网络搜索推断
                complete_name = self.infer_company_name_from_search(user_input)
                if not complete_name:
                    return {
                        "status": "error",
                        "message": "无法从输入中提取公司名称，请提供更明确的公司信息",
                        "name": None,
                        "is_complete": False
                    }
                return {
                    "status": "success",
                    "name": complete_name,
                    "is_complete": True,
                    "source": "search_inference"
                }
            else:
                company_name = extraction_result['name']
                is_complete = extraction_result['is_complete']
                
                # 如果提取到的名称不完整，尝试通过搜索获取完整名称
                if not is_complete:
                    complete_name = self.infer_complete_company_name_from_search(company_name)
                    if complete_name:
                        return {
                            "status": "success",
                            "name": complete_name,
                            "is_complete": True,
                            "source": "search_completion"
                        }
                
                return {
                    "status": "success",
                    "name": company_name,
                    "is_complete": is_complete,
                    "source": "local_extraction"
                }
                
        except Exception as e:
            print(f"提取公司名称时出错: {e}")
            return {
                "status": "error",
                "message": f"提取公司名称时出错: {str(e)}",
                "name": None,
                "is_complete": False
            }