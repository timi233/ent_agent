#!/usr/bin/env python3
"""
基础设施测试脚本
验证所有重构的模块可以正常导入和基本功能运行
"""
import sys
import traceback
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_config_modules():
    """测试配置模块"""
    print("🔧 测试配置模块...")
    
    try:
        from config.settings import get_settings, Settings
        settings = get_settings()
        print(f"  ✅ 配置加载成功: {settings.APP_NAME}")
        
        from config.database import DatabaseManager
        db_manager = DatabaseManager()
        print("  ✅ 数据库管理器初始化成功")
        
        return True
    except Exception as e:
        print(f"  ❌ 配置模块测试失败: {e}")
        traceback.print_exc()
        return False

def test_database_models():
    """测试数据库模型"""
    print("🗄️ 测试数据库模型...")
    
    try:
        from infrastructure.database.models import (
            Customer, Enterprise, Industry, IndustryBrain,
            create_customer, create_enterprise, create_industry, create_industry_brain
        )
        
        # 测试模型创建
        test_customer_data = {
            'customer_id': 1,
            'customer_name': '测试企业',
            'address': '测试地址',
            'tag_result': 1
        }
        customer = create_customer(test_customer_data)
        print(f"  ✅ 客户模型创建成功: {customer.customer_name}")
        
        test_enterprise_data = {
            'enterprise_id': 1,
            'enterprise_name': '测试链主企业',
            'industry_id': 1,
            'area_id': 1
        }
        enterprise = create_enterprise(test_enterprise_data)
        print(f"  ✅ 企业模型创建成功: {enterprise.enterprise_name}")
        
        return True
    except Exception as e:
        print(f"  ❌ 数据库模型测试失败: {e}")
        traceback.print_exc()
        return False

def test_database_repositories():
    """测试数据库仓储"""
    print("📚 测试数据库仓储...")
    
    try:
        from infrastructure.database.repositories import (
            BaseRepository, CustomerRepository, EnterpriseRepository,
            IndustryRepository, IndustryBrainRepository, AreaRepository
        )
        
        # 测试仓储初始化（不连接真实数据库）
        customer_repo = CustomerRepository()
        enterprise_repo = EnterpriseRepository()
        industry_repo = IndustryRepository()
        
        print("  ✅ 客户仓储初始化成功")
        print("  ✅ 企业仓储初始化成功")
        print("  ✅ 行业仓储初始化成功")
        
        return True
    except Exception as e:
        print(f"  ❌ 数据库仓储测试失败: {e}")
        traceback.print_exc()
        return False

def test_utils_modules():
    """测试工具模块"""
    print("🛠️ 测试工具模块...")
    
    try:
        # 测试日志工具
        from infrastructure.utils.logger import get_logger, CityBrainLogger
        logger = get_logger()
        logger.log_company_query("测试企业", "测试查询", "测试成功")
        print("  ✅ 日志工具测试成功")
        
        # 测试文本处理工具
        from infrastructure.utils.text_processor import (
            CompanyNameExtractor, extract_company_name, is_complete_company_name
        )
        extractor = CompanyNameExtractor()
        result = extractor.extract_company_name("青岛海尔智家股份有限公司")
        if result and result['name']:
            print(f"  ✅ 文本处理工具测试成功: {result['name']}")
        else:
            print("  ⚠️ 文本处理工具测试无结果")
        
        # 测试地址处理工具
        from infrastructure.utils.address_processor import (
            AddressExtractor, extract_city_from_address
        )
        extractor = AddressExtractor()
        city = extractor.extract_city_from_address("山东省青岛市市南区香港中路12号")
        if city:
            print(f"  ✅ 地址处理工具测试成功: {city}")
        else:
            print("  ⚠️ 地址处理工具测试无结果")
        
        return True
    except Exception as e:
        print(f"  ❌ 工具模块测试失败: {e}")
        traceback.print_exc()
        return False

def test_module_imports():
    """测试模块导入"""
    print("📦 测试模块导入...")
    
    modules_to_test = [
        'config',
        'config.settings',
        'config.database',
        'infrastructure',
        'infrastructure.database',
        'infrastructure.database.connection',
        'infrastructure.database.models',
        'infrastructure.database.repositories',
        'infrastructure.utils',
        'api',
        'api.v1',
        'core',
        'core.company',
        'core.search',
        'core.ai',
    ]
    
    success_count = 0
    total_count = len(modules_to_test)
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"  ✅ {module_name}")
            success_count += 1
        except ImportError as e:
            print(f"  ❌ {module_name}: {e}")
        except Exception as e:
            print(f"  ⚠️ {module_name}: {e}")
    
    print(f"  📊 导入成功率: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    return success_count == total_count

def test_backward_compatibility():
    """测试向后兼容性"""
    print("🔄 测试向后兼容性...")
    
    try:
        # 测试向后兼容的函数
        from infrastructure.utils import (
            extract_company_name, is_complete_company_name,
            extract_city_from_address, city_brain_logger
        )
        
        # 测试企业名称提取
        result = extract_company_name("青岛啤酒股份有限公司")
        if result:
            print(f"  ✅ 企业名称提取兼容: {result.get('name')}")
        
        # 测试企业名称完整性检查
        is_complete = is_complete_company_name("青岛啤酒股份有限公司")
        print(f"  ✅ 企业名称完整性检查兼容: {is_complete}")
        
        # 测试城市提取
        city = extract_city_from_address("山东省青岛市市南区")
        if city:
            print(f"  ✅ 城市提取兼容: {city}")
        
        # 测试日志记录
        city_brain_logger.log_company_query("测试", "兼容性测试", "成功")
        print("  ✅ 日志记录兼容")
        
        return True
    except Exception as e:
        print(f"  ❌ 向后兼容性测试失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 开始基础设施测试...")
    print("=" * 50)
    
    test_results = []
    
    # 执行各项测试
    test_results.append(("模块导入", test_module_imports()))
    test_results.append(("配置模块", test_config_modules()))
    test_results.append(("数据库模型", test_database_models()))
    test_results.append(("数据库仓储", test_database_repositories()))
    test_results.append(("工具模块", test_utils_modules()))
    test_results.append(("向后兼容性", test_backward_compatibility()))
    
    # 统计结果
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 总体结果: {passed}/{total} 通过 ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 所有测试通过！基础设施重构成功！")
        return True
    else:
        print("⚠️ 部分测试失败，需要修复问题")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)