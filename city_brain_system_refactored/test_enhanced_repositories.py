#!/usr/bin/env python3
"""
完全独立的增强版仓储层测试脚本
避免相对导入问题，直接测试仓储功能
"""
import sys
import os
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_enhanced_customer_repository():
    """测试增强版客户仓储类"""
    try:
        # 直接导入增强版客户仓储
        import importlib.util
        
        # 加载增强版客户仓储模块
        spec = importlib.util.spec_from_file_location(
            "enhanced_customer_repository", 
            "infrastructure/database/repositories/enhanced_customer_repository.py"
        )
        module = importlib.util.module_from_spec(spec)
        
        # 模拟依赖
        sys.modules['infrastructure.database.repositories.base_repository'] = type('MockModule', (), {
            'BaseRepository': type('BaseRepository', (), {
                '__init__': lambda self, connection_manager=None: None,
                '_execute_single_query': lambda self, query, params=None: None,
                '_execute_query': lambda self, query, params=None: [],
                '_execute_update': lambda self, query, params=None: True,
            })
        })()
        
        sys.modules['infrastructure.database.models.customer'] = type('MockModule', (), {
            'Customer': type('Customer', (), {
                '__init__': lambda self, **kwargs: setattr(self, '__dict__', kwargs),
                'to_dict': lambda self: self.__dict__,
            })
        })()
        
        sys.modules['infrastructure.database.models.area'] = type('MockModule', (), {
            'Area': type('Area', (), {})
        })()
        
        sys.modules['infrastructure.database.models.industry'] = type('MockModule', (), {
            'Industry': type('Industry', (), {})
        })()
        
        sys.modules['infrastructure.database.models.enterprise'] = type('MockModule', (), {
            'IndustryBrain': type('IndustryBrain', (), {})
        })()
        
        # 执行模块
        spec.loader.exec_module(module)
        
        # 测试类创建
        EnhancedCustomerRepository = module.EnhancedCustomerRepository
        repo = EnhancedCustomerRepository()
        
        # 测试方法存在
        expected_methods = [
            'find_by_name', 'find_by_id', 'find_by_industry', 
            'find_by_area', 'search_by_keyword', 'create', 
            'update', 'update_address', 'get_statistics'
        ]
        
        for method_name in expected_methods:
            if not hasattr(repo, method_name):
                logger.error(f"❌ 增强版客户仓储缺少方法: {method_name}")
                return False
        
        logger.info("✅ 增强版客户仓储类测试通过")
        return True
        
    except Exception as e:
        logger.error(f"❌ 增强版客户仓储测试失败: {e}")
        return False

def test_enhanced_enterprise_repository():
    """测试增强版企业仓储类"""
    try:
        import importlib.util
        
        # 加载增强版企业仓储模块
        spec = importlib.util.spec_from_file_location(
            "enhanced_enterprise_repository", 
            "infrastructure/database/repositories/enhanced_enterprise_repository.py"
        )
        module = importlib.util.module_from_spec(spec)
        
        # 模拟依赖
        sys.modules['infrastructure.database.repositories.base_repository'] = type('MockModule', (), {
            'BaseRepository': type('BaseRepository', (), {
                '__init__': lambda self, connection_manager=None: None,
                '_execute_single_query': lambda self, query, params=None: None,
                '_execute_query': lambda self, query, params=None: [],
                '_execute_update': lambda self, query, params=None: True,
            })
        })()
        
        sys.modules['infrastructure.database.models.enterprise'] = type('MockModule', (), {
            'Enterprise': type('Enterprise', (), {
                '__init__': lambda self, **kwargs: setattr(self, '__dict__', kwargs),
            }),
            'IndustryBrain': type('IndustryBrain', (), {
                '__init__': lambda self, **kwargs: setattr(self, '__dict__', kwargs),
            })
        })()
        
        # 执行模块
        spec.loader.exec_module(module)
        
        # 测试类创建
        EnhancedEnterpriseRepository = module.EnhancedEnterpriseRepository
        IndustryBrainRepository = module.IndustryBrainRepository
        
        enterprise_repo = EnhancedEnterpriseRepository()
        brain_repo = IndustryBrainRepository()
        
        # 测试企业仓储方法
        enterprise_methods = ['find_by_name', 'find_by_id', 'find_by_industry', 'find_by_area', 'search_by_keyword']
        for method_name in enterprise_methods:
            if not hasattr(enterprise_repo, method_name):
                logger.error(f"❌ 增强版企业仓储缺少方法: {method_name}")
                return False
        
        # 测试产业大脑仓储方法
        brain_methods = ['find_by_id', 'find_by_name', 'find_by_area', 'get_all']
        for method_name in brain_methods:
            if not hasattr(brain_repo, method_name):
                logger.error(f"❌ 产业大脑仓储缺少方法: {method_name}")
                return False
        
        logger.info("✅ 增强版企业仓储和产业大脑仓储测试通过")
        return True
        
    except Exception as e:
        logger.error(f"❌ 增强版企业仓储测试失败: {e}")
        return False

def test_area_repository():
    """测试地区仓储类"""
    try:
        import importlib.util
        
        # 加载地区仓储模块
        spec = importlib.util.spec_from_file_location(
            "area_repository", 
            "infrastructure/database/repositories/area_repository.py"
        )
        module = importlib.util.module_from_spec(spec)
        
        # 模拟依赖
        sys.modules['infrastructure.database.repositories.base_repository'] = type('MockModule', (), {
            'BaseRepository': type('BaseRepository', (), {
                '__init__': lambda self, connection_manager=None: None,
                '_execute_single_query': lambda self, query, params=None: None,
                '_execute_query': lambda self, query, params=None: [],
                '_execute_update': lambda self, query, params=None: True,
            })
        })()
        
        sys.modules['infrastructure.database.models.area'] = type('MockModule', (), {
            'Area': type('Area', (), {
                '__init__': lambda self, **kwargs: setattr(self, '__dict__', kwargs),
            })
        })()
        
        # 执行模块
        spec.loader.exec_module(module)
        
        # 测试类创建
        AreaRepository = module.AreaRepository
        repo = AreaRepository()
        
        # 测试方法存在
        expected_methods = [
            'find_by_id', 'find_by_name', 'find_by_city', 
            'search_by_keyword', 'get_all_cities', 'get_all', 
            'create', 'update', 'get_statistics'
        ]
        
        for method_name in expected_methods:
            if not hasattr(repo, method_name):
                logger.error(f"❌ 地区仓储缺少方法: {method_name}")
                return False
        
        logger.info("✅ 地区仓储类测试通过")
        return True
        
    except Exception as e:
        logger.error(f"❌ 地区仓储测试失败: {e}")
        return False

def test_enhanced_industry_repository():
    """测试增强版行业仓储类"""
    try:
        import importlib.util
        
        # 加载增强版行业仓储模块
        spec = importlib.util.spec_from_file_location(
            "enhanced_industry_repository", 
            "infrastructure/database/repositories/enhanced_industry_repository.py"
        )
        module = importlib.util.module_from_spec(spec)
        
        # 模拟依赖
        sys.modules['infrastructure.database.repositories.base_repository'] = type('MockModule', (), {
            'BaseRepository': type('BaseRepository', (), {
                '__init__': lambda self, connection_manager=None: None,
                '_execute_single_query': lambda self, query, params=None: None,
                '_execute_query': lambda self, query, params=None: [],
                '_execute_update': lambda self, query, params=None: True,
            })
        })()
        
        sys.modules['infrastructure.database.models.industry'] = type('MockModule', (), {
            'Industry': type('Industry', (), {
                '__init__': lambda self, **kwargs: setattr(self, '__dict__', kwargs),
            })
        })()
        
        # 执行模块
        spec.loader.exec_module(module)
        
        # 测试类创建
        EnhancedIndustryRepository = module.EnhancedIndustryRepository
        repo = EnhancedIndustryRepository()
        
        # 测试方法存在
        expected_methods = [
            'find_by_id', 'find_by_name', 'find_by_type', 
            'search_by_keyword', 'get_all_types', 'get_all',
            'create', 'update', 'get_related_customers_count',
            'get_related_enterprises_count', 'get_related_brains', 'get_statistics'
        ]
        
        for method_name in expected_methods:
            if not hasattr(repo, method_name):
                logger.error(f"❌ 增强版行业仓储缺少方法: {method_name}")
                return False
        
        logger.info("✅ 增强版行业仓储类测试通过")
        return True
        
    except Exception as e:
        logger.error(f"❌ 增强版行业仓储测试失败: {e}")
        return False

def test_repository_file_structure():
    """测试仓储文件结构"""
    try:
        expected_files = [
            'infrastructure/database/repositories/enhanced_customer_repository.py',
            'infrastructure/database/repositories/enhanced_enterprise_repository.py',
            'infrastructure/database/repositories/enhanced_industry_repository.py',
            'infrastructure/database/repositories/area_repository.py',
            'infrastructure/database/repositories/__init__.py'
        ]
        
        for file_path in expected_files:
            if not os.path.exists(file_path):
                logger.error(f"❌ 缺少仓储文件: {file_path}")
                return False
        
        logger.info("✅ 仓储文件结构完整")
        return True
        
    except Exception as e:
        logger.error(f"❌ 仓储文件结构测试失败: {e}")
        return False

def main():
    """主测试函数"""
    logger.info("开始增强版仓储层独立测试...")
    
    tests = [
        ("仓储文件结构", test_repository_file_structure),
        ("增强版客户仓储", test_enhanced_customer_repository),
        ("增强版企业仓储", test_enhanced_enterprise_repository),
        ("地区仓储", test_area_repository),
        ("增强版行业仓储", test_enhanced_industry_repository),
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
    logger.info(f"增强版仓储层独立测试完成")
    logger.info(f"通过率: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate == 100:
        logger.info("✅ 增强版仓储层测试通过！任务2.2完成")
        return True
    else:
        logger.warning("⚠️  部分测试未通过，需要修复后再继续")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)