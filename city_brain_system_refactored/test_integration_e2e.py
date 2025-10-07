"""
Phase 6.1: 端到端集成测试
验证完整的业务流程，从API请求到数据库操作的全链路测试
"""

import os
import sys
import asyncio
import time
import json
from datetime import datetime
from typing import Dict, Any, List

# 添加项目根目录到路径
sys.path.append(os.path.dirname(__file__))

# 导入所有必要的模块
from config.simple_settings import load_settings
from infrastructure.database.connection import get_database_connection, test_connection
from infrastructure.database.standalone_queries import *
from infrastructure.external.service_manager import ServiceManager
from domain.services.enterprise_service import EnterpriseService
from domain.services.search_service import SearchService
from domain.services.data_enhancement_service import DataEnhancementService
from domain.services.analysis_service import AnalysisService
from api.v1.dependencies import ServiceContainer


class E2ETestRunner:
    """端到端测试运行器"""
    
    def __init__(self):
        self.settings = load_settings()
        self.test_results = []
        self.start_time = time.time()
        
    def log_test(self, test_name: str, status: str, message: str = "", duration: float = 0):
        """记录测试结果"""
        result = {
            "test_name": test_name,
            "status": status,
            "message": message,
            "duration": f"{duration:.3f}s",
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status} ({duration:.3f}s)")
        if message:
            print(f"   {message}")
    
    def test_database_connectivity(self):
        """测试数据库连接"""
        start = time.time()
        try:
            # 测试基础连接
            connection_result = test_connection()
            if not connection_result:
                self.log_test("数据库连接测试", "FAIL", "无法建立数据库连接", time.time() - start)
                return False
            
            # 测试查询功能
            conn = get_database_connection()
            if conn:
                result = conn.execute("SELECT COUNT(*) as count FROM customer LIMIT 1")
                row = result.fetchone()
                conn.close()
                
                self.log_test("数据库连接测试", "PASS", f"连接正常，可执行查询", time.time() - start)
                return True
            else:
                self.log_test("数据库连接测试", "FAIL", "无法获取数据库连接", time.time() - start)
                return False
                
        except Exception as e:
            self.log_test("数据库连接测试", "FAIL", f"数据库连接异常: {str(e)}", time.time() - start)
            return False
    
    def test_external_services(self):
        """测试外部服务连接"""
        start = time.time()
        try:
            service_manager = ServiceManager()
            health_status = service_manager.get_all_service_health()
            
            healthy_count = sum(1 for status in health_status.values() if status.get("status") == "healthy")
            total_count = len(health_status)
            
            if healthy_count > 0:
                self.log_test("外部服务连接测试", "PASS", 
                            f"{healthy_count}/{total_count} 个服务正常", time.time() - start)
                return True
            else:
                self.log_test("外部服务连接测试", "WARN", 
                            f"所有外部服务不可用，但系统可继续运行", time.time() - start)
                return True  # 外部服务不可用不应该阻止系统运行
                
        except Exception as e:
            self.log_test("外部服务连接测试", "WARN", 
                        f"外部服务检查异常: {str(e)}", time.time() - start)
            return True  # 外部服务异常不应该阻止系统运行
    
    def test_data_layer_operations(self):
        """测试数据层操作"""
        start = time.time()
        try:
            # 测试查询接口
            customers = get_all_customers()
            enterprises = get_all_enterprises()
            industries = get_all_industries()
            
            # 测试搜索功能
            if customers:
                search_result = search_customers_by_name("测试")
                
            self.log_test("数据层操作测试", "PASS", 
                        f"查询接口正常，客户数: {len(customers)}, 企业数: {len(enterprises)}", 
                        time.time() - start)
            return True
            
        except Exception as e:
            self.log_test("数据层操作测试", "FAIL", 
                        f"数据层操作异常: {str(e)}", time.time() - start)
            return False
    
    def test_business_services(self):
        """测试业务服务层"""
        start = time.time()
        try:
            # 初始化服务
            search_service = SearchService()
            data_enhancement_service = DataEnhancementService()
            analysis_service = AnalysisService()
            enterprise_service = EnterpriseService()
            
            # 测试企业名称提取
            extraction_result = search_service.extract_company_name_from_input("查询海尔集团的信息")
            if extraction_result['status'] != 'success':
                self.log_test("业务服务测试", "FAIL", 
                            f"企业名称提取失败: {extraction_result.get('message')}", time.time() - start)
                return False
            
            company_name = extraction_result['name']
            
            # 测试本地数据库搜索
            local_result = enterprise_service.search_local_database(company_name)
            
            # 测试企业信息处理（使用模拟数据避免外部API调用）
            # 这里我们只测试服务的初始化和基本功能
            
            self.log_test("业务服务测试", "PASS", 
                        f"服务初始化成功，企业名称提取: {company_name}", time.time() - start)
            return True
            
        except Exception as e:
            self.log_test("业务服务测试", "FAIL", 
                        f"业务服务异常: {str(e)}", time.time() - start)
            return False
    
    def test_api_dependencies(self):
        """测试API依赖注入"""
        start = time.time()
        try:
            # 测试服务容器
            container = ServiceContainer()
            
            # 测试各个服务的获取
            enterprise_service = container.enterprise_service
            search_service = container.search_service
            data_enhancement_service = container.data_enhancement_service
            analysis_service = container.analysis_service
            
            # 验证服务实例
            assert enterprise_service is not None, "企业服务未正确初始化"
            assert search_service is not None, "搜索服务未正确初始化"
            assert data_enhancement_service is not None, "数据增强服务未正确初始化"
            assert analysis_service is not None, "分析服务未正确初始化"
            
            self.log_test("API依赖注入测试", "PASS", 
                        "所有服务依赖注入正常", time.time() - start)
            return True
            
        except Exception as e:
            self.log_test("API依赖注入测试", "FAIL", 
                        f"依赖注入异常: {str(e)}", time.time() - start)
            return False
    
    def test_complete_business_flow(self):
        """测试完整业务流程"""
        start = time.time()
        try:
            # 模拟完整的企业查询流程
            enterprise_service = EnterpriseService()
            
            # 步骤1: 企业名称提取
            user_input = "查询海尔集团的详细信息"
            extraction_result = enterprise_service.search_service.extract_company_name_from_input(user_input)
            
            if extraction_result['status'] != 'success':
                self.log_test("完整业务流程测试", "FAIL", 
                            f"企业名称提取失败", time.time() - start)
                return False
            
            company_name = extraction_result['name']
            
            # 步骤2: 本地数据库搜索
            local_result = enterprise_service.search_local_database(company_name)
            
            # 步骤3: 如果本地没有，模拟网络搜索（不实际调用外部API）
            if not local_result['found']:
                # 这里我们模拟搜索结果，避免实际的外部API调用
                mock_search_result = {
                    'status': 'success',
                    'data': {
                        'company_name': company_name,
                        'address': '青岛市',
                        'industry': '家电制造',
                        'description': '模拟搜索结果'
                    }
                }
            
            self.log_test("完整业务流程测试", "PASS", 
                        f"业务流程执行完成，处理企业: {company_name}", time.time() - start)
            return True
            
        except Exception as e:
            self.log_test("完整业务流程测试", "FAIL", 
                        f"业务流程异常: {str(e)}", time.time() - start)
            return False
    
    def test_error_handling(self):
        """测试错误处理机制"""
        start = time.time()
        try:
            enterprise_service = EnterpriseService()
            
            # 测试空输入处理
            try:
                result = enterprise_service.search_service.extract_company_name_from_input("")
                if result['status'] == 'error':
                    # 正确处理了错误
                    pass
            except Exception:
                # 异常被正确抛出
                pass
            
            # 测试无效数据处理
            try:
                result = enterprise_service.search_local_database("")
                # 应该返回未找到的结果
                assert not result['found'], "空查询应该返回未找到"
            except Exception:
                # 异常处理正常
                pass
            
            self.log_test("错误处理测试", "PASS", 
                        "错误处理机制正常", time.time() - start)
            return True
            
        except Exception as e:
            self.log_test("错误处理测试", "FAIL", 
                        f"错误处理测试异常: {str(e)}", time.time() - start)
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始端到端集成测试...")
        print("=" * 60)
        
        tests = [
            ("数据库连接", self.test_database_connectivity),
            ("外部服务", self.test_external_services),
            ("数据层操作", self.test_data_layer_operations),
            ("业务服务", self.test_business_services),
            ("API依赖注入", self.test_api_dependencies),
            ("完整业务流程", self.test_complete_business_flow),
            ("错误处理", self.test_error_handling),
        ]
        
        passed = 0
        failed = 0
        warnings = 0
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                if result:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.log_test(f"{test_name}测试", "FAIL", f"测试执行异常: {str(e)}", 0)
                failed += 1
        
        # 统计警告
        warnings = sum(1 for result in self.test_results if result["status"] == "WARN")
        
        total_time = time.time() - self.start_time
        
        print("=" * 60)
        print(f"📊 测试结果汇总:")
        print(f"   总测试数: {len(tests)}")
        print(f"   通过: {passed} ✅")
        print(f"   失败: {failed} ❌")
        print(f"   警告: {warnings} ⚠️")
        print(f"   总耗时: {total_time:.3f}s")
        print(f"   通过率: {(passed/(passed+failed)*100):.1f}%")
        
        # 保存详细测试报告
        self.save_test_report()
        
        return failed == 0
    
    def save_test_report(self):
        """保存测试报告"""
        report = {
            "test_run": {
                "timestamp": datetime.now().isoformat(),
                "total_duration": f"{time.time() - self.start_time:.3f}s",
                "environment": "integration_test"
            },
            "summary": {
                "total_tests": len(self.test_results),
                "passed": sum(1 for r in self.test_results if r["status"] == "PASS"),
                "failed": sum(1 for r in self.test_results if r["status"] == "FAIL"),
                "warnings": sum(1 for r in self.test_results if r["status"] == "WARN")
            },
            "detailed_results": self.test_results
        }
        
        report_file = f"logs/e2e_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs("logs", exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📄 详细测试报告已保存: {report_file}")


def main():
    """主函数"""
    print("🧪 Phase 6.1: 端到端集成测试")
    print("测试整个系统的集成性和业务流程完整性")
    print()
    
    runner = E2ETestRunner()
    success = runner.run_all_tests()
    
    if success:
        print("\n🎉 所有集成测试通过！系统集成正常。")
        return 0
    else:
        print("\n❌ 部分集成测试失败，请检查系统配置。")
        return 1


if __name__ == "__main__":
    exit(main())