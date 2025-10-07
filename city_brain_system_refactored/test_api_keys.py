"""
API密钥有效性检查脚本

测试：
1. DeepSeek LLM API
2. Bocha AI 搜索API
"""

import sys
import os
import logging
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

# 加载环境变量 - 必须在导入其他模块之前
from dotenv import load_dotenv
load_dotenv()

from infrastructure.external.llm_client import LLMClient
from infrastructure.external.bocha_client import BochaAIClient
from config.settings import get_settings

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_deepseek_llm_api():
    """测试DeepSeek LLM API"""
    logger.info("\n" + "=" * 70)
    logger.info("测试 1: DeepSeek LLM API 连接性检查")
    logger.info("=" * 70)

    try:
        # 加载配置
        settings = get_settings()
        logger.info(f"LLM Base URL: {settings.llm_api.base_url}")
        logger.info(f"LLM Model: {settings.llm_api.model}")
        logger.info(f"API Key配置: {'已配置' if settings.llm_api.api_key else '未配置'}")
        logger.info(f"API Key (前8位): {settings.llm_api.api_key[:8]}..." if settings.llm_api.api_key else "N/A")

        # 创建LLM客户端
        llm_client = LLMClient()

        # 测试简单的聊天请求
        test_prompt = "你好，请用一句话介绍你自己。"
        logger.info(f"\n发送测试请求: {test_prompt}")

        response = llm_client.chat(test_prompt)

        if response:
            logger.info(f"✓ API响应成功")
            logger.info(f"响应内容: {response[:200]}..." if len(response) > 200 else f"响应内容: {response}")
            logger.info(f"响应长度: {len(response)} 字符")
            return True
        else:
            logger.error("✗ API返回空响应")
            return False

    except Exception as e:
        logger.error(f"✗ DeepSeek LLM API测试失败: {e}", exc_info=True)
        return False


def test_bocha_search_api():
    """测试Bocha AI 搜索API"""
    logger.info("\n" + "=" * 70)
    logger.info("测试 2: Bocha AI 搜索API 连接性检查")
    logger.info("=" * 70)

    try:
        # 加载配置
        settings = get_settings()
        logger.info(f"Bocha Base URL: {settings.bocha_api.base_url}")
        logger.info(f"API Key配置: {'已配置' if settings.bocha_api.api_key else '未配置'}")
        logger.info(f"API Key (前8位): {settings.bocha_api.api_key[:8]}..." if settings.bocha_api.api_key else "N/A")

        # 创建Bocha客户端
        bocha_client = BochaAIClient()

        # 测试简单的搜索请求
        test_query = "Python编程语言"
        logger.info(f"\n发送测试搜索: {test_query}")

        response = bocha_client.search(test_query, count=3)

        if response and response.get('status') == 'success':
            data = response.get('data', {})
            web_pages = data.get('webPages', {})
            results = web_pages.get('value', [])

            logger.info(f"✓ 搜索成功")
            logger.info(f"返回结果数: {len(results)}")

            if results:
                logger.info(f"\n前3个搜索结果:")
                for idx, result in enumerate(results[:3], 1):
                    title = result.get('name', 'N/A')
                    url = result.get('url', 'N/A')
                    snippet = result.get('snippet', 'N/A')
                    logger.info(f"\n  结果 {idx}:")
                    logger.info(f"    标题: {title}")
                    logger.info(f"    URL: {url}")
                    logger.info(f"    摘要: {snippet[:100]}..." if len(snippet) > 100 else f"    摘要: {snippet}")

            return True
        else:
            logger.error(f"✗ 搜索失败")
            logger.error(f"响应: {response}")
            return False

    except Exception as e:
        logger.error(f"✗ Bocha AI 搜索API测试失败: {e}", exc_info=True)
        return False


def test_integration_workflow():
    """测试集成工作流（LLM + 搜索）"""
    logger.info("\n" + "=" * 70)
    logger.info("测试 3: 集成工作流测试（搜索 + LLM总结）")
    logger.info("=" * 70)

    try:
        # 1. 搜索企业信息
        bocha_client = BochaAIClient()
        search_query = "华为技术有限公司"
        logger.info(f"步骤1: 搜索企业信息 - {search_query}")

        search_response = bocha_client.search(search_query, count=3)

        if not search_response or search_response.get('status') != 'success':
            logger.error("✗ 搜索步骤失败")
            return False

        # 提取搜索结果文本
        data = search_response.get('data', {})
        web_pages = data.get('webPages', {})
        results = web_pages.get('value', [])

        if not results:
            logger.error("✗ 未找到搜索结果")
            return False

        logger.info(f"✓ 搜索成功，找到 {len(results)} 个结果")

        # 2. 使用LLM总结搜索结果
        llm_client = LLMClient()

        # 构建总结prompt
        search_text = "\n".join([
            f"- {r.get('name', '')}: {r.get('snippet', '')}"
            for r in results[:3]
        ])

        summary_prompt = f"""
        请根据以下搜索结果，简要总结"{search_query}"的基本信息（50字以内）：

        {search_text}
        """

        logger.info(f"\n步骤2: 使用LLM总结搜索结果")
        summary = llm_client.chat(summary_prompt.strip())

        if summary:
            logger.info(f"✓ LLM总结成功")
            logger.info(f"总结内容: {summary}")
            return True
        else:
            logger.error("✗ LLM总结失败")
            return False

    except Exception as e:
        logger.error(f"✗ 集成工作流测试失败: {e}", exc_info=True)
        return False


def generate_health_report(results):
    """生成API健康检查报告"""
    logger.info("\n" + "=" * 70)
    logger.info("API 健康检查报告")
    logger.info("=" * 70)

    report = f"""
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

测试结果汇总:
{'─' * 70}
1. DeepSeek LLM API     : {'✓ 正常' if results['llm'] else '✗ 失败'}
2. Bocha AI 搜索API     : {'✓ 正常' if results['bocha'] else '✗ 失败'}
3. 集成工作流          : {'✓ 正常' if results['integration'] else '✗ 失败'}
{'─' * 70}

总体状态: {'✓ 所有API正常' if all(results.values()) else '✗ 部分API异常'}
通过率: {sum(results.values())}/{len(results)} ({sum(results.values())/len(results)*100:.1f}%)

建议:
"""

    if not results['llm']:
        report += "\n  - 检查 LLM_API_KEY 配置是否正确"
        report += "\n  - 确认DeepSeek账户余额充足"
        report += "\n  - 检查网络连接和防火墙设置"

    if not results['bocha']:
        report += "\n  - 检查 BOCHA_API_KEY 配置是否正确"
        report += "\n  - 确认Bocha AI账户状态正常"
        report += "\n  - 检查API密钥是否过期"

    if not results['integration']:
        report += "\n  - 检查两个API是否都正常工作"
        report += "\n  - 确认网络环境稳定"

    if all(results.values()):
        report += "\n  ✓ 所有API工作正常，系统可以正常使用"

    logger.info(report)

    # 保存报告到文件
    report_file = "/home/jian/code/code/city_brain_system_refactored/API_HEALTH_REPORT.txt"
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"\n报告已保存到: {report_file}")
    except Exception as e:
        logger.error(f"保存报告失败: {e}")

    return all(results.values())


def main():
    """主测试函数"""
    logger.info("\n\n")
    logger.info("*" * 70)
    logger.info("*" + " " * 20 + "API密钥有效性检查" + " " * 20 + "*")
    logger.info("*" * 70)
    logger.info("\n")

    results = {
        'llm': False,
        'bocha': False,
        'integration': False
    }

    # 测试1: DeepSeek LLM
    try:
        results['llm'] = test_deepseek_llm_api()
    except Exception as e:
        logger.error(f"LLM测试异常: {e}")

    # 测试2: Bocha AI
    try:
        results['bocha'] = test_bocha_search_api()
    except Exception as e:
        logger.error(f"Bocha测试异常: {e}")

    # 测试3: 集成工作流
    if results['llm'] and results['bocha']:
        try:
            results['integration'] = test_integration_workflow()
        except Exception as e:
            logger.error(f"集成测试异常: {e}")
    else:
        logger.warning("\n跳过集成测试（前置API测试未全部通过）")

    # 生成报告
    success = generate_health_report(results)

    logger.info("\n" + "*" * 70)
    logger.info(f"{'测试完成 - 所有API正常' if success else '测试完成 - 部分API异常'}")
    logger.info("*" * 70 + "\n")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
