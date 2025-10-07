#!/usr/bin/env python3
"""
测试向后兼容的查询接口
验证新的查询接口是否能正常工作
"""
import sys
import os
import traceback
from typing import Dict, Any, List

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_import_queries():
    """测试查询模块导入"""
    try:
        from infrastructure.database.queries import (
            get_customer_by_name,
            get_customer_by_id,
            get_enterprise_by_name,
            get_enterprise_by_id,
            get_industry_by_id,
            get_area_by_id,
            get_industry_brain_by_id,
            get_comprehensive_enterprise_info
        )
        print("✅ 查询模块导入成功")
        return True
    except Exception as e:
        print(f"❌ 查询模块导入失败: {e}")
        traceback.print_exc()
        return False

def test_repository_initialization():
    """测试仓储初始化"""
    try:
        from infrastructure.database.queries import (
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
        
        print("✅ 所有仓储实例化成功")
        print(f"   - 客户仓储: {type(customer_repo).__name__}")
        print(f"   - 企业仓储: {type(enterprise_repo).__name__}")
        print(f"   - 行业仓储: {type(industry_repo).__name__}")
        print(f"   - 地区仓储: {type(area_repo).__name__}")
        print(f"   - 产业大脑仓储: {type(brain_repo).__name__}")
        return True
    except Exception as e:
        print(f"❌ 仓储初始化失败: {e}")
        traceback.print_exc()
        return False

def test_query_interface_structure():
    """测试查询接口结构"""
    try:
        from infrastructure.database import queries
        
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
            if not hasattr(queries, func_name):
                missing_functions.append(func_name)
        
        if missing_functions:
            print(f"❌ 缺少查询函数: {missing_functions}")
            return False
        
        print("✅ 所有查询接口函数都存在")
        print(f"   - 总计 {len(required_functions)} 个查询函数")
        return True
    except Exception as e:
        print(f"❌ 查询接口结构检查失败: {e}")
        traceback.print_exc()
        return False

def test_mock_query_calls():
    """测试模拟查询调用（不连接真实数据库）"""
    try:
        from infrastructure.database.queries import (
            get_customer_by_name,
            get_enterprise_by_name,
            get_industry_by_id,
            get_comprehensive_enterprise_info
        )
        
        # 这些调用会失败（因为没有数据库连接），但我们检查是否能正确处理异常
        result1 = get_customer_by_name("测试企业")
        result2 = get_enterprise_by_name("测试企业")
        result3 = get_industry_by_id(1)
        result4 = get_comprehensive_enterprise_info("测试企业")
        
        # 所有结果应该是None或空字典（因为数据库连接失败）
        print("✅ 查询函数调用正常（返回默认值）")
        print(f"   - get_customer_by_name: {type(result1)} = {result1}")
        print(f"   - get_enterprise_by_name: {type(result2)} = {result2}")
        print(f"   - get_industry_by_id: {type(result3)} = {result3}")
        print(f"   - get_comprehensive_enterprise_info: {type(result4)} = {result4}")
        return True
    except Exception as e:
        print(f"❌ 模拟查询调用失败: {e}")
        traceback.print_exc()
        return False

def test_backward_compatibility_aliases():
    """测试向后兼容别名"""
    try:
        from infrastructure.database.queries import (
            get_customer_by_name,
            find_customer_by_name,
            get_enterprise_by_name,
            find_enterprise_by_name
        )
        
        # 检查别名是否指向同一个函数
        assert get_customer_by_name is find_customer_by_name, "客户查询别名不匹配"
        assert get_enterprise_by_name is find_enterprise_by_name, "企业查询别名不匹配"
        
        print("✅ 向后兼容别名正常")
        return True
    except Exception as e:
        print(f"❌ 向后兼容别名测试失败: {e}")
        traceback.print_exc()
        return False

def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("🧪 开始测试向后兼容的查询接口")
    print("=" * 60)
    
    tests = [
        ("导入查询模块", test_import_queries),
        ("仓储初始化", test_repository_initialization),
        ("查询接口结构", test_query_interface_structure),
        ("模拟查询调用", test_mock_query_calls),
        ("向后兼容别名", test_backward_compatibility_aliases)
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
        print("🎉 所有测试通过！向后兼容查询接口工作正常")
        return True
    else:
        print("⚠️  部分测试失败，需要修复")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)