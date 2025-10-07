#!/usr/bin/env python3
"""
测试独立的查询接口
验证完全独立的查询接口是否能正常工作
"""
import sys
import os
import traceback
from typing import Dict, Any, List

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_import_standalone_queries():
    """测试独立查询模块导入"""
    try:
        from infrastructure.database.standalone_queries import (
            get_customer_by_name,
            get_customer_by_id,
            get_enterprise_by_name,
            get_enterprise_by_id,
            get_industry_by_id,
            get_area_by_id,
            get_industry_brain_by_id,
            get_comprehensive_enterprise_info
        )
        print("✅ 独立查询模块导入成功")
        return True
    except Exception as e:
        print(f"❌ 独立查询模块导入失败: {e}")
        traceback.print_exc()
        return False

def test_mock_repository_functionality():
    """测试模拟仓储功能"""
    try:
        from infrastructure.database.standalone_queries import (
            _get_customer_repo,
            _get_enterprise_repo,
            _get_industry_repo,
            _get_area_repo,
            _get_brain_repo
        )
        
        # 测试仓储实例化
        customer_repo = _get_customer_repo()
        enterprise_repo = _get_enterprise_repo()
        industry_repo = _get_industry_repo()
        area_repo = _get_area_repo()
        brain_repo = _get_brain_repo()
        
        print("✅ 所有模拟仓储实例化成功")
        print(f"   - 客户仓储: {type(customer_repo).__name__}")
        print(f"   - 企业仓储: {type(enterprise_repo).__name__}")
        print(f"   - 行业仓储: {type(industry_repo).__name__}")
        print(f"   - 地区仓储: {type(area_repo).__name__}")
        print(f"   - 产业大脑仓储: {type(brain_repo).__name__}")
        
        # 测试基本方法调用
        result1 = customer_repo.find_by_name("测试企业")
        result2 = customer_repo.get_statistics()
        result3 = area_repo.get_all_cities()
        
        print(f"   - find_by_name结果: {result1}")
        print(f"   - get_statistics结果: {result2}")
        print(f"   - get_all_cities结果: {result3}")
        
        return True
    except Exception as e:
        print(f"❌ 模拟仓储功能测试失败: {e}")
        traceback.print_exc()
        return False

def test_query_interface_completeness():
    """测试查询接口完整性"""
    try:
        from infrastructure.database import standalone_queries
        
        # 检查主要查询函数是否存在
        required_functions = [
            'get_customer_by_name',
            'get_customer_by_id',
            'update_customer_info',
            'update_customer_address',
            'insert_customer',
            'search_customers_by_keyword',
            'get_customer_statistics',
            'get_enterprise_by_name',
            'get_enterprise_by_id',
            'search_enterprises_by_keyword',
            'get_enterprise_statistics',
            'get_industry_by_id',
            'get_industry_by_name',
            'get_all_industries',
            'get_industry_related_info',
            'get_area_by_id',
            'get_area_by_name',
            'get_all_cities',
            'get_all_areas',
            'get_industry_brain_by_id',
            'get_industry_brain_by_name',
            'get_all_industry_brains',
            'get_industry_brain_related_industries',
            'get_comprehensive_enterprise_info',
            # 向后兼容别名
            'find_customer_by_name',
            'find_customer_by_id',
            'find_enterprise_by_name',
            'find_enterprise_by_id'
        ]
        
        missing_functions = []
        for func_name in required_functions:
            if not hasattr(standalone_queries, func_name):
                missing_functions.append(func_name)
        
        if missing_functions:
            print(f"❌ 缺少查询函数: {missing_functions}")
            return False
        
        print("✅ 所有查询接口函数都存在")
        print(f"   - 总计 {len(required_functions)} 个查询函数")
        return True
    except Exception as e:
        print(f"❌ 查询接口完整性检查失败: {e}")
        traceback.print_exc()
        return False

