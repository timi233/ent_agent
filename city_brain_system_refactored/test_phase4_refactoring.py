#!/usr/bin/env python3
"""
阶段四核心业务逻辑重构测试

测试内容：
1. 企业信息处理器测试
2. 企业数据增强器测试
3. 企业分析器测试
4. 重构后的企业服务测试
5. 模块导入测试
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试模块导入"""
    print("=" * 80)
    print("测试 1: 模块导入测试")
    print("=" * 80)

    try:
        # 测试新模块导入
        from domain.services.enterprise_processor import EnterpriseProcessor
        print("✅ EnterpriseProcessor 导入成功")

        from domain.services.enterprise_enhancer import EnterpriseEnhancer
        print("✅ EnterpriseEnhancer 导入成功")

        from domain.services.enterprise_analyzer import EnterpriseAnalyzer
        print("✅ EnterpriseAnalyzer 导入成功")

        from domain.services.enterprise_service_refactored import EnterpriseServiceRefactored
        print("✅ EnterpriseServiceRefactored 导入成功")

        # 测试从__init__导入
        from domain.services import (
            EnterpriseProcessor,
            EnterpriseEnhancer,
            EnterpriseAnalyzer,
            EnterpriseServiceRefactored
        )
        print("✅ 从 domain.services 导入所有新模块成功")

        return True
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_processor():
    """测试企业信息处理器"""
    print("\n" + "=" * 80)
    print("测试 2: 企业信息处理器测试")
    print("=" * 80)

    try:
        from domain.services.enterprise_processor import EnterpriseProcessor
        from domain.services.search_service import SearchService

        # 创建依赖（SearchService不需要参数）
        search_service = SearchService()

        # 创建处理器
        processor = EnterpriseProcessor(search_service)
        print("✅ 企业信息处理器创建成功")

        # 测试标准化名称
        test_name = "青岛啤酒股份有限公司"
        normalized = processor.normalize_company_name(test_name)
        print(f"✅ 名称标准化: {test_name} -> {normalized}")

        # 测试清洗名称
        dirty_name = "青岛啤酒股份有限公司-企业信息"
        cleaned = processor.clean_company_name(dirty_name)
        print(f"✅ 名称清洗: {dirty_name} -> {cleaned}")

        # 测试提取核心名称
        core_name = processor.extract_core_company_name(dirty_name)
        print(f"✅ 核心名称提取: {dirty_name} -> {core_name}")

        return True
    except Exception as e:
        print(f"❌ 企业信息处理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_enhancer():
    """测试企业数据增强器"""
    print("\n" + "=" * 80)
    print("测试 3: 企业数据增强器测试")
    print("=" * 80)

    try:
        from domain.services.enterprise_enhancer import EnterpriseEnhancer
        from domain.services.data_enhancement_service import DataEnhancementService

        # 创建依赖（DataEnhancementService不需要参数）
        data_enhancement_service = DataEnhancementService()

        # 创建增强器
        enhancer = EnterpriseEnhancer(data_enhancement_service)
        print("✅ 企业数据增强器创建成功")

        # 测试数据（模拟）
        test_data = {
            'customer_name': '青岛啤酒股份有限公司',
            'address': '青岛市市北区登州路56号',
            'industry_name': '',
            'district_name': ''
        }

        # 测试地址增强（可能失败，因为需要外部服务）
        try:
            enhanced = enhancer.enhance_location_info(test_data.copy())
            print(f"✅ 地址信息增强完成")
        except Exception as e:
            print(f"⚠️  地址信息增强跳过（外部服务不可用）: {e}")

        # 测试行业增强
        try:
            enhanced = enhancer.enhance_industry_info(test_data.copy())
            print(f"✅ 行业信息增强完成")
        except Exception as e:
            print(f"⚠️  行业信息增强跳过（外部服务不可用）: {e}")

        # 测试外部数据增强
        external_data = enhancer.enhance_from_external('青岛啤酒股份有限公司', '食品饮料')
        print(f"✅ 外部数据增强完成: {external_data}")

        return True
    except Exception as e:
        print(f"❌ 企业数据增强器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_analyzer():
    """测试企业分析器"""
    print("\n" + "=" * 80)
    print("测试 4: 企业分析器测试")
    print("=" * 80)

    try:
        from domain.services.enterprise_analyzer import EnterpriseAnalyzer
        from domain.services.analysis_service import AnalysisService

        # 创建依赖（AnalysisService不需要参数）
        analysis_service = AnalysisService()

        # 创建分析器
        analyzer = EnterpriseAnalyzer(analysis_service)
        print("✅ 企业分析器创建成功")

        # 测试数据
        test_data = {
            'customer_name': '青岛啤酒股份有限公司',
            'address': '青岛市市北区登州路56号',
            'industry_name': '食品饮料制造业',
            'district_name': '青岛市',
            'chain_status': '链主企业',
            'revenue_info': '暂无营收数据',
            'company_status': '暂无排名信息'
        }

        # 测试备用分析生成
        fallback_analysis = analyzer._generate_fallback_analysis(test_data)
        print(f"✅ 备用分析生成成功")
        print(f"   分析内容: {fallback_analysis[:100]}...")

        # 测试格式化备用结果
        news_data = {'summary': '暂无最新商业资讯', 'references': []}
        fallback_result = analyzer._format_fallback_result(test_data, news_data, fallback_analysis)
        print(f"✅ 格式化备用结果成功")
        print(f"   结果状态: {fallback_result.get('status')}")

        return True
    except Exception as e:
        print(f"❌ 企业分析器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_refactored_service():
    """测试重构后的企业服务"""
    print("\n" + "=" * 80)
    print("测试 5: 重构后的企业服务测试")
    print("=" * 80)

    try:
        from domain.services.enterprise_service_refactored import EnterpriseServiceRefactored
        from domain.services.search_service import SearchService
        from domain.services.data_enhancement_service import DataEnhancementService
        from domain.services.analysis_service import AnalysisService

        # 创建依赖（所有服务都不需要参数）
        search_service = SearchService()
        data_enhancement_service = DataEnhancementService()
        analysis_service = AnalysisService()

        # Mock Repository
        class MockCustomerRepository:
            def find_by_name(self, name):
                # 返回None，模拟本地无数据
                return None

            def update(self, customer_id, updates):
                return {'customer_id': customer_id, **updates}

        customer_repository = MockCustomerRepository()

        # 创建重构后的企业服务
        service = EnterpriseServiceRefactored(
            search_service,
            data_enhancement_service,
            analysis_service,
            customer_repository
        )
        print("✅ 重构后的企业服务创建成功")

        # 验证处理器已初始化
        assert service.processor is not None, "处理器未初始化"
        assert service.enhancer is not None, "增强器未初始化"
        assert service.analyzer is not None, "分析器未初始化"
        print("✅ 所有处理器已正确初始化")

        # 测试基础信息获取（轻量测试，不实际调用外部API）
        result = service.search_local_database("测试公司")
        print(f"✅ 本地数据库搜索测试: {result.get('message')}")

        return True
    except Exception as e:
        print(f"❌ 重构后的企业服务测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_architecture_compliance():
    """测试架构合规性"""
    print("\n" + "=" * 80)
    print("测试 6: 架构合规性测试")
    print("=" * 80)

    try:
        # 检查新模块是否遵循Clean Architecture
        from domain.services import enterprise_processor
        from domain.services import enterprise_enhancer
        from domain.services import enterprise_analyzer
        from domain.services import enterprise_service_refactored

        # 验证依赖方向（domain层不应依赖api层）
        import inspect

        modules_to_check = [
            ('enterprise_processor', enterprise_processor),
            ('enterprise_enhancer', enterprise_enhancer),
            ('enterprise_analyzer', enterprise_analyzer),
            ('enterprise_service_refactored', enterprise_service_refactored)
        ]

        for name, module in modules_to_check:
            source = inspect.getsource(module)

            # 检查是否有对api层的导入（违反架构）
            if 'from api.' in source or 'import api.' in source:
                print(f"❌ {name} 违反架构：依赖了api层")
                return False

            print(f"✅ {name} 架构合规：未依赖api层")

        print("\n✅ 所有模块符合Clean Architecture依赖原则")
        return True

    except Exception as e:
        print(f"❌ 架构合规性测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("🚀 开始阶段四核心业务逻辑重构测试")
    print("=" * 80)

    tests = [
        ("模块导入", test_imports),
        ("企业信息处理器", test_processor),
        ("企业数据增强器", test_enhancer),
        ("企业分析器", test_analyzer),
        ("重构后的企业服务", test_refactored_service),
        ("架构合规性", test_architecture_compliance)
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
        print("\n🎉 阶段四核心业务逻辑重构测试全部通过！")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败，请检查")
        return 1


if __name__ == "__main__":
    exit(main())
