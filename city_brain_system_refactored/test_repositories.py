#!/usr/bin/env python3
"""
增强版仓储层测试脚本
测试所有增强版仓储类的功能
"""
import sys
import os
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_repository_imports():
    """测试仓储类导入"""
    try:
        from infrastructure.database.repositories import (
            EnhancedCustomerRepository,
            EnhancedEnterpriseRepository,
            EnhancedIndustryRepository,
            AreaRepository,
            IndustryBrainRepository,
            get_repository,
            REPOSITORY_REGISTRY
        )
        logger.info("✅ 所有增强版仓储类导入成功")
        return True
    except Exception as e:
        logger.error(f"❌ 仓储类导入失败: {e}")
        return False

def test_repository_registry():
    """测试仓储注册表功能"""
    try:
        from infrastructure.database.repositories import get_repository, REPOSITORY_REGISTRY
        
        # 测试注册表内容
        expected_types = ['customer', 'enterprise', 'industry', 'area', 'industry_brain']
        for repo_type in expected_types:
            if repo_type not in REPOSITORY_REGISTRY:
                logger.error(f"❌ 仓储类型 {repo_type} 未在注册表中")
                return False
        
        # 测试获取仓储实例
        customer_repo = get_repository('customer')
        if customer_repo is None:
            logger.error("❌ 无法获取客户仓储实例")
            return False
        
        logger.info("✅ 仓储注册表功能正常")
        return True
    except Exception as e:
        logger.error(f"❌ 仓储注册表测试失败: {e}")
        return False

def test_repository_initialization():
    """测试仓储类初始化"""
    try:
        from infrastructure.database.repositories import (
            EnhancedCustomerRepository,
            EnhancedEnterpriseRepository,
            EnhancedIndustryRepository,
            AreaRepository,
            IndustryBrainRepository
        )
        
        # 测试各个仓储类的初始化
        repos = [
            ('客户仓储', EnhancedCustomerRepository),
            ('企业仓储', EnhancedEnterpriseRepository),
            ('行业仓储', EnhancedIndustryRepository),
            ('地区仓储', AreaRepository),
            ('产业大脑仓储', IndustryBrainRepository)
        ]
        
        for name, repo_class in repos:
            try:
                repo = repo_class()
                if hasattr(repo, 'table_name'):
                    logger.info(f"✅ {name}初始化成功，表名: {repo.table_name}")
                else:
                    logger.info(f"✅ {name}初始化成功")
            except Exception as e:
                logger.error(f"❌ {name}初始化失败: {e}")
                return False
        
        return True
    except Exception as e:
        logger.error(f"❌ 仓储类初始化测试失败: {e}")
        return False

def test_repository_methods():
    """测试仓储类方法"""
    try:
        from infrastructure.database.repositories import EnhancedCustomerRepository
        
        # 创建客户仓储实例
        customer_repo = EnhancedCustomerRepository()
        
        # 测试方法是否存在
        expected_methods = [
            'find_by_name', 'find_by_id', 'find_by_industry', 
            'find_by_area', 'search_by_keyword', 'create', 
            'update', 'update_address', 'get_statistics'
        ]
        
        for method_name in expected_methods:
            if not hasattr(customer_repo, method_name):
                logger.error(f"❌ 客户仓储缺少方法: {method_name}")
                return False
            if not callable(getattr(customer_repo, method_name)):
                logger.error(f"❌ 客户仓储方法不可调用: {method_name}")
                return False
        
        logger.info("✅ 仓储类方法检查通过")
        return True
    except Exception as e:
        logger.error(f"❌ 仓储类方法测试失败: {e}")
        return False

def test_data_model_integration():
    """测试数据模型集成"""
    try:
        from infrastructure.database.models import Customer, Enterprise, Industry, Area
        from infrastructure.database.repositories import EnhancedCustomerRepository
        
        # 测试创建数据模型实例
        customer = Customer(
            customer_id=1,
            customer_name="测试企业",
            data_source="test",
            address="测试地址",
            tag_result=1
        )
        
        # 测试数据模型方法
        customer_dict = customer.to_dict()
        if not isinstance(customer_dict, dict):
            logger.error("❌ 客户模型to_dict方法返回类型错误")
            return False
        
        # 测试仓储与模型的集成
        repo = EnhancedCustomerRepository()
        if hasattr(repo, '_create_customer_from_result'):
            logger.info("✅ 仓储类包含模型创建方法")
        
        logger.info("✅ 数据模型集成测试通过")
        return True
    except Exception as e:
        logger.error(f"❌ 数据模型集成测试失败: {e}")
        return False

def main():
    """主测试函数"""
    logger.info("开始增强版仓储层测试...")
    
    tests = [
        ("仓储类导入", test_repository_imports),
        ("仓储注册表", test_repository_registry),
        ("仓储类初始化", test_repository_initialization),
        ("仓储类方法", test_repository_methods),
        ("数据模型集成", test_data_model_integration),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- 测试: {test_name} ---")
        try:
            if test_func():
                passed += 1
                logger.info(f"✅ {test_name} 通过")
            else:
                logger.error(f"❌ {test_name} 失败")
        except Exception as e:
            logger.error(f"❌ {test_name} 异常: {e}")
    
    # 输出测试结果
    success_rate = (passed / total) * 100
    logger.info(f"\n{'='*50}")
    logger.info(f"增强版仓储层测试完成")
    logger.info(f"通过率: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate == 100:
        logger.info("✅ 增强版仓储层测试通过！可以继续下一阶段开发")
        return True
    else:
        logger.warning("⚠️  部分测试未通过，需要修复后再继续")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)