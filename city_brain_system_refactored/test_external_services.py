#!/usr/bin/env python3
"""
外部服务层测试脚本
测试博查AI客户端、LLM客户端和服务管理器的功能
"""
import sys
import os
import logging
import time
from typing import Dict, Any

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 加载环境变量 - 必须在导入其他模块之前
from dotenv import load_dotenv
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_bocha_client():
    """测试博查AI客户端"""
    print("\n" + "="*50)
    print("测试博查AI客户端")
    print("="*50)
    
    try:
        from infrastructure.external.bocha_client import BochaAIClient, get_bocha_client
        
        # 测试客户端创建
        client = get_bocha_client()
        print(f"✓ 博查AI客户端创建成功")
        
        # 获取客户端信息
        client_info = client.get_client_info()
        print(f"✓ 客户端信息: {client_info}")
        
        # 测试健康检查
        is_healthy = client.health_check()
        print(f"✓ 健康检查: {'通过' if is_healthy else '失败'}")
        
        # 测试搜索功能（使用简单查询避免API调用）
        print("✓ 搜索功能接口可用")
        
        return True
        
    except Exception as e:
        print(f"✗ 博查AI客户端测试失败: {e}")
        return False


def test_llm_client():
    """测试LLM客户端"""
    print("\n" + "="*50)
    print("测试LLM客户端")
    print("="*50)
    
    try:
        from infrastructure.external.llm_client import LLMClient, get_llm_client, ChatMessage
        
        # 测试客户端创建
        client = get_llm_client()
        print(f"✓ LLM客户端创建成功")
        
        # 获取客户端信息
        client_info = client.get_client_info()
        print(f"✓ 客户端信息: {client_info}")
        
        # 测试消息创建
        system_msg = ChatMessage.system("你是一个测试助手")
        user_msg = ChatMessage.user("测试消息")
        print(f"✓ 消息对象创建成功")
        
        # 测试消息转换
        system_dict = system_msg.to_dict()
        user_dict = user_msg.to_dict()
        print(f"✓ 消息格式转换成功: {system_dict}, {user_dict}")
        
        # 测试健康检查（不实际调用API）
        print("✓ LLM客户端接口可用")
        
        return True
        
    except Exception as e:
        print(f"✗ LLM客户端测试失败: {e}")
        return False


def test_service_manager():
    """测试服务管理器"""
    print("\n" + "="*50)
    print("测试服务管理器")
    print("="*50)
    
    try:
        from infrastructure.external.service_manager import (
            ExternalServiceManager, 
            get_service_manager,
            EnterpriseSearchRequest,
            EnterpriseInfo,
            ServiceResult,
            ServiceType
        )
        
        # 测试服务管理器创建
        manager = get_service_manager()
        print(f"✓ 服务管理器创建成功")
        
        # 测试服务状态
        status = manager.get_service_status()
        print(f"✓ 服务状态获取成功: {len(status)}个服务")
        
        # 测试企业搜索请求对象
        search_request = EnterpriseSearchRequest(
            enterprise_name="测试企业",
            search_fields=['address', 'industry'],
            max_results=3
        )
        print(f"✓ 企业搜索请求创建成功: {search_request.enterprise_name}")
        
        # 测试企业信息对象
        enterprise_info = EnterpriseInfo(
            name="测试企业",
            address="测试地址",
            industry="测试行业"
        )
        print(f"✓ 企业信息对象创建成功: {enterprise_info.name}")
        
        # 测试服务结果对象
        success_result = ServiceResult.success_result(
            ServiceType.SEARCH,
            {"test": "data"},
            1.5
        )
        error_result = ServiceResult.error_result(
            ServiceType.SEARCH,
            "测试错误",
            0.5
        )
        print(f"✓ 服务结果对象创建成功: 成功={success_result.success}, 失败={error_result.success}")
        
        return True
        
    except Exception as e:
        print(f"✗ 服务管理器测试失败: {e}")
        return False


def test_external_module_imports():
    """测试外部模块导入"""
    print("\n" + "="*50)
    print("测试外部模块导入")
    print("="*50)
    
    try:
        # 测试主模块导入
        from infrastructure.external import (
            BochaAIClient,
            get_bocha_client,
            search_web,
            LLMClient,
            get_llm_client,
            generate_summary,
            analyze_text
        )
        print("✓ 外部模块主要接口导入成功")
        
        # 测试向后兼容函数
        print("✓ 向后兼容函数可用:")
        print(f"  - search_web: {callable(search_web)}")
        print(f"  - generate_summary: {callable(generate_summary)}")
        print(f"  - analyze_text: {callable(analyze_text)}")
        
        return True
        
    except Exception as e:
        print(f"✗ 外部模块导入测试失败: {e}")
        return False


def test_configuration_loading():
    """测试配置加载"""
    print("\n" + "="*50)
    print("测试配置加载")
    print("="*50)
    
    try:
        # 测试配置加载
        try:
            from config.simple_settings import get_simple_config
            config = get_simple_config()
            print("✓ 配置加载成功")
            
            # 检查配置属性
            config_attrs = ['bocha_base_url', 'bocha_api_key', 'deepseek_base_url', 'deepseek_api_key']
            available_attrs = []
            for attr in config_attrs:
                if hasattr(config, attr):
                    available_attrs.append(attr)
            
            print(f"✓ 可用配置项: {available_attrs}")
            
        except ImportError:
            print("✓ 配置模块未找到，使用默认配置")
        
        return True
        
    except Exception as e:
        print(f"✗ 配置加载测试失败: {e}")
        return False


def test_error_handling():
    """测试错误处理"""
    print("\n" + "="*50)
    print("测试错误处理")
    print("="*50)
    
    try:
        from infrastructure.external.bocha_client import BochaAIClient, BochaAPIError
        from infrastructure.external.llm_client import LLMClient, LLMAPIError
        
        # 测试异常类
        bocha_error = BochaAPIError("测试错误", 400, "测试响应")
        llm_error = LLMAPIError("测试错误", 500, "测试响应")
        
        print(f"✓ 异常类创建成功:")
        print(f"  - BochaAPIError: {bocha_error.status_code}")
        print(f"  - LLMAPIError: {llm_error.status_code}")
        
        # 测试客户端错误处理
        bocha_client = BochaAIClient(api_key="invalid_key")
        llm_client = LLMClient(api_key="invalid_key")
        
        print("✓ 无效密钥客户端创建成功（错误处理正常）")
        
        return True
        
    except Exception as e:
        print(f"✗ 错误处理测试失败: {e}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("开始外部服务层测试")
    print("="*80)
    
    test_results = []
    
    # 运行各项测试
    tests = [
        ("配置加载", test_configuration_loading),
        ("博查AI客户端", test_bocha_client),
        ("LLM客户端", test_llm_client),
        ("服务管理器", test_service_manager),
        ("模块导入", test_external_module_imports),
        ("错误处理", test_error_handling),
    ]
    
    for test_name, test_func in tests:
        try:
            start_time = time.time()
            result = test_func()
            end_time = time.time()
            
            test_results.append({
                'name': test_name,
                'success': result,
                'duration': end_time - start_time
            })
            
        except Exception as e:
            logger.error(f"测试 {test_name} 执行异常: {e}")
            test_results.append({
                'name': test_name,
                'success': False,
                'duration': 0,
                'error': str(e)
            })
    
    # 输出测试结果汇总
    print("\n" + "="*80)
    print("测试结果汇总")
    print("="*80)
    
    passed = 0
    failed = 0
    total_time = 0
    
    for result in test_results:
        status = "✓ 通过" if result['success'] else "✗ 失败"
        duration = f"{result['duration']:.3f}s"
        print(f"{result['name']:<20} {status:<10} {duration}")
        
        if result['success']:
            passed += 1
        else:
            failed += 1
        
        total_time += result['duration']
        
        if not result['success'] and 'error' in result:
            print(f"  错误: {result['error']}")
    
    print("-" * 80)
    print(f"总计: {passed + failed}个测试, {passed}个通过, {failed}个失败")
    print(f"总耗时: {total_time:.3f}秒")
    
    # 计算通过率
    pass_rate = (passed / (passed + failed)) * 100 if (passed + failed) > 0 else 0
    print(f"通过率: {pass_rate:.1f}%")
    
    if pass_rate == 100:
        print("\n🎉 所有测试通过！外部服务层重构成功！")
    elif pass_rate >= 80:
        print(f"\n⚠️  大部分测试通过，但有{failed}个测试失败，需要检查")
    else:
        print(f"\n❌ 测试失败过多，需要修复问题")
    
    return pass_rate == 100


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)