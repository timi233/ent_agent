#!/usr/bin/env python3
"""
企业信息爬虫 V2
使用博查AI进行企业搜索
"""
import logging
from typing import Dict, Any, Optional
import time
import json
import os
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)


class CallTrace:
    """调用链路追踪"""

    def __init__(self, trace_id: str = None):
        self.trace_id = trace_id or uuid.uuid4().hex
        self.steps = []

    def add_step(self, step_name: str, input_data: Any, output_data: Any,
                  elapsed: float, success: bool, error: str = None):
        """记录一个步骤"""
        self.steps.append({
            'step_name': step_name,
            'timestamp': datetime.now().isoformat(),
            'input': input_data,
            'output': output_data,
            'elapsed': elapsed,
            'success': success,
            'error': error
        })

    def to_dict(self):
        """转为字典"""
        return {
            'trace_id': self.trace_id,
            'total_steps': len(self.steps),
            'steps': self.steps
        }

    def save(self, output_dir: str = "traces"):
        """保存追踪日志"""
        os.makedirs(output_dir, exist_ok=True)
        filename = f"{output_dir}/trace_{self.trace_id}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2, default=str)
        return filename


class EnterpriseCrawlerV2:
    """企业信息爬虫V2 - 使用博查AI搜索"""

    def __init__(self, bocha_client=None):
        """
        初始化爬虫

        Args:
            bocha_client: 博查AI客户端实例 (可选,如未提供则使用默认客户端)
        """
        if bocha_client is None:
            from infrastructure.external.bocha_client import get_bocha_client
            bocha_client = get_bocha_client()
        self.bocha_client = bocha_client
        logger.info("EnterpriseCrawlerV2 initialized with Bocha AI client")

    async def search_enterprise_info(self, company_name: str, trace: CallTrace = None) -> Dict[str, Any]:
        """
        搜索企业信息

        Args:
            company_name: 企业名称
            trace: 调用追踪对象 (可选)

        Returns:
            Dict包含:
                - success: bool 是否成功
                - data: dict 企业数据 (如果成功)
                - error: str 错误信息 (如果失败)
                - trace: CallTrace 调用追踪对象
        """
        if trace is None:
            trace = CallTrace()

        try:
            start_time = time.time()
            logger.info(f"开始搜索企业: {company_name}")

            # 使用博查AI搜索
            query = f"{company_name} 企业信息 工商 注册资本 经营范围"
            search_start = time.time()
            result = self.bocha_client.search(query)
            search_elapsed = time.time() - search_start

            # 记录搜索步骤到trace
            trace.add_step(
                step_name="bocha_search",
                input_data={'company_name': company_name, 'query': query},
                output_data=result.data if result and result.success else None,
                elapsed=search_elapsed,
                success=result.success if result else False,
                error=result.error if result and not result.success else None
            )

            elapsed = time.time() - start_time

            if not result or not result.success:
                error_msg = result.error if result else "API返回空结果"
                logger.error(f"❌ 博查AI搜索失败: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'data': None,
                    'trace': trace
                }

            # 解析博查AI返回的数据
            search_data = result.data

            # 博查AI返回格式: {code, data: {webPages: {value: [...]}}}
            data_section = search_data.get('data', {})
            web_pages = data_section.get('webPages', {})
            results = web_pages.get('value', [])
            ai_summary = data_section.get('summary', '')

            logger.info(f"✅ 搜索完成: 找到{len(results)}条结果, 耗时={elapsed:.2f}秒")

            if not results:
                logger.warning(f"⚠️ 未找到企业信息: {company_name}")
                return {
                    'success': True,
                    'data': {
                        'company_name': company_name,
                        'search_results': [],
                        'combined_text': '',
                        'ai_summary': ai_summary,
                        'result_count': 0
                    },
                    'trace': trace
                }

            # 组合所有搜索结果的文本
            combined_texts = []
            search_results = []

            for i, r in enumerate(results, 1):
                # 博查API字段: name, snippet, summary, url
                title = r.get('name', '')
                snippet = r.get('snippet', '')
                summary = r.get('summary', '')
                url = r.get('url', '')

                # 优先使用summary(更详细),fallback到snippet
                content = summary if summary else snippet

                if title and content:
                    combined_texts.append(f"【来源{i}】{title}\n{content}")
                    search_results.append({
                        'title': title,
                        'content': content,
                        'url': url,
                        'source': i
                    })

            combined_text = '\n\n'.join(combined_texts)

            logger.debug(f"合并文本长度: {len(combined_text)} 字符")

            return {
                'success': True,
                'data': {
                    'company_name': company_name,
                    'search_results': search_results,
                    'combined_text': combined_text,
                    'ai_summary': ai_summary,
                    'result_count': len(results)
                },
                'trace': trace,
                'elapsed': elapsed
            }

        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"❌ 搜索企业信息异常: {company_name}, 错误: {str(e)}", exc_info=True)

            # 记录异常到trace
            trace.add_step(
                step_name="search_exception",
                input_data={'company_name': company_name},
                output_data=None,
                elapsed=elapsed,
                success=False,
                error=str(e)
            )

            return {
                'success': False,
                'error': str(e),
                'data': None,
                'trace': trace
            }
