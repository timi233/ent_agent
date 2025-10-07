#!/usr/bin/env python3
"""
API集成测试脚本

测试内容：
1. API服务启动和健康检查
2. V2版本API端点测试
3. 依赖注入系统测试
4. 错误处理测试
5. 日志记录测试
"""

import sys
import os
import requests
import time
import subprocess
import signal

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 测试配置
API_BASE_URL = "http://localhost:9003"
API_V1_PREFIX = "/api/v1"
API_V2_PREFIX = "/api/v1/v2"


def test_server_running():
    """测试服务器是否运行"""
    print("=" * 80)
    print("测试 1: 服务器运行状态检查")
    print("=" * 80)

    try:
        response = requests.get(f"{API_BASE_URL}{API_V1_PREFIX}/health", timeout=5)
        if response.status_code == 200:
            print("✅ 服务器正在运行")
            print(f"   响应: {response.json()}")
            return True
        else:
            print(f"❌ 服务器响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器")
        print(f"   请确保服务器运行在 {API_BASE_URL}")
        return False
    except Exception as e:
        print(f"❌ 服务器检查失败: {e}")
        return False


def test_v2_health_check():
    """测试V2版本健康检查"""
    print("\n" + "=" * 80)
    print("测试 2: V2版本健康检查")
    print("=" * 80)

    try:
        response = requests.get(f"{API_BASE_URL}{API_V2_PREFIX}/company/health", timeout=5)

        if response.status_code == 200:
            data = response.json()
            print("✅ V2健康检查通过")
            print(f"   版本: {data.get('version')}")
            print(f"   架构: {data.get('architecture')}")
            print(f"   功能: {', '.join(data.get('features', []))}")
            return True
        else:
            print(f"❌ V2健康检查失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
    except Exception as e:
        print(f"❌ V2健康检查异常: {e}")
        return False


def test_v2_basic_info():
    """测试V2基础信息获取"""
    print("\n" + "=" * 80)
    print("测试 3: V2基础信息获取")
    print("=" * 80)

    test_companies = [
        "测试公司A",
        "青岛啤酒",
        "海尔集团"
    ]

    passed = 0
    for company_name in test_companies:
        try:
            response = requests.post(
                f"{API_BASE_URL}{API_V2_PREFIX}/company/basic-info",
                json={"input_text": company_name},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                print(f"✅ 获取 '{company_name}' 基础信息成功")
                if data.get('data'):
                    print(f"   公司名: {data['data'].get('name', 'N/A')}")
                    print(f"   来源: {data['data'].get('source', 'N/A')}")
                passed += 1
            else:
                print(f"⚠️  获取 '{company_name}' 基础信息失败: {response.status_code}")

        except Exception as e:
            print(f"❌ 测试 '{company_name}' 异常: {e}")

    print(f"\n通过率: {passed}/{len(test_companies)}")
    return passed == len(test_companies)


def test_v2_search():
    """测试V2搜索功能"""
    print("\n" + "=" * 80)
    print("测试 4: V2本地数据库搜索")
    print("=" * 80)

    test_companies = ["测试公司", "不存在的公司XYZ"]

    passed = 0
    for company_name in test_companies:
        try:
            response = requests.get(
                f"{API_BASE_URL}{API_V2_PREFIX}/company/search/{company_name}",
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                found = data.get('found', False)
                print(f"✅ 搜索 '{company_name}': {'找到' if found else '未找到'}")
                print(f"   消息: {data.get('message', 'N/A')}")
                passed += 1
            else:
                print(f"⚠️  搜索 '{company_name}' 失败: {response.status_code}")

        except Exception as e:
            print(f"❌ 搜索 '{company_name}' 异常: {e}")

    print(f"\n通过率: {passed}/{len(test_companies)}")
    return passed == len(test_companies)


def test_error_handling():
    """测试错误处理"""
    print("\n" + "=" * 80)
    print("测试 5: 错误处理")
    print("=" * 80)

    # 测试空输入
    try:
        response = requests.post(
            f"{API_BASE_URL}{API_V2_PREFIX}/company/basic-info",
            json={"input_text": ""},
            timeout=5
        )

        if response.status_code >= 400:
            print("✅ 空输入正确返回错误")
            print(f"   状态码: {response.status_code}")
        else:
            print("⚠️  空输入应该返回错误但返回了成功")

    except Exception as e:
        print(f"❌ 错误处理测试异常: {e}")
        return False

    # 测试无效的JSON
    try:
        response = requests.post(
            f"{API_BASE_URL}{API_V2_PREFIX}/company/basic-info",
            data="invalid json",
            headers={"Content-Type": "application/json"},
            timeout=5
        )

        if response.status_code >= 400:
            print("✅ 无效JSON正确返回错误")
            print(f"   状态码: {response.status_code}")
            return True
        else:
            print("⚠️  无效JSON应该返回错误")
            return False

    except Exception as e:
        print(f"❌ 无效JSON测试异常: {e}")
        return False


def test_response_format():
    """测试响应格式"""
    print("\n" + "=" * 80)
    print("测试 6: 响应格式验证")
    print("=" * 80)

    try:
        response = requests.get(f"{API_BASE_URL}{API_V2_PREFIX}/company/health", timeout=5)

        if response.status_code == 200:
            data = response.json()

            # 检查必需字段
            required_fields = ['status', 'version', 'timestamp']
            missing_fields = [field for field in required_fields if field not in data]

            if not missing_fields:
                print("✅ 响应包含所有必需字段")
                print(f"   字段: {', '.join(required_fields)}")

                # 检查版本号
                if data.get('version') == 'v2':
                    print("✅ 版本号正确: v2")
                    return True
                else:
                    print(f"⚠️  版本号不正确: {data.get('version')}")
                    return False
            else:
                print(f"❌ 响应缺少字段: {', '.join(missing_fields)}")
                return False
        else:
            print(f"❌ 响应状态码错误: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ 响应格式测试异常: {e}")
        return False


def test_dependency_injection():
    """测试依赖注入系统"""
    print("\n" + "=" * 80)
    print("测试 7: 依赖注入系统")
    print("=" * 80)

    try:
        from api.v1.dependencies import (
            get_container,
            get_enterprise_service_refactored
        )

        # 测试容器
        container = get_container()
        print("✅ 依赖注入容器获取成功")

        # 测试服务获取
        service = get_enterprise_service_refactored()
        print("✅ 重构后的企业服务获取成功")

        # 验证处理器已初始化
        if hasattr(service, 'processor') and service.processor is not None:
            print("✅ 企业信息处理器已初始化")
        else:
            print("❌ 企业信息处理器未初始化")
            return False

        if hasattr(service, 'enhancer') and service.enhancer is not None:
            print("✅ 企业数据增强器已初始化")
        else:
            print("❌ 企业数据增强器未初始化")
            return False

        if hasattr(service, 'analyzer') and service.analyzer is not None:
            print("✅ 企业分析器已初始化")
        else:
            print("❌ 企业分析器未初始化")
            return False

        return True

    except Exception as e:
        print(f"❌ 依赖注入测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_performance():
    """测试性能"""
    print("\n" + "=" * 80)
    print("测试 8: 性能测试")
    print("=" * 80)

    try:
        # 测试健康检查响应时间
        start_time = time.time()
        response = requests.get(f"{API_BASE_URL}{API_V2_PREFIX}/company/health", timeout=5)
        duration = time.time() - start_time

        if response.status_code == 200:
            print(f"✅ 健康检查响应时间: {duration*1000:.2f}ms")

            if duration < 0.5:
                print("✅ 响应时间优秀 (<500ms)")
                return True
            elif duration < 1.0:
                print("⚠️  响应时间可接受 (<1s)")
                return True
            else:
                print("⚠️  响应时间较慢 (>1s)")
                return False
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ 性能测试异常: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 开始API集成测试")
    print("=" * 80)
    print(f"API基础URL: {API_BASE_URL}")
    print(f"V1前缀: {API_V1_PREFIX}")
    print(f"V2前缀: {API_V2_PREFIX}")
    print("=" * 80)

    tests = [
        ("服务器运行状态", test_server_running),
        ("V2健康检查", test_v2_health_check),
        ("V2基础信息获取", test_v2_basic_info),
        ("V2本地搜索", test_v2_search),
        ("错误处理", test_error_handling),
        ("响应格式验证", test_response_format),
        ("依赖注入系统", test_dependency_injection),
        ("性能测试", test_performance)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ 测试 '{test_name}' 执行异常: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # 汇总结果
    print("\n" + "=" * 80)
    print("📊 测试结果汇总")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status}: {test_name}")

    print(f"\n总计: {passed}/{total} 测试通过 ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n🎉 所有API集成测试通过！")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    exit(main())
