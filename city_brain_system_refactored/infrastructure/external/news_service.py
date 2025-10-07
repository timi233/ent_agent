"""
企业新闻资讯搜索服务
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from . import search_web, generate_summary
import re


def get_company_business_news(company_name):
    """
    获取企业最近的商业新闻资讯
    
    Args:
        company_name (str): 企业名称
        
    Returns:
        dict: 包含新闻内容和来源的字典
    """
    try:
        # 搜索企业商业新闻
        search_query = f"{company_name} 新闻 订单 产品 合作 投资 业务 最新"
        search_results = search_web(search_query)
        
        if search_results and search_results.get('data'):
            # 使用LLM处理新闻信息并生成带引用的描述
            prompt = f"""
            请基于以下搜索结果，为{company_name}生成最近的商业新闻摘要。
            
            重点关注：
            1. 新的大订单或合作协议
            2. 新产品发布或技术创新
            3. 业务扩展或投资动态
            4. 其他重要商业动态
            
            搜索结果：{search_results['data']}
            
            请按以下格式输出：
            ## 最新商业动态
            
            ### 重要订单与合作
            - [具体内容]【1】
            
            ### 产品与技术创新  
            - [具体内容]【2】
            
            ### 业务发展动态
            - [具体内容]【3】
            
            ## 参考来源
            【1】[来源标题] - [来源链接]
            【2】[来源标题] - [来源链接]  
            【3】[来源标题] - [来源链接]
            
            如果没有找到相关新闻，请返回"暂无最新商业资讯"
            """
            
            news_summary = generate_summary(prompt)
            
            # 解析新闻摘要和引用
            return {
                "content": news_summary,
                "sources": extract_sources_from_search(search_results)
            }
        else:
            return {
                "content": "暂无最新商业资讯",
                "sources": []
            }
            
    except Exception as e:
        print(f"获取企业新闻失败: {e}")
        return {
            "content": "暂无最新商业资讯", 
            "sources": []
        }


def extract_sources_from_search(search_results):
    """
    从搜索结果中提取来源信息
    
    Args:
        search_results (dict): 搜索结果
        
    Returns:
        list: 来源信息列表
    """
    sources = []
    try:
        data = search_results.get('data')
        if isinstance(data, dict) and 'webPages' in data:
            # 博查API返回的字典格式
            web_pages = data.get('webPages', {}).get('value', [])
            for i, item in enumerate(web_pages[:5], 1):  # 最多5个来源
                if isinstance(item, dict):
                    title = item.get('name', item.get('title', f'来源{i}'))
                    url = item.get('url', '#')
                    snippet = item.get('snippet', item.get('summary', ''))
                    sources.append({
                        "id": i,
                        "title": title,
                        "url": url,
                        "snippet": snippet[:100] + '...' if len(snippet) > 100 else snippet
                    })
        elif isinstance(data, list):
            # 列表格式：直接提取每个项目的标题和URL
            for i, item in enumerate(data[:5], 1):  # 最多5个来源
                if isinstance(item, dict):
                    title = item.get('title', f'来源{i}')
                    url = item.get('url', item.get('link', '#'))
                    sources.append({
                        "id": i,
                        "title": title,
                        "url": url
                    })
        elif isinstance(data, str):
            # 字符串格式：尝试解析HTML或文本内容中的链接
            # 查找URL模式
            url_pattern = r'https?://[^\s<>\"\']+'
            urls = re.findall(url_pattern, data)
            
            # 查找标题模式（在URL前的文本）
            for i, url in enumerate(urls[:5], 1):
                # 尝试从URL中提取域名作为标题
                domain = re.search(r'https?://([^/]+)', url)
                title = domain.group(1) if domain else f'来源{i}'
                sources.append({
                    "id": i,
                    "title": title,
                    "url": url
                })
            
            # 如果没有找到URL，创建默认引用
            if not sources:
                sources.append({
                    "id": 1,
                    "title": f"{search_results.get('query', '搜索结果')}",
                    "url": "#"
                })
    except Exception as e:
        print(f"提取来源信息失败: {e}")
    
    return sources


def get_company_latest_news(company_name, news_type="all"):
    """
    获取企业最新新闻（按类型分类）
    
    Args:
        company_name (str): 企业名称
        news_type (str): 新闻类型 ("all", "financial", "product", "cooperation")
        
    Returns:
        dict: 分类的新闻信息
    """
    try:
        news_queries = {
            "financial": f"{company_name} 财报 业绩 营收 利润",
            "product": f"{company_name} 新产品 技术 创新 发布",
            "cooperation": f"{company_name} 合作 协议 签约 合同",
            "all": f"{company_name} 最新新闻 动态"
        }
        
        query = news_queries.get(news_type, news_queries["all"])
        search_results = search_web(query)
        
        if search_results and search_results.get('data'):
            # 根据新闻类型生成不同的分析提示
            type_prompts = {
                "financial": "请重点关注财务数据、业绩表现、营收情况等财务相关信息",
                "product": "请重点关注新产品发布、技术创新、研发成果等产品相关信息",
                "cooperation": "请重点关注合作协议、战略联盟、商业合同等合作相关信息",
                "all": "请全面分析各类商业动态"
            }
            
            prompt = f"""
            请基于以下搜索结果，为{company_name}生成{news_type}类型的新闻摘要。
            
            分析重点：{type_prompts.get(news_type, type_prompts["all"])}
            
            搜索结果：{search_results['data']}
            
            请提供简洁明了的新闻摘要，如果没有找到相关新闻，请返回"暂无相关资讯"。
            """
            
            news_summary = generate_summary(prompt)
            
            return {
                "type": news_type,
                "content": news_summary,
                "sources": extract_sources_from_search(search_results)
            }
        else:
            return {
                "type": news_type,
                "content": "暂无相关资讯",
                "sources": []
            }
            
    except Exception as e:
        print(f"获取{news_type}类型新闻失败: {e}")
        return {
            "type": news_type,
            "content": "暂无相关资讯",
            "sources": []
        }