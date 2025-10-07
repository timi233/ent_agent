"""
企业排名状态检查工具
用于判断企业是否属于中国五百强或行业前五
"""

from api.bocha_client import search_web
from api.llm_client import generate_summary
import re
import json

def get_company_ranking_status(company_name, industry_name=None):
    """
    获取企业排名状态
    
    Args:
        company_name (str): 企业名称
        industry_name (str): 行业名称，可选
    
    Returns:
        str: 企业地位描述
    """
    try:
        # 首先检查是否为中国五百强
        china_500_status = check_china_top_500(company_name)
        if china_500_status:
            return china_500_status
        
        # 如果不是中国五百强，检查行业排名
        if industry_name:
            industry_ranking = check_industry_ranking(company_name, industry_name)
            if industry_ranking:
                return industry_ranking
        
        return "暂无排名信息"
        
    except Exception as e:
        print(f"获取企业排名状态失败: {e}")
        return "暂无排名信息"

def check_china_top_500(company_name):
    """
    检查企业是否属于中国五百强
    
    Args:
        company_name (str): 企业名称
    
    Returns:
        str: 如果是中国五百强返回具体信息，否则返回None
    """
    try:
        # 搜索中国五百强相关信息
        search_queries = [
            f"{company_name} 中国五百强",
            f"{company_name} 中国500强企业",
            f"{company_name} 财富中国500强"
        ]
        
        for query in search_queries:
            search_results = search_web(query)
            
            if search_results and 'data' in search_results:
                web_pages = search_results['data'].get('webPages', {})
                if 'value' in web_pages:
                    # 分析搜索结果
                    for result in web_pages['value'][:5]:
                        title = result.get('name', '').lower()
                        snippet = result.get('snippet', '').lower()
                        
                        # 检查是否包含中国五百强相关关键词
                        keywords = ['中国500强', '中国五百强', '财富中国500强', '财富500强']
                        content = f"{title} {snippet}"
                        
                        for keyword in keywords:
                            if keyword.lower() in content and company_name in content:
                                # 使用LLM提取具体排名信息
                                ranking_info = extract_china_500_ranking(content, company_name)
                                if ranking_info:
                                    return f"中国五百强 - {ranking_info}"
                                else:
                                    return "中国五百强企业"
        
        return None
        
    except Exception as e:
        print(f"检查中国五百强状态失败: {e}")
        return None

def check_industry_ranking(company_name, industry_name):
    """
    检查企业在行业内的排名
    
    Args:
        company_name (str): 企业名称
        industry_name (str): 行业名称
    
    Returns:
        str: 如果是行业前五返回具体信息，否则返回None
    """
    try:
        # 搜索行业排名相关信息
        search_queries = [
            f"{company_name} {industry_name} 行业排名",
            f"{company_name} {industry_name} 龙头企业",
            f"{industry_name} 行业前五 {company_name}",
            f"{industry_name} 领军企业 {company_name}"
        ]
        
        for query in search_queries:
            search_results = search_web(query)
            
            if search_results and 'data' in search_results:
                web_pages = search_results['data'].get('webPages', {})
                if 'value' in web_pages:
                    # 分析搜索结果
                    for result in web_pages['value'][:5]:
                        title = result.get('name', '').lower()
                        snippet = result.get('snippet', '').lower()
                        content = f"{title} {snippet}"
                        
                        # 检查是否包含行业排名相关关键词
                        ranking_keywords = ['前五', '前5', '第一', '第二', '第三', '第四', '第五', 
                                          '龙头', '领军', '领先', '排名第', '位列第']
                        
                        if company_name in content:
                            for keyword in ranking_keywords:
                                if keyword in content:
                                    # 使用LLM提取具体排名信息
                                    ranking_info = extract_industry_ranking(content, company_name, industry_name)
                                    if ranking_info:
                                        return ranking_info
        
        return None
        
    except Exception as e:
        print(f"检查行业排名失败: {e}")
        return None

def extract_china_500_ranking(content, company_name):
    """
    从搜索内容中提取中国五百强排名信息
    
    Args:
        content (str): 搜索结果内容
        company_name (str): 企业名称
    
    Returns:
        str: 排名信息
    """
    try:
        prompt = f"""
        请从以下内容中提取关于"{company_name}"在中国五百强中的具体排名信息：

        内容：{content}

        请只返回具体的排名信息，例如："第123名"、"排名第45位"等。
        如果没有找到具体排名，请返回"具体排名未知"。
        不要返回其他解释性文字。
        """
        
        ranking_info = generate_summary(prompt)
        
        # 简单验证返回结果
        if ranking_info and any(keyword in ranking_info for keyword in ['第', '排名', '位']):
            return ranking_info.strip()
        
        return None
        
    except Exception as e:
        print(f"提取中国五百强排名信息失败: {e}")
        return None

def extract_industry_ranking(content, company_name, industry_name):
    """
    从搜索内容中提取行业排名信息
    
    Args:
        content (str): 搜索结果内容
        company_name (str): 企业名称
        industry_name (str): 行业名称
    
    Returns:
        str: 排名信息
    """
    try:
        prompt = f"""
        请从以下内容中分析"{company_name}"在"{industry_name}"行业中的地位和排名：

        内容：{content}

        请判断该企业是否属于行业前五，并返回相应的地位描述。
        如果是行业前五，请返回类似"行业前五"、"行业第二"、"行业龙头"等描述。
        如果不是前五但有其他重要地位，请返回相应描述。
        如果无法确定，请返回"行业地位未知"。
        不要返回其他解释性文字。
        """
        
        ranking_info = generate_summary(prompt)
        
        # 验证返回结果是否包含行业排名信息
        if ranking_info and any(keyword in ranking_info for keyword in 
                               ['行业前', '行业第', '龙头', '领军', '领先']):
            return ranking_info.strip()
        
        return None
        
    except Exception as e:
        print(f"提取行业排名信息失败: {e}")
        return None

def validate_ranking_info(ranking_info, company_name):
    """
    验证排名信息的合理性
    
    Args:
        ranking_info (str): 排名信息
        company_name (str): 企业名称
    
    Returns:
        bool: 是否合理
    """
    if not ranking_info:
        return False
    
    # 检查是否包含企业名称（避免错误匹配）
    if company_name not in ranking_info:
        return False
    
    # 检查是否包含合理的排名关键词
    valid_keywords = ['第', '排名', '前', '龙头', '领军', '领先', '五百强', '500强']
    if not any(keyword in ranking_info for keyword in valid_keywords):
        return False
    
    return True