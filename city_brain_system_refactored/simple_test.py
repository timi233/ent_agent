#!/usr/bin/env python3
"""
简化的基础设施测试脚本
测试基本的模块导入和配置加载
"""

def test_config():
    """测试配置模块"""
    print("=== 测试配置模块 ===")
    try:
        from config.settings import get_settings, validate_settings
        settings = get_settings()
        print(f"✓ 配置加载成功")
        print(f"  数据库主机: {settings.database.host}")
        print(f"  数据库端口: {settings.database.port}")
        print(f"  应用名称: {settings.app.app_name}")
        
        if validate_settings():
            print("✓ 配置验证通过")
        else:
            print("✗ 配置验证失败")
            
    except Exception as e:
        print(f"✗ 配置模块测试失败: {e}")
        return False
    return True


def test_database():
    """测试数据库连接模块"""
    print("\n=== 测试数据库连接模块 ===")
    try:
        from infrastructure.database.connection import DatabaseConnection
        db = DatabaseConnection()
        print("✓ 数据库连接类创建成功")
        
        # 注意：这里不实际连接数据库，只测试类的创建
        print("✓ 数据库模块导入成功")
        
    except Exception as e:
        print(f"✗ 数据库模块测试失败: {e}")
        return False
    return True


def test_models():
    """测试数据模型"""
    print("\n=== 测试数据模型 ===")
    try:
        from infrastructure.database.models.customer import Customer
        from infrastructure.database.models.enterprise import Enterprise
        from infrastructure.database.models.industry import Industry
        print("✓ 数据模型导入成功")
        
    except Exception as e:
        print(f"✗ 数据模型测试失败: {e}")
        return False
    return True


def test_repositories():
    """测试仓储层"""
    print("\n=== 测试仓储层 ===")
    try:
        from infrastructure.database.repositories.base_repository import BaseRepository
        from infrastructure.database.repositories.customer_repository import CustomerRepository
        print("✓ 仓储层导入成功")
        
    except Exception as e:
        print(f"✗ 仓储层测试失败: {e}")
        return False
    return True


def test_utils():
    """测试工具类"""
    print("\n=== 测试工具类 ===")
    try:
        from infrastructure.utils.logger import get_logger
        from infrastructure.utils.text_processor import TextProcessor
        from infrastructure.utils.address_processor import AddressProcessor
        
        logger = get_logger("test")
        logger.info("日志系统测试")
        print("✓ 工具类导入成功")
        
    except Exception as e:
        print(f"✗ 工具类测试失败: {e}")
        return False
    return True


def main():
    """主测试函数"""
    print("城市大脑系统基础设施测试")
    print("=" * 50)
    
    tests = [
        test_config,
        test_database, 
        test_models,
        test_repositories,
        test_utils
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n=== 测试结果 ===")
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("✓ 所有测试通过！基础设施准备就绪")
        return True
    else:
        print("✗ 部分测试失败，需要修复")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)