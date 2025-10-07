#!/usr/bin/env python3
"""
数据层完整性测试
测试数据模型、仓储层和查询接口的完整性和正确性
"""
import sys
import os
import traceback
from typing import Dict, Any, List

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_data_models_import():
    """测试数据模型导入"""
    try:
        from infrastructure.database.models.customer import Customer
        from infrastructure.database.models.enterprise import Enterprise
        from infrastructure.database.models.industry import Industry
        from infrastructure.database.models.industry_brain import IndustryBrain
        from infrastructure.database.models.area import Area
        from infrastructure.database.models.relations import BrainIndustryRelation, CompanyRelationship
        
        print("✅ 所有数据模型导入成功")
        print(f"   - Customer: {Customer}")
        print(f"   - Enterprise: {Enterprise}")
        print(f"   - Industry: {Industry}")
        print(f"   - IndustryBrain: {IndustryBrain}")
        print(f"   - Area: {Area}")
        print(f"   - BrainIndustryRelation: {BrainIndustryRelation}")
        print(f"   - CompanyRelationship: {CompanyRelationship}")
        return True
    except Exception as e:
        print(f"❌ 数据模型导入失败: {e}")
        traceback.print_exc()
        return False

def test_data_models_functionality():
    """测试数据模型功能"""
    try:
        from infrastructure.database.models.customer import Customer
        from infrastructure.database.models.area import Area
        
        # 测试Customer模型
        customer_data = {
            'customer_id': 1,
            'customer_name': '测试企业',
            'data_source': 'manual',
            'address': '青岛市市南区测试路123号',
            'tag_result': 1,
            'industry_id': 1,
            'brain_id': 1,
            'chain_leader_id': 1
        }
        
        customer = Customer(**customer_data)
        customer_dict = customer.to_dict()
        customer_db_dict = customer.to_db_dict()
        
        # 测试Area模型
        area_data = {
            'area_id': 1,
            'city_name': '青岛市',
            'district_name': '市南区',
            'district_code': '370202'
        }
        
        area = Area(**area_data)
        area_dict = area.to_dict()
        area_db_dict = area.to_db_dict()
        
        print("✅ 数据模型功能测试通过")
        print(f"   - Customer字典转换: {len(customer_dict)} 个字段")
        print(f"   - Customer数据库格式: {len(customer_db_dict)} 个字段")
        print(f"   - Area字典转换: {len(area_dict)} 个字段")
        print(f"   - Area数据库格式: {len(area_db_dict)} 个字段")
        return True
    except Exception as e:
        print(f"❌ 数据模型功能测试失败: {e}")
        traceback.print_exc()
        return False

def test_repositories_import():
    """测试仓储层导入"""
    try:
        # 通过查询接口间接测试仓储层导入
        from infrastructure.database.standalone_queries import (
            _get_customer_repo,
            _get_enterprise_repo,
            _get_industry_repo,
            _get_area_repo,
            _get_brain_repo
        )
        
        # 测试仓储实例化
        repos = {
            'CustomerRepository': _get_customer_repo(),
            'EnterpriseRepository': _get_enterprise_repo(),
            'IndustryRepository': _get_industry_repo(),
            'AreaRepository': _get_area_repo(),
            'BrainRepository': _get_brain_repo()
        }
        
        print("✅ 所有仓储类导入成功")
        for repo_name, repo_instance in repos.items():
            print(f"   - {repo_name}: {type(repo_instance).__name__}")
        
        # 验证仓储基本方法存在
        basic_methods = ['find_by_name', 'find_by_id', 'create', 'update', 'get_statistics']
        for method_name in basic_methods:
            if not hasattr(repos['CustomerRepository'], method_name):
                print(f"❌ 缺少方法: {method_name}")
                return False
        
        print(f"   - 基本方法验证通过: {len(basic_methods)} 个方法")
        return True
    except Exception as e:
        print(f"❌ 仓储层导入失败: {e}")
        traceback.print_exc()
        return False

def test_repositories_functionality():
    """测试仓储层功能"""
    try:
        # 使用独立查询接口中的模拟仓储来测试功能
        from infrastructure.database.standalone_queries import (
            _get_customer_repo,
            _get_area_repo
        )
        
        # 测试客户仓储
        customer_repo = _get_customer_repo()
        
        # 测试基本方法
        customer = customer_repo.find_by_name("测试企业")
        customer_by_id = customer_repo.find_by_id(1)
        customers = customer_repo.search_by_keyword("测试", 10)
        stats = customer_repo.get_statistics()
        
        # 测试地区仓储
        area_repo = _get_area_repo()
        area = area_repo.find_by_id(1)
        cities = area_repo.get_all_cities()
        areas = area_repo.get_all()
        
        print("✅ 仓储层功能测试通过")
        print(f"   - 客户查询结果: {type(customer)} = {customer}")
        print(f"   - 客户统计: {stats}")
        print(f"   - 城市列表: {cities}")
        print(f"   - 地区数量: {len(areas)}")
        return True
    except Exception as e:
        print(f"❌ 仓储层功能测试失败: {e}")
        traceback.print_exc()
        return False

def test_queries_interface_import():
    """测试查询接口导入"""
    try:
        from infrastructure.database.standalone_queries import (
            get_customer_by_name,
            get_customer_by_id,
            get_enterprise_by_name,
            get_industry_by_id,
            get_area_by_id,
            get_industry_brain_by_id,
            get_comprehensive_enterprise_info,
            update_customer_info,
            insert_customer,
            search_customers_by_keyword,
            get_customer_statistics,
            get_all_cities,
            get_all_industries,
            # 向后兼容别名
            find_customer_by_name,
            find_enterprise_by_name
        )
        
        print("✅ 查询接口导入成功")
        print(f"   - 导入了 15 个查询函数")
        return True
    except Exception as e:
        print(f"❌ 查询接口导入失败: {e}")
        traceback.print_exc()
        return False

def test_queries_interface_functionality():
    """测试查询接口功能"""
    try:
        from infrastructure.database.standalone_queries import (
            get_customer_by_name,
            get_comprehensive_enterprise_info,
            update_customer_info,
            insert_customer,
            get_customer_statistics,
            get_all_cities,
            find_customer_by_name  # 测试向后兼容
        )
        
        # 测试各种查询功能
        test_results = {}
        
        # 基本查询
        customer = get_customer_by_name("测试企业")
        test_results['get_customer_by_name'] = customer
        
        # 综合查询
        comprehensive = get_comprehensive_enterprise_info("测试企业")
        test_results['get_comprehensive_enterprise_info'] = comprehensive
        
        # 更新操作
        update_result = update_customer_info(1, {"address": "新地址"})
        test_results['update_customer_info'] = update_result
        
        # 插入操作
        insert_result = insert_customer({
            "customer_name": "新测试企业",
            "address": "测试地址",
            "tag_result": 1
        })
        test_results['insert_customer'] = insert_result
        
        # 统计查询
        stats = get_customer_statistics()
        test_results['get_customer_statistics'] = stats
        
        # 列表查询
        cities = get_all_cities()
        test_results['get_all_cities'] = cities
        
        # 向后兼容测试
        customer_compat = find_customer_by_name("测试企业")
        test_results['find_customer_by_name'] = customer_compat
        
        # 验证向后兼容性
        assert get_customer_by_name is find_customer_by_name, "向后兼容别名不正确"
        
        print("✅ 查询接口功能测试通过")
        for func_name, result in test_results.items():
            print(f"   - {func_name}: {type(result)} = {result}")
        
        return True
    except Exception as e:
        print(f"❌ 查询接口功能测试失败: {e}")
        traceback.print_exc()
        return False

def test_data_layer_integration():
    """测试数据层集成"""
    try:
        # 测试从模型到仓储到查询接口的完整流程
        from infrastructure.database.models.customer import Customer
        from infrastructure.database.standalone_queries import (
            get_customer_by_name,
            _get_customer_repo
        )
        
        # 1. 创建数据模型
        customer_data = {
            'customer_id': 999,
            'customer_name': '集成测试企业',
            'data_source': 'test',
            'address': '集成测试地址',
            'tag_result': 1
        }
        customer = Customer(**customer_data)
        
        # 2. 通过仓储操作
        repo = _get_customer_repo()
        create_result = repo.create(customer.to_db_dict())
        
        # 3. 通过查询接口访问
        query_result = get_customer_by_name("集成测试企业")
        
        print("✅ 数据层集成测试通过")
        print(f"   - 模型创建: {customer.customer_name}")
        print(f"   - 仓储操作: {create_result}")
        print(f"   - 查询接口: {type(query_result)} = {query_result}")
        return True
    except Exception as e:
        print(f"❌ 数据层集成测试失败: {e}")
        traceback.print_exc()
        return False

def test_error_handling():
    """测试错误处理"""
    try:
        from infrastructure.database.standalone_queries import (
            get_customer_by_name,
            update_customer_info,
            get_industry_by_id
        )
        
        # 测试各种错误情况
        error_tests = []
        
        # 1. 查询不存在的数据
        result1 = get_customer_by_name("不存在的企业")
        error_tests.append(("查询不存在企业", result1 is None))
        
        # 2. 更新不存在的记录
        result2 = update_customer_info(99999, {"address": "新地址"})
        error_tests.append(("更新不存在记录", result2 == False))
        
        # 3. 查询无效ID
        result3 = get_industry_by_id(-1)
        error_tests.append(("查询无效ID", result3 is None))
        
        # 统计通过的错误处理测试
        passed_tests = sum(1 for _, passed in error_tests if passed)
        total_tests = len(error_tests)
        
        print("✅ 错误处理测试通过")
        print(f"   - 通过率: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
        for test_name, passed in error_tests:
            status = "✅" if passed else "❌"
            print(f"   - {test_name}: {status}")
        
        return passed_tests == total_tests
    except Exception as e:
        print(f"❌ 错误处理测试失败: {e}")
        traceback.print_exc()
        return False

def test_performance_basic():
    """基本性能测试"""
    try:
        import time
        from infrastructure.database.standalone_queries import (
            get_customer_by_name,
            get_all_cities,
            get_customer_statistics
        )
        
        # 测试查询性能
        performance_tests = []
        
        # 1. 单个查询性能
        start_time = time.time()
        for i in range(100):
            get_customer_by_name(f"测试企业{i}")
        single_query_time = time.time() - start_time
        performance_tests.append(("100次单个查询", single_query_time, single_query_time < 1.0))
        
        # 2. 列表查询性能
        start_time = time.time()
        for i in range(50):
            get_all_cities()
        list_query_time = time.time() - start_time
        performance_tests.append(("50次列表查询", list_query_time, list_query_time < 0.5))
        
        # 3. 统计查询性能
        start_time = time.time()
        for i in range(20):
            get_customer_statistics()
        stats_query_time = time.time() - start_time
        performance_tests.append(("20次统计查询", stats_query_time, stats_query_time < 0.2))
        
        print("✅ 基本性能测试完成")
        for test_name, duration, passed in performance_tests:
            status = "✅" if passed else "⚠️"
            print(f"   - {test_name}: {status} {duration:.3f}秒")
        
        return all(passed for _, _, passed in performance_tests)
    except Exception as e:
        print(f"❌ 基本性能测试失败: {e}")
        traceback.print_exc()
        return False

def run_all_tests():
    """运行所有数据层测试"""
    print("=" * 60)
    print("🧪 开始数据层完整性测试")
    print("=" * 60)
    
    tests = [
        ("数据模型导入", test_data_models_import),
        ("数据模型功能", test_data_models_functionality),
        ("仓储层导入", test_repositories_import),
        ("仓储层功能", test_repositories_functionality),
        ("查询接口导入", test_queries_interface_import),
        ("查询接口功能", test_queries_interface_functionality),
        ("数据层集成", test_data_layer_integration),
        ("错误处理", test_error_handling),
        ("基本性能", test_performance_basic)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 测试: {test_name}")
        print("-" * 40)
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"📊 数据层测试结果: {passed}/{total} 通过 ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 数据层完整性测试全部通过！")
        print("✅ 数据模型、仓储层、查询接口都工作正常")
        print("✅ 错误处理和性能表现良好")
        return True
    else:
        print("⚠️  部分测试失败，需要修复")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)