def test_query_function_calls():
    """测试查询函数调用"""
    try:
        from infrastructure.database.standalone_queries import (
            get_customer_by_name,
            get_enterprise_by_name,
            get_industry_by_id,
            get_comprehensive_enterprise_info,
            update_customer_info,
            insert_customer,
            search_customers_by_keyword,
            get_customer_statistics,
            get_all_cities,
            get_all_industries
        )
        
        # 测试各种查询函数调用
        test_cases = [
            ("get_customer_by_name", lambda: get_customer_by_name("测试企业")),
            ("get_enterprise_by_name", lambda: get_enterprise_by_name("测试企业")),
            ("get_industry_by_id", lambda: get_industry_by_id(1)),
            ("get_comprehensive_enterprise_info", lambda: get_comprehensive_enterprise_info("测试企业")),
            ("update_customer_info", lambda: update_customer_info(1, {"address": "新地址"})),
            ("insert_customer", lambda: insert_customer({"customer_name": "新企业", "address": "测试地址"})),
            ("search_customers_by_keyword", lambda: search_customers_by_keyword("测试")),
            ("get_customer_statistics", lambda: get_customer_statistics()),
            ("get_all_cities", lambda: get_all_cities()),
            ("get_all_industries", lambda: get_all_industries())
        ]
        
        results = {}
        for func_name, func_call in test_cases:
            try:
                result = func_call()
                results[func_name] = {
                    'success': True,
                    'result_type': type(result).__name__,
                    'result': result
                }
            except Exception as e:
                results[func_name] = {
                    'success': False,
                    'error': str(e)
                }
        
        # 统计结果
        successful_calls = sum(1 for r in results.values() if r['success'])
        total_calls = len(test_cases)
        
        print("✅ 查询函数调用测试完成")
        print(f"   - 成功调用: {successful_calls}/{total_calls}")
        
        for func_name, result in results.items():
            if result['success']:
                print(f"   - {func_name}: ✅ {result['result_type']} = {result['result']}")
            else:
                print(f"   - {func_name}: ❌ {result['error']}")
        
        return successful_calls == total_calls
    except Exception as e:
        print(f"❌ 查询函数调用测试失败: {e}")
        traceback.print_exc()
        return False

def test_backward_compatibility():
    """测试向后兼容性"""
    try:
        from infrastructure.database.standalone_queries import (
            get_customer_by_name,
            find_customer_by_name,
            get_enterprise_by_name,
            find_enterprise_by_name
        )
        
        # 检查别名是否指向同一个函数
        assert get_customer_by_name is find_customer_by_name, "客户查询别名不匹配"
        assert get_enterprise_by_name is find_enterprise_by_name, "企业查询别名不匹配"
        
        # 测试别名调用
        result1 = find_customer_by_name("测试企业")
        result2 = find_enterprise_by_name("测试企业")
        
        print("✅ 向后兼容性测试通过")
        print(f"   - find_customer_by_name: {type(result1)} = {result1}")
        print(f"   - find_enterprise_by_name: {type(result2)} = {result2}")
        return True
    except Exception as e:
        print(f"❌ 向后兼容性测试失败: {e}")
        traceback.print_exc()
        return False

def test_data_model_functionality():
    """测试数据模型功能"""
    try:
        from infrastructure.database.standalone_queries import MockDataModel
        
        # 创建测试数据模型
        model = MockDataModel(
            id=1,
            name="测试企业",
            address="测试地址",
            industry_id=1
        )
        
        # 测试属性访问
        assert model.id == 1
        assert model.name == "测试企业"
        assert model.address == "测试地址"
        assert model.industry_id == 1
        
        # 测试to_dict方法
        data_dict = model.to_dict()
        expected_keys = {'id', 'name', 'address', 'industry_id'}
        assert set(data_dict.keys()) == expected_keys
        
        print("✅ 数据模型功能测试通过")
        print(f"   - 模型属性: {list(data_dict.keys())}")
        print(f"   - 字典转换: {data_dict}")
        return True
    except Exception as e:
        print(f"❌ 数据模型功能测试失败: {e}")
        traceback.print_exc()
        return False

def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("🧪 开始测试独立查询接口")
    print("=" * 60)
    
    tests = [
        ("导入独立查询模块", test_import_standalone_queries),
        ("模拟仓储功能", test_mock_repository_functionality),
        ("查询接口完整性", test_query_interface_completeness),
        ("查询函数调用", test_query_function_calls),
        ("向后兼容性", test_backward_compatibility),
        ("数据模型功能", test_data_model_functionality)
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
    print(f"📊 测试结果: {passed}/{total} 通过 ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 所有测试通过！独立查询接口工作正常")
        return True
    else:
        print("⚠️  部分测试失败，需要修复")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)