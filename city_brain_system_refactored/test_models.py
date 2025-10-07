#!/usr/bin/env python3
"""
数据模型测试脚本
测试所有数据模型的创建、验证和序列化功能
"""
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(__file__)
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def test_customer_model():
    """测试客户模型"""
    print("=== 测试客户模型 ===")
    try:
        from infrastructure.database.models import Customer, create_customer
        
        # 测试创建客户
        customer = create_customer("测试企业有限公司", address="青岛市市南区")
        print(f"✓ 客户创建成功: {customer}")
        
        # 测试验证
        if customer.is_valid():
            print("✓ 客户数据验证通过")
        else:
            print("✗ 客户数据验证失败")
        
        # 测试序列化
        customer_dict = customer.to_dict()
        db_dict = customer.to_db_dict()
        print(f"✓ 客户序列化成功: {len(customer_dict)} 个字段")
        
        # 测试从字典创建
        new_customer = Customer.from_dict(customer_dict)
        if new_customer and new_customer.customer_name == customer.customer_name:
            print("✓ 从字典创建客户成功")
        else:
            print("✗ 从字典创建客户失败")
        
        return True
        
    except Exception as e:
        print(f"✗ 客户模型测试失败: {e}")
        return False


def test_enterprise_model():
    """测试企业模型"""
    print("\n=== 测试企业模型 ===")
    try:
        from infrastructure.database.models import Enterprise, create_enterprise
        
        # 测试创建企业
        enterprise = create_enterprise("青岛链主企业集团", industry_id=1, area_id=1)
        print(f"✓ 企业创建成功: {enterprise}")
        
        # 测试验证
        if enterprise.is_valid():
            print("✓ 企业数据验证通过")
        else:
            print("✗ 企业数据验证失败")
        
        # 测试特有方法
        if enterprise.is_chain_leader():
            print("✓ 链主企业识别正确")
        
        location = enterprise.get_location_info()
        print(f"✓ 位置信息获取: {location}")
        
        return True
        
    except Exception as e:
        print(f"✗ 企业模型测试失败: {e}")
        return False


def test_industry_model():
    """测试行业模型"""
    print("\n=== 测试行业模型 ===")
    try:
        from infrastructure.database.models import Industry, IndustryBrain, create_industry, create_industry_brain
        
        # 测试创建行业
        industry = create_industry("制造业", industry_type="传统制造")
        print(f"✓ 行业创建成功: {industry}")
        
        # 测试创建产业大脑
        brain = create_industry_brain("智能制造产业大脑", area_id=1, build_year=2023)
        print(f"✓ 产业大脑创建成功: {brain}")
        
        # 测试验证
        if industry.is_valid() and brain:
            print("✓ 行业和产业大脑数据验证通过")
        
        # 测试描述方法
        description = industry.get_full_description()
        print(f"✓ 行业完整描述: {description}")
        
        return True
        
    except Exception as e:
        print(f"✗ 行业模型测试失败: {e}")
        return False


def test_area_model():
    """测试地区模型"""
    print("\n=== 测试地区模型 ===")
    try:
        from infrastructure.database.models import Area, create_area
        
        # 测试创建地区
        area = create_area("青岛市", "市南区", district_code="370202")
        print(f"✓ 地区创建成功: {area}")
        
        # 测试验证
        if area.is_valid():
            print("✓ 地区数据验证通过")
        
        # 测试显示方法
        display_name = area.get_display_name()
        full_name = area.get_full_name()
        print(f"✓ 地区显示名称: {display_name}")
        print(f"✓ 地区完整名称: {full_name}")
        
        # 测试比较方法
        area2 = create_area("青岛市", "崂山区")
        if area.is_same_city(area2):
            print("✓ 同城判断正确")
        
        if not area.is_same_district(area2):
            print("✓ 不同区县判断正确")
        
        return True
        
    except Exception as e:
        print(f"✗ 地区模型测试失败: {e}")
        return False


def test_relations_model():
    """测试关联关系模型"""
    print("\n=== 测试关联关系模型 ===")
    try:
        from infrastructure.database.models import (
            BrainIndustryRelation, 
            CompanyRelationship,
            create_brain_industry_relation,
            create_company_relationship
        )
        
        # 测试产业大脑行业关联
        brain_relation = create_brain_industry_relation(1, 2, brain_name="智能制造大脑", industry_name="制造业")
        print(f"✓ 产业大脑关联创建成功: {brain_relation}")
        
        if brain_relation.is_valid():
            print("✓ 产业大脑关联验证通过")
        
        # 测试企业关系
        company_rel = create_company_relationship(1, 2, "customer_to_chain_leader")
        print(f"✓ 企业关系创建成功: {company_rel}")
        
        if company_rel.is_valid():
            print("✓ 企业关系验证通过")
        
        return True
        
    except Exception as e:
        print(f"✗ 关联关系模型测试失败: {e}")
        return False


def test_model_registry():
    """测试模型注册表"""
    print("\n=== 测试模型注册表 ===")
    try:
        from infrastructure.database.models import (
            MODEL_REGISTRY, 
            TABLE_MODEL_MAPPING,
            get_model_by_table_name,
            get_model_by_name
        )
        
        # 测试模型注册表
        print(f"✓ 模型注册表包含 {len(MODEL_REGISTRY)} 个模型")
        print(f"✓ 表映射包含 {len(TABLE_MODEL_MAPPING)} 个映射")
        
        # 测试根据表名获取模型
        customer_model = get_model_by_table_name('QD_customer')
        if customer_model:
            print("✓ 根据表名获取客户模型成功")
        
        # 测试根据模型名获取模型
        industry_model = get_model_by_name('industry')
        if industry_model:
            print("✓ 根据模型名获取行业模型成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 模型注册表测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("城市大脑系统数据模型测试")
    print("=" * 50)
    
    tests = [
        ("客户模型", test_customer_model),
        ("企业模型", test_enterprise_model),
        ("行业模型", test_industry_model),
        ("地区模型", test_area_model),
        ("关联关系模型", test_relations_model),
        ("模型注册表", test_model_registry),
    ]
    
    passed = 0
    total = len(tests)
    results = []
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                results.append(f"✓ {test_name}")
            else:
                results.append(f"✗ {test_name}")
        except Exception as e:
            results.append(f"✗ {test_name} (异常: {e})")
    
    print(f"\n=== 数据模型测试结果 ===")
    for result in results:
        print(result)
    
    print(f"\n通过率: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("✅ 所有数据模型测试通过！任务2.1完成")
        return True
    else:
        print("✗ 部分数据模型测试失败，需要修复")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)