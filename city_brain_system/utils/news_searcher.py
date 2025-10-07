"""
企业新闻资讯搜索工具
"""
from api.bocha_client import search_web
from api.llm_client import generate_summary
import json
import re

def get_company_business_news(company_name):
    """
    获取企业最近的商业新闻资讯
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
            import re
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