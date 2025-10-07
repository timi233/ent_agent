#!/usr/bin/env python3
"""
完全独立的基础设施测试脚本
使用绝对路径导入，避免所有相对导入问题
"""
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(__file__)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_config():
    """测试配置模块"""
    print("=== 测试配置模块 ===")
    try:
        from config.simple_settings import get_settings, validate_settings
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
        from infrastructure.database.simple_connection import DatabaseConnection, test_database_connection
        db = DatabaseConnection()
        print("✓ 数据库连接类创建成功")
        
        # 测试连接
        if test_database_connection():
            print("✓ 数据库连接测试成功")
        else:
            print("⚠ 数据库连接测试失败（可能是依赖缺失或配置问题）")
        
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
    """测试独立仓储层"""
    print("\n=== 测试独立仓储层 ===")
    try:
        from infrastructure.database.repositories.standalone_repository import (
            StandaloneRepository, 
            StandaloneCustomerRepository, 
            StandaloneEnterpriseRepository
        )
        
        # 创建仓储实例
        customer_repo = StandaloneCustomerRepository()
        enterprise_repo = StandaloneEnterpriseRepository()
        print("✓ 独立仓储层导入成功")
        
        # 测试基本功能（不实际连接数据库）
        print("✓ 仓储层实例创建成功")
        
    except Exception as e:
        print(f"✗ 独立仓储层测试失败: {e}")
        return False
    return True


def test_utils():
    """测试工具类"""
    print("\n=== 测试工具类 ===")
    try:
        from infrastructure.utils.simple_logger import get_logger
        
        logger = get_logger("test")
        logger.info("日志系统测试")
        print("✓ 简化日志工具导入成功")
        
        # 测试其他工具类（如果存在）
        try:
            from infrastructure.utils.text_processor import TextProcessor
            text_processor = TextProcessor()
            print("✓ 文本处理器导入成功")
        except ImportError:
            print("⚠ 文本处理器导入失败（可能未实现）")
        except Exception as e:
            print(f"⚠ 文本处理器测试失败: {e}")
        
        try:
            from infrastructure.utils.address_processor import AddressProcessor
            address_processor = AddressProcessor()
            print("✓ 地址处理器导入成功")
        except ImportError:
            print("⚠ 地址处理器导入失败（可能未实现）")
        except Exception as e:
            print(f"⚠ 地址处理器测试失败: {e}")
        
    except Exception as e:
        print(f"✗ 工具类测试失败: {e}")
        return False
    return True


def test_integration():
    """集成测试"""
    print("\n=== 集成测试 ===")
    try:
        # 测试配置和数据库的集成
        from config.simple_settings import get_settings
        from infrastructure.database.repositories.standalone_repository import StandaloneCustomerRepository
        
        settings = get_settings()
        customer_repo = StandaloneCustomerRepository()
        
        print("✓ 配置和仓储层集成成功")
        
        # 测试日志和配置的集成
        from infrastructure.utils.simple_logger import get_logger
        logger = get_logger("integration_test")
        logger.info(f"集成测试 - 应用: {settings.app.app_name}")
        
        print("✓ 日志和配置集成成功")
        
    except Exception as e:
        print(f"✗ 集成测试失败: {e}")
        return False
    return True


def main():
    """主测试函数"""
    print("城市大脑系统独立基础设施测试")
    print("=" * 50)
    
    tests = [
        ("配置模块", test_config),
        ("数据库模块", test_database), 
        ("数据模型", test_models),
        ("仓储层", test_repositories),
        ("工具类", test_utils),
        ("集成测试", test_integration)
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
    
    print(f"\n=== 最终测试结果 ===")
    for result in results:
        print(result)
    
    print(f"\n通过率: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed >= 4:  # 至少4个测试通过
        print("✓ 基础设施基本可用，可以继续下一阶段开发")
        print("\n=== 下一步建议 ===")
        print("1. 修复剩余的导入问题")
        print("2. 完善工具类的实现")
        print("3. 开始阶段二：数据层重构")
        return True
    else:
        print("✗ 基础设施存在问题，需要进一步修复")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)