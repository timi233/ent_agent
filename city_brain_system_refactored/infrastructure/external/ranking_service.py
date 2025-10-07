"""
企业排名状态检查服务
用于判断企业是否属于中国五百强或行业前五

优化改进：
- 增加重试机制（最多3次）
- 超时控制（单次搜索10秒）
- 结构容错（解析description/title/snippets多来源）
- 日志记录便于调试
"""

import sys
import os
import time
import logging
from typing import Optional, Dict, Any, List
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from . import search_web, generate_summary

logger = logging.getLogger(__name__)

# 配置常量
MAX_RETRIES = 3
SEARCH_TIMEOUT = 10  # 秒
MAX_SEARCH_RESULTS = 5


def get_company_ranking_status(company_name, industry_name=None):
    """
    获取企业排名状态（优化版：带重试和超时）

    Args:
        company_name (str): 企业名称
        industry_name (str): 行业名称，可选

    Returns:
        str: 企业地位描述
    """
    try:
        logger.info(f"开始查询企业排名状态: {company_name}, 行业: {industry_name or '未指定'}")

        # 首先检查是否为中国五百强
        china_500_status = check_china_top_500(company_name)
        if china_500_status:
            logger.info(f"找到中国五百强信息: {china_500_status}")
            return china_500_status

        # 如果不是中国五百强，检查行业排名
        if industry_name:
            industry_ranking = check_industry_ranking(company_name, industry_name)
            if industry_ranking:
                logger.info(f"找到行业排名信息: {industry_ranking}")
                return industry_ranking

        logger.warning(f"未找到排名信息: {company_name}")
        return "暂无排名信息"

    except Exception as e:
        logger.error(f"获取企业排名状态失败: {e}", exc_info=True)
        return "暂无排名信息"


def check_china_top_500(company_name):
    """
    检查企业是否属于中国五百强（优化版：带重试和多来源解析）

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
            logger.debug(f"查询中国五百强: {query}")

            # 带重试的搜索
            search_results = _search_with_retry(query)

            if not search_results:
                continue

            # 提取所有可能的内容来源（容错）
            contents = _extract_search_contents(search_results, company_name)

            if not contents:
                continue

            # 检查是否包含中国五百强相关关键词
            keywords = ['中国500强', '中国五百强', '财富中国500强', '财富500强']

            for content_item in contents:
                content_text = content_item['text'].lower()

                for keyword in keywords:
                    if keyword.lower() in content_text and company_name.lower() in content_text:
                        logger.info(f"在内容中找到中国五百强关键词: {keyword}")
                        # 使用LLM提取具体排名信息
                        ranking_info = extract_china_500_ranking(content_item['text'], company_name)
                        if ranking_info:
                            return f"中国五百强 - {ranking_info}"
                        else:
                            return "中国五百强企业"

        return None

    except Exception as e:
        logger.error(f"检查中国五百强状态失败: {e}", exc_info=True)
        return None


def check_industry_ranking(company_name, industry_name):
    """
    检查企业在行业内的排名（优化版：带重试和多来源解析）

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
            logger.debug(f"查询行业排名: {query}")

            # 带重试的搜索
            search_results = _search_with_retry(query)

            if not search_results:
                continue

            # 提取所有可能的内容来源（容错）
            contents = _extract_search_contents(search_results, company_name)

            if not contents:
                continue

            # 检查是否包含行业排名相关关键词
            ranking_keywords = ['前五', '前5', '第一', '第二', '第三', '第四', '第五',
                              '龙头', '领军', '领先', '排名第', '位列第']

            for content_item in contents:
                content_text = content_item['text']

                if company_name in content_text:
                    for keyword in ranking_keywords:
                        if keyword in content_text:
                            logger.info(f"在内容中找到行业排名关键词: {keyword}")
                            # 使用LLM提取具体排名信息
                            ranking_info = extract_industry_ranking(content_text, company_name, industry_name)
                            if ranking_info:
                                return ranking_info

        return None

    except Exception as e:
        logger.error(f"检查行业排名失败: {e}", exc_info=True)
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


# ==================== 辅助函数（优化增强）====================

def _search_with_retry(query: str, max_retries: int = MAX_RETRIES) -> Optional[Dict[str, Any]]:
    """
    带重试机制的搜索函数

    Args:
        query: 搜索查询
        max_retries: 最大重试次数

    Returns:
        搜索结果或None
    """
    for attempt in range(max_retries):
        try:
            logger.debug(f"搜索尝试 {attempt + 1}/{max_retries}: {query}")

            # 设置超时
            import signal

            def timeout_handler(signum, frame):
                raise TimeoutError("搜索超时")

            # 仅在Linux/Unix系统上使用signal
            if hasattr(signal, 'SIGALRM'):
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(SEARCH_TIMEOUT)

            try:
                result = search_web(query)

                if hasattr(signal, 'SIGALRM'):
                    signal.alarm(0)  # 取消超时

                if result:
                    logger.debug(f"搜索成功: {query}")
                    return result
                else:
                    logger.warning(f"搜索返回空结果: {query}")

            except TimeoutError:
                logger.warning(f"搜索超时 ({SEARCH_TIMEOUT}秒): {query}")
                if hasattr(signal, 'SIGALRM'):
                    signal.alarm(0)

        except Exception as e:
            logger.warning(f"搜索失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(1)  # 重试前等待1秒

    logger.error(f"搜索失败，已达最大重试次数: {query}")
    return None


def _extract_search_contents(search_results: Dict[str, Any], company_name: str) -> List[Dict[str, str]]:
    """
    从搜索结果中提取所有可能的内容（多来源容错）

    Args:
        search_results: 搜索结果
        company_name: 企业名称（用于过滤）

    Returns:
        内容列表，每个元素包含 {'text': str, 'source': str}
    """
    contents = []

    try:
        if not search_results or 'data' not in search_results:
            return contents

        data = search_results['data']
        web_pages = data.get('webPages', {})

        if 'value' not in web_pages:
            return contents

        # 遍历搜索结果
        for idx, result in enumerate(web_pages['value'][:MAX_SEARCH_RESULTS]):
            # 提取多个来源的内容
            title = result.get('name', '') or result.get('title', '')
            snippet = result.get('snippet', '') or result.get('description', '')
            url = result.get('url', '')

            # 合并所有文本内容
            combined_text = f"{title} {snippet}".strip()

            if combined_text and company_name in combined_text:
                contents.append({
                    'text': combined_text,
                    'source': f"result_{idx}",
                    'url': url,
                    'title': title,
                    'snippet': snippet
                })
                logger.debug(f"提取到内容 (来源: result_{idx}): {combined_text[:100]}...")

        logger.info(f"成功提取 {len(contents)} 个相关内容")

    except Exception as e:
        logger.error(f"提取搜索内容失败: {e}", exc_info=True)

    return contents