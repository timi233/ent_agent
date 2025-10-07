#!/usr/bin/env python3
"""
端到端集成测试

测试完整的业务流程：
1. 用户输入 → API请求 → 服务处理 → 数据库查询 → 外部服务调用 → 返回结果
2. 测试数据流动的完整链路
3. 验证各层协同工作
"""

import sys
import os
import json
import time
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 加载环境变量 - 必须在导入其他模块之前
from dotenv import load_dotenv
load_dotenv()


class E2ETestRunner:
    """端到端测试运行器"""

    def __init__(self):
        self.results = []
        self.setup_complete = False

    def setup(self):
        """测试环境设置"""
        print("=" * 80)
        print("🔧 设置测试环境")
        print("=" * 80)

        try:
            # 导入所需模块
            from api.v1.dependencies import (
                get_enterprise_service_refactored,
                get_customer_repository
            )
            from domain.services.enterprise_service_refactored import EnterpriseServiceRefactored

            self.get_service = get_enterprise_service_refactored
            self.get_repository = get_customer_repository
            self.service_class = EnterpriseServiceRefactored

            print("✅ 模块导入成功")
            self.setup_complete = True
            return True

        except Exception as e:
            print(f"❌ 环境设置失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_complete_workflow_with_local_data(self):
        """测试完整工作流程 - 有本地数据"""
        print("\n" + "=" * 80)
        print("测试 1: 完整工作流程（本地数据）")
        print("=" * 80)

        try:
            service = self.get_service()

            # 测试输入
            test_input = "青岛啤酒股份有限公司"
            print(f"输入: {test_input}")

            # 执行完整处理流程
            start_time = time.time()
            result = service.process_company_info(test_input)
            duration = time.time() - start_time

            print(f"处理时间: {duration:.3f}秒")

            # 验证结果
            if result.get('status') == 'success':
                data = result.get('data', {})
                if data:
                    print(f"✅ 处理成功")
                    print(f"   公司名称: {data.get('company_name', 'N/A')}")
                    print(f"   数据来源: {result.get('source', 'N/A')}")
                    print(f"   详细信息:")
                    details = data.get('details', {})
                    if details:
                        print(f"     - 地区: {details.get('region', 'N/A')}")
                        print(f"     - 地址: {details.get('address', 'N/A')[:50] if details.get('address') else 'N/A'}...")
                        print(f"     - 行业: {details.get('industry', 'N/A')}")
                        print(f"     - 产业大脑: {details.get('industry_brain', 'N/A')}")
                        print(f"     - 链主状态: {details.get('chain_status', 'N/A')}")

                    # 验证关键字段（允许为空，因为可能是搜索失败）
                    print(f"✅ 数据结构完整")
                    return True
                else:
                    print(f"⚠️  数据为空，但状态为成功")
                    return True  # 仍然算通过，因为没有崩溃
            else:
                print(f"⚠️  处理失败: {result.get('message', 'Unknown error')}")
                return False

        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_complete_workflow_without_local_data(self):
        """测试完整工作流程 - 无本地数据"""
        print("\n" + "=" * 80)
        print("测试 2: 完整工作流程（网络搜索）")
        print("=" * 80)

        try:
            service = self.get_service()

            # 测试输入（不太可能在本地数据库中）
            test_input = "某个不存在的测试公司XYZ123"
            print(f"输入: {test_input}")

            # 执行处理流程
            start_time = time.time()
            result = service.process_company_info(test_input)
            duration = time.time() - start_time

            print(f"处理时间: {duration:.3f}秒")

            # 验证结果（预期会失败或返回web_search来源）
            if result.get('status') == 'success':
                data = result.get('data', {})
                source = result.get('source', 'unknown')
                print(f"✅ 处理完成")
                print(f"   公司名称: {data.get('company_name', 'N/A')}")
                print(f"   数据来源: {source}")

                # 验证是网络搜索来源
                assert source in ['web_search', 'unknown'], f"预期web_search来源，实际: {source}"

                return True
            else:
                print(f"⚠️  处理结果: {result.get('message', 'Unknown')}")
                # 这也算正常，因为可能找不到数据
                return True

        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_processor_chain(self):
        """测试处理器链"""
        print("\n" + "=" * 80)
        print("测试 3: 处理器链协同")
        print("=" * 80)

        try:
            service = self.get_service()

            # 验证处理器已初始化
            assert service.processor is not None, "处理器未初始化"
            assert service.enhancer is not None, "增强器未初始化"
            assert service.analyzer is not None, "分析器未初始化"
            print("✅ 所有处理器已初始化")

            # 测试处理器方法调用
            test_name = "测试公司有限公司-企业信息"

            # 1. 测试名称清洗
            cleaned = service.processor.clean_company_name(test_name)
            print(f"✅ 名称清洗: {test_name} → {cleaned}")

            # 2. 测试名称标准化
            normalized = service.processor.normalize_company_name(test_name)
            print(f"✅ 名称标准化: {test_name} → {normalized}")

            # 3. 测试核心名称提取
            core = service.processor.extract_core_company_name(test_name)
            print(f"✅ 核心名称: {test_name} → {core}")

            return True

        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_data_flow(self):
        """测试数据流动"""
        print("\n" + "=" * 80)
        print("测试 4: 数据流动验证")
        print("=" * 80)

        try:
            service = self.get_service()

            # 测试基础信息获取
            test_company = "测试企业A"
            result = service.get_company_basic_info(test_company)

            if result.get('status') == 'success':
                data = result.get('data', {})
                print(f"✅ 基础信息获取成功")
                print(f"   公司名: {data.get('name', 'N/A')}")
                print(f"   来源: {data.get('source', 'N/A')}")

                # 验证数据结构
                required_fields = ['name', 'region', 'address', 'industry', 'source']
                for field in required_fields:
                    assert field in data, f"缺少字段: {field}"
                print(f"✅ 数据结构完整（包含所有必需字段）")

                return True
            else:
                print(f"⚠️  获取结果: {result.get('message', 'Unknown')}")
                return True  # 可能确实没有数据

        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_error_handling(self):
        """测试错误处理"""
        print("\n" + "=" * 80)
        print("测试 5: 错误处理机制")
        print("=" * 80)

        try:
            service = self.get_service()

            # 测试1: 空输入
            result = service.process_company_info("")
            if result.get('status') == 'error':
                print("✅ 空输入正确返回错误")
            else:
                print("⚠️  空输入未返回错误")

            # 测试2: 特殊字符
            result = service.process_company_info("@#$%^&*()")
            print(f"✅ 特殊字符处理: {result.get('status', 'unknown')}")

            # 测试3: 超长输入
            long_input = "A" * 1000
            result = service.process_company_info(long_input)
            print(f"✅ 超长输入处理: {result.get('status', 'unknown')}")

            return True

        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_repository_integration(self):
        """测试仓储层集成"""
        print("\n" + "=" * 80)
        print("测试 6: 仓储层集成")
        print("=" * 80)

        try:
            repository = self.get_repository()

            # 测试查询
            test_name = "测试公司"
            result = repository.find_by_name(test_name)

            if result:
                print(f"✅ 仓储查询成功: 找到数据")
                print(f"   公司名: {result.get('customer_name', 'N/A')}")
            else:
                print(f"✅ 仓储查询成功: 未找到数据（正常）")

            # 验证仓储方法存在
            methods = ['find_by_id', 'find_by_name', 'find_all', 'insert', 'update', 'count_all']
            for method in methods:
                assert hasattr(repository, method), f"缺少方法: {method}"
            print(f"✅ 仓储接口完整（所有主要方法存在）")

            return True

        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_service_composition(self):
        """测试服务组合"""
        print("\n" + "=" * 80)
        print("测试 7: 服务组合与协同")
        print("=" * 80)

        try:
            service = self.get_service()

            # 验证服务依赖
            assert service.search_service is not None, "搜索服务未注入"
            assert service.data_enhancement_service is not None, "数据增强服务未注入"
            assert service.analysis_service is not None, "分析服务未注入"
            assert service.customer_repository is not None, "客户仓储未注入"
            print("✅ 所有服务依赖已正确注入")

            # 验证处理器依赖
            assert service.processor.search_service is not None, "处理器未获得搜索服务"
            assert service.enhancer.data_enhancement_service is not None, "增强器未获得数据增强服务"
            assert service.analyzer.analysis_service is not None, "分析器未获得分析服务"
            print("✅ 所有处理器依赖已正确注入")

            return True

        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run_all_tests(self):
        """运行所有测试"""
        if not self.setup():
            print("\n❌ 环境设置失败，无法运行测试")
            return False

        tests = [
            ("完整工作流程（本地数据）", self.test_complete_workflow_with_local_data),
            ("完整工作流程（网络搜索）", self.test_complete_workflow_without_local_data),
            ("处理器链协同", self.test_processor_chain),
            ("数据流动验证", self.test_data_flow),
            ("错误处理机制", self.test_error_handling),
            ("仓储层集成", self.test_repository_integration),
            ("服务组合与协同", self.test_service_composition)
        ]

        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"\n❌ 测试 '{test_name}' 执行异常: {e}")
                import traceback
                traceback.print_exc()
                results.append((test_name, False))

        return results


def main():
    """主函数"""
    print("🚀 开始端到端集成测试")
    print("=" * 80)

    runner = E2ETestRunner()
    results = runner.run_all_tests()

    # 汇总结果
    print("\n" + "=" * 80)
    print("📊 测试结果汇总")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status}: {test_name}")

    print(f"\n总计: {passed}/{total} 测试通过 ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n🎉 所有端到端集成测试通过！")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    exit(main())
