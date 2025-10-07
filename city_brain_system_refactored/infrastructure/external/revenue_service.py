"""
企业营收信息搜索服务
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from . import search_web, generate_summary


def get_company_revenue_info(company_name):
    """
    获取企业近三年营收情况
    
    Args:
        company_name (str): 企业名称
    
    Returns:
        str: 营收信息描述
    """
    try:
        # 搜索企业财务信息
        search_queries = [
            f"{company_name} 营收 财报 2021 2022 2023",
            f"{company_name} 年报 营业收入",
            f"{company_name} 财务数据 营收"
        ]
        
        revenue_data = []
        
        for query in search_queries:
            search_results = search_web(query)
            
            if search_results and 'data' in search_results:
                web_pages = search_results['data'].get('webPages', {})
                if 'value' in web_pages:
                    # 提取前几个相关结果
                    for result in web_pages['value'][:3]:
                        title = result.get('name', '')
                        snippet = result.get('snippet', '')
                        url = result.get('url', '')
                        
                        # 检查是否包含财务相关信息
                        if any(keyword in f"{title} {snippet}".lower() for keyword in 
                               ['营收', '营业收入', '财报', '年报', '亿元', '万元', '收入']):
                            revenue_data.append({
                                'title': title,
                                'snippet': snippet,
                                'url': url
                            })
        
        if revenue_data:
            # 使用LLM分析和总结营收信息
            revenue_summary = analyze_revenue_data(revenue_data, company_name)
            return revenue_summary
        else:
            return "暂无营收数据"
            
    except Exception as e:
        print(f"获取营收信息失败: {e}")
        return "暂无营收数据"


def analyze_revenue_data(revenue_data, company_name):
    """
    使用LLM分析营收数据
    
    Args:
        revenue_data (list): 营收相关的搜索结果
        company_name (str): 企业名称
    
    Returns:
        str: 营收分析结果
    """
    try:
        # 构建分析提示
        data_text = ""
        for i, data in enumerate(revenue_data[:5], 1):
            data_text += f"{i}. 标题: {data['title']}\n"
            data_text += f"   内容: {data['snippet']}\n\n"
        
        prompt = f"""
        请基于以下搜索结果，分析和总结"{company_name}"近三年（2021-2023年）的营收情况：

        搜索结果：
        {data_text}

        请提供简洁的营收总结，包括：
        1. 近三年营收数据（如果有具体数字）
        2. 营收趋势（增长/下降/稳定）
        3. 如果没有具体数据，请说明"暂无详细营收数据"

        请用中文回答，保持简洁明了。
        """
        
        revenue_summary = generate_summary(prompt)
        return revenue_summary if revenue_summary else "暂无营收数据"
        
    except Exception as e:
        print(f"分析营收数据失败: {e}")
        return "暂无营收数据"