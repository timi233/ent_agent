"""
简单的API密钥测试脚本（直接读取.env）
"""
import os
import sys
import requests
import json
from datetime import datetime

# 直接加载.env文件
def load_env():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    env_vars = {}
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    return env_vars

env_vars = load_env()

# API配置
BOCHA_API_KEY = env_vars.get('BOCHA_API_KEY', '')
BOCHA_BASE_URL = env_vars.get('BOCHA_BASE_URL', 'https://api.bochaai.com/v1/web-search')

LLM_API_KEY = env_vars.get('LLM_API_KEY', '')
LLM_BASE_URL = env_vars.get('LLM_BASE_URL', 'https://api.deepseek.com')
LLM_MODEL = env_vars.get('LLM_MODEL', 'deepseek-chat')

print("=" * 80)
print("API密钥有效性检查")
print("=" * 80)
print(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 测试结果
results = {
    'bocha': False,
    'llm': False
}

# ========== 测试1: Bocha AI 搜索API ==========
print("\n" + "─" * 80)
print("测试1: Bocha AI 搜索API")
print("─" * 80)
print(f"Base URL: {BOCHA_BASE_URL}")
print(f"API Key: {BOCHA_API_KEY[:12]}...{BOCHA_API_KEY[-4:]}" if len(BOCHA_API_KEY) > 16 else f"API Key: {BOCHA_API_KEY}")

try:
    headers = {
        'Authorization': f'Bearer {BOCHA_API_KEY}',
        'Content-Type': 'application/json'
    }

    data = {
        'query': 'Python编程语言',
        'summary': False,
        'count': 3,
        'freshness': 'year',
        'include_images': False,
        'include_videos': False
    }

    print(f"\n发送测试请求: {data['query']}")
    response = requests.post(
        BOCHA_BASE_URL,
        headers=headers,
        json=data,
        timeout=15
    )

    print(f"HTTP状态码: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"API响应: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}")

        # Bocha API返回格式: {code: 200, data: {webPages: {value: [...]}}}
        if result.get('code') == 200 and 'data' in result:
            data = result.get('data', {})
            web_pages = data.get('webPages', {}).get('value', [])
            print(f"✓ API响应成功")
            print(f"返回结果数: {len(web_pages)}")

            if web_pages:
                print(f"\n前3个结果:")
                for idx, page in enumerate(web_pages[:3], 1):
                    print(f"  {idx}. {page.get('name', 'N/A')}")
                    print(f"     URL: {page.get('url', 'N/A')[:80]}...")

            results['bocha'] = True
        else:
            print(f"✗ API返回失败状态: code={result.get('code')}, msg={result.get('msg', 'Unknown')}")
    else:
        print(f"✗ API请求失败")
        print(f"响应内容: {response.text[:200]}")

except Exception as e:
    print(f"✗ 测试异常: {e}")

# ========== 测试2: DeepSeek LLM API ==========
print("\n" + "─" * 80)
print("测试2: DeepSeek LLM API")
print("─" * 80)
print(f"Base URL: {LLM_BASE_URL}")
print(f"Model: {LLM_MODEL}")
print(f"API Key: {LLM_API_KEY[:12]}...{LLM_API_KEY[-4:]}" if len(LLM_API_KEY) > 16 else f"API Key: {LLM_API_KEY}")

try:
    headers = {
        'Authorization': f'Bearer {LLM_API_KEY}',
        'Content-Type': 'application/json'
    }

    data = {
        'model': LLM_MODEL,
        'messages': [
            {
                'role': 'user',
                'content': '你好，请用一句话介绍你自己。'
            }
        ],
        'max_tokens': 100,
        'temperature': 0.7
    }

    print(f"\n发送测试请求: {data['messages'][0]['content']}")
    response = requests.post(
        f"{LLM_BASE_URL}/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=30
    )

    print(f"HTTP状态码: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        if 'choices' in result and len(result['choices']) > 0:
            message = result['choices'][0].get('message', {})
            content = message.get('content', '')

            print(f"✓ API响应成功")
            print(f"响应内容: {content}")
            print(f"Token用量: {result.get('usage', {})}")

            results['llm'] = True
        else:
            print(f"✗ API返回格式异常: {result}")
    else:
        print(f"✗ API请求失败")
        print(f"响应内容: {response.text[:200]}")

except Exception as e:
    print(f"✗ 测试异常: {e}")

# ========== 测试总结 ==========
print("\n" + "=" * 80)
print("测试总结")
print("=" * 80)
print(f"\nBocha AI 搜索API: {'✓ 正常' if results['bocha'] else '✗ 失败'}")
print(f"DeepSeek LLM API: {'✓ 正常' if results['llm'] else '✗ 失败'}")
print(f"\n通过率: {sum(results.values())}/{len(results)} ({sum(results.values())/len(results)*100:.0f}%)")

if all(results.values()):
    print("\n✓ 所有API密钥有效，系统可以正常使用！")
else:
    print("\n✗ 部分API密钥无效，请检查配置")
    if not results['bocha']:
        print("  - Bocha AI API密钥可能无效或已过期")
    if not results['llm']:
        print("  - DeepSeek LLM API密钥可能无效或已过期")

print("\n" + "=" * 80)

# 保存报告
report = f"""API密钥有效性检查报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

测试结果:
- Bocha AI 搜索API: {'✓ 正常' if results['bocha'] else '✗ 失败'}
- DeepSeek LLM API: {'✓ 正常' if results['llm'] else '✗ 失败'}

通过率: {sum(results.values())}/{len(results)} ({sum(results.values())/len(results)*100:.0f}%)

配置信息:
- BOCHA_BASE_URL: {BOCHA_BASE_URL}
- BOCHA_API_KEY: {BOCHA_API_KEY[:12]}...{BOCHA_API_KEY[-4:] if len(BOCHA_API_KEY) > 16 else BOCHA_API_KEY}
- LLM_BASE_URL: {LLM_BASE_URL}
- LLM_MODEL: {LLM_MODEL}
- LLM_API_KEY: {LLM_API_KEY[:12]}...{LLM_API_KEY[-4:] if len(LLM_API_KEY) > 16 else LLM_API_KEY}
"""

with open('API_TEST_REPORT.txt', 'w', encoding='utf-8') as f:
    f.write(report)

print(f"\n报告已保存到: API_TEST_REPORT.txt")

sys.exit(0 if all(results.values()) else 1)
