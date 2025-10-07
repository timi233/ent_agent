#!/usr/bin/env python3
"""
API密钥验证脚本 - 快速验证.env文件中的密钥是否正确加载

使用方法:
    python3 verify_api_keys.py
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 加载环境变量 - 关键步骤
from dotenv import load_dotenv
load_dotenv()

# 导入配置和客户端
from infrastructure.external.bocha_client import DEFAULT_API_KEY as BOCHA_KEY
from infrastructure.external.llm_client import DEFAULT_API_KEY as LLM_KEY


def main():
    """验证API密钥是否正确加载"""
    print("=" * 80)
    print("API密钥加载验证")
    print("=" * 80)

    # 从环境变量读取
    env_bocha_key = os.getenv("BOCHA_API_KEY")
    env_llm_key = os.getenv("LLM_API_KEY")

    print("\n1. 环境变量检查:")
    print(f"   BOCHA_API_KEY: {env_bocha_key[:10]}...{env_bocha_key[-4:] if env_bocha_key else 'None'}")
    print(f"   LLM_API_KEY:   {env_llm_key[:10]}...{env_llm_key[-4:] if env_llm_key else 'None'}")

    print("\n2. 客户端配置检查:")
    print(f"   Bocha Client:  {BOCHA_KEY[:10]}...{BOCHA_KEY[-4:] if BOCHA_KEY else 'None'}")
    print(f"   LLM Client:    {LLM_KEY[:10]}...{LLM_KEY[-4:] if LLM_KEY else 'None'}")

    print("\n3. 密钥匹配验证:")
    bocha_match = env_bocha_key == BOCHA_KEY
    llm_match = env_llm_key == LLM_KEY

    if bocha_match:
        print("   ✅ Bocha API密钥匹配")
    else:
        print("   ❌ Bocha API密钥不匹配")

    if llm_match:
        print("   ✅ LLM API密钥匹配")
    else:
        print("   ❌ LLM API密钥不匹配")

    print("\n4. 完整性检查:")
    if env_bocha_key and not env_bocha_key.startswith("your_"):
        print("   ✅ Bocha API密钥已配置（非默认值）")
    else:
        print("   ⚠️  Bocha API密钥使用默认值或未配置")

    if env_llm_key and not env_llm_key.startswith("your_"):
        print("   ✅ LLM API密钥已配置（非默认值）")
    else:
        print("   ⚠️  LLM API密钥使用默认值或未配置")

    print("\n" + "=" * 80)

    # 总结
    if bocha_match and llm_match and env_bocha_key and env_llm_key:
        print("✅ API密钥验证通过！所有密钥正确加载。")
        return 0
    else:
        print("❌ API密钥验证失败！请检查.env文件和导入顺序。")
        return 1


if __name__ == "__main__":
    exit(main())
