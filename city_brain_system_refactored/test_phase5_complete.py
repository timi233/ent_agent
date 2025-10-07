#!/usr/bin/env python3
"""
阶段五完整验证测试

测试内容：
1. 依赖注入系统验证
2. V2 API端点验证
3. 路由配置验证
4. 服务集成验证
5. 架构合规性验证
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 加载环境变量 - 必须在导入其他模块之前
from dotenv import load_dotenv
load_dotenv()


def test_dependency_injection():
    """测试依赖注入系统"""
    print("=" * 80)
    print("测试 1: 依赖注入系统")
    print("=" * 80)

    try:
        from api.v1.dependencies import (
            get_container,
            get_enterprise_service,
            get_enterprise_service_refactored,
            get_data_enhancement_service,
            get_analysis_service,
            get_search_service,
            get_customer_repository
        )

        # 测试容器
        container = get_container()
        print("✅ 依赖注入容器获取成功")

        # 测试原服务
        service_v1 = get_enterprise_service()
        print("✅ 原企业服务获取成功")

        # 测试重构后的服务
        service_v2 = get_enterprise_service_refactored()
        print("✅ 重构后的企业服务获取成功")

        # 验证处理器已初始化
        assert hasattr(service_v2, 'processor') and service_v2.processor is not None
        print("✅ 企业信息处理器已初始化")

        assert hasattr(service_v2, 'enhancer') and service_v2.enhancer is not None
        print("✅ 企业数据增强器已初始化")

        assert hasattr(service_v2, 'analyzer') and service_v2.analyzer is not None
        print("✅ 企业分析器已初始化")

        # 测试其他服务
        data_enhancement_service = get_data_enhancement_service()
        print("✅ 数据增强服务获取成功")

        analysis_service = get_analysis_service()
        print("✅ 分析服务获取成功")

        search_service = get_search_service()
        print("✅ 搜索服务获取成功")

        customer_repository = get_customer_repository()
        print("✅ 客户仓储获取成功")

        return True

    except Exception as e:
        print(f"❌ 依赖注入测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_v2_endpoints():
    """测试V2端点"""
    print("\n" + "=" * 80)
    print("测试 2: V2 API端点")
    print("=" * 80)

    try:
        from api.v1.endpoints.company_v2 import router

        print(f"✅ V2路由器导入成功")
        print(f"   路由前缀: {router.prefix}")
        print(f"   标签: {router.tags}")
        print(f"   路由数量: {len(router.routes)}")

        # 验证路由
        expected_routes = [
            ('/v2/company/process', {'POST'}),
            ('/v2/company/basic-info', {'POST'}),
            ('/v2/company/search/{company_name}', {'GET'}),
            ('/v2/company/health', {'GET'})
        ]

        actual_routes = [(route.path, route.methods) for route in router.routes]

        for expected_path, expected_methods in expected_routes:
            found = any(path == expected_path and methods == expected_methods
                       for path, methods in actual_routes)
            if found:
                print(f"✅ 路由存在: {list(expected_methods)[0]} {expected_path}")
            else:
                print(f"❌ 路由缺失: {list(expected_methods)[0]} {expected_path}")
                return False

        return True

    except Exception as e:
        print(f"❌ V2端点测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_router_configuration():
    """测试路由配置"""
    print("\n" + "=" * 80)
    print("测试 3: 路由配置")
    print("=" * 80)

    try:
        from api.v1 import router as v1_router

        print("✅ V1路由器导入成功")
        print(f"   路由前缀: {v1_router.prefix}")

        # 统计路由
        total_routes = len(v1_router.routes)
        print(f"✅ 总路由数: {total_routes}")

        # 检查是否包含V2路由
        v2_routes = [route for route in v1_router.routes if '/v2/' in route.path]
        if v2_routes:
            print(f"✅ V2路由已注册: {len(v2_routes)} 个")
            for route in v2_routes:
                print(f"   - {list(route.methods)[0]} {route.path}")
        else:
            print("❌ V2路由未注册")
            return False

        return True

    except Exception as e:
        print(f"❌ 路由配置测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_service_integration():
    """测试服务集成"""
    print("\n" + "=" * 80)
    print("测试 4: 服务集成")
    print("=" * 80)

    try:
        from api.v1.dependencies import get_enterprise_service_refactored

        service = get_enterprise_service_refactored()

        # 测试服务方法存在
        methods = [
            'process_company_info',
            'process_with_local_data',
            'process_without_local_data',
            'get_company_basic_info',
            'search_local_database',
            'update_company_info',
            'update_chain_leader_info'
        ]

        for method_name in methods:
            if hasattr(service, method_name):
                print(f"✅ 方法存在: {method_name}")
            else:
                print(f"❌ 方法缺失: {method_name}")
                return False

        # 测试处理器方法
        processor_methods = [
            'extract_company_name',
            'normalize_company_name',
            'clean_company_name',
            'extract_core_company_name',
            'build_basic_info_from_search'
        ]

        for method_name in processor_methods:
            if hasattr(service.processor, method_name):
                print(f"✅ 处理器方法存在: {method_name}")
            else:
                print(f"❌ 处理器方法缺失: {method_name}")
                return False

        return True

    except Exception as e:
        print(f"❌ 服务集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_architecture_compliance():
    """测试架构合规性"""
    print("\n" + "=" * 80)
    print("测试 5: 架构合规性")
    print("=" * 80)

    try:
        from api.v1.endpoints import company_v2
        import inspect

        source = inspect.getsource(company_v2)

        # 检查是否直接导入infrastructure层（允许，因为是API层）
        # 检查是否正确使用依赖注入
        if 'Depends(get_enterprise_service_refactored)' in source:
            print("✅ 正确使用依赖注入")
        else:
            print("⚠️  未使用依赖注入")

        # 检查是否有适当的错误处理
        if 'try:' in source and 'except' in source:
            print("✅ 包含错误处理")
        else:
            print("⚠️  缺少错误处理")

        # 检查是否有日志记录
        if 'logger.' in source:
            print("✅ 包含日志记录")
        else:
            print("⚠️  缺少日志记录")

        # 检查是否返回标准化响应
        if 'JSONResponse' in source:
            print("✅ 使用标准化响应")
        else:
            print("⚠️  未使用标准化响应")

        return True

    except Exception as e:
        print(f"❌ 架构合规性测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_backward_compatibility():
    """测试向后兼容性"""
    print("\n" + "=" * 80)
    print("测试 6: 向后兼容性")
    print("=" * 80)

    try:
        # 测试原服务仍然可用
        from api.v1.dependencies import get_enterprise_service
        from api.v1.endpoints.company import router as company_router

        service_v1 = get_enterprise_service()
        print("✅ 原企业服务仍然可用")

        print(f"✅ 原公司路由器可用")
        print(f"   路由前缀: {company_router.prefix}")
        print(f"   路由数量: {len(company_router.routes)}")

        # 验证两个版本服务都有process_company_info方法
        from api.v1.dependencies import get_enterprise_service_refactored

        service_v2 = get_enterprise_service_refactored()

        if hasattr(service_v1, 'process_company_info') and hasattr(service_v2, 'process_company_info'):
            print("✅ 两个版本都有process_company_info方法")
        else:
            print("❌ 方法不兼容")
            return False

        return True

    except Exception as e:
        print(f"❌ 向后兼容性测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_module_imports():
    """测试模块导入"""
    print("\n" + "=" * 80)
    print("测试 7: 模块导入")
    print("=" * 80)

    modules = [
        ('domain.services.enterprise_processor', 'EnterpriseProcessor'),
        ('domain.services.enterprise_enhancer', 'EnterpriseEnhancer'),
        ('domain.services.enterprise_analyzer', 'EnterpriseAnalyzer'),
        ('domain.services.enterprise_service_refactored', 'EnterpriseServiceRefactored'),
        ('api.v1.endpoints.company_v2', 'router'),
        ('api.v1.dependencies', 'get_enterprise_service_refactored')
    ]

    all_passed = True
    for module_name, class_or_var in modules:
        try:
            module = __import__(module_name, fromlist=[class_or_var])
            getattr(module, class_or_var)
            print(f"✅ 导入成功: {module_name}.{class_or_var}")
        except Exception as e:
            print(f"❌ 导入失败: {module_name}.{class_or_var} - {e}")
            all_passed = False

    return all_passed


def main():
    """主测试函数"""
    print("🚀 开始阶段五完整验证测试")
    print("=" * 80)

    tests = [
        ("模块导入", test_module_imports),
        ("依赖注入系统", test_dependency_injection),
        ("V2 API端点", test_v2_endpoints),
        ("路由配置", test_router_configuration),
        ("服务集成", test_service_integration),
        ("架构合规性", test_architecture_compliance),
        ("向后兼容性", test_backward_compatibility)
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
        print("\n🎉 阶段五完整验证测试全部通过！")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    exit(main())
