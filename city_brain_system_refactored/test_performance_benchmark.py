"""
Phase 6.2: 性能基准测试
评估系统响应时间、并发能力和资源使用情况
"""

import os
import sys
import time
import asyncio
import threading
import json
import statistics
from datetime import datetime
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed
import psutil

# 添加项目根目录到路径
sys.path.append(os.path.dirname(__file__))

from config.simple_settings import load_settings
from infrastructure.database.connection import get_database_connection
from infrastructure.database.standalone_queries import (
    get_customers, get_enterprises, get_industries,
    search_customers
)
from domain.services.enterprise_service import EnterpriseService
from api.v1.dependencies import ServiceContainer


class PerformanceBenchmark:
    """性能基准测试器"""
    
    def __init__(self):
        self.settings = load_settings()
        self.results = {}
        self.start_time = time.time()
        
    def log_result(self, test_name: str, metrics: Dict[str, Any]):
        """记录测试结果"""
        self.results[test_name] = {
            **metrics,
            "timestamp": datetime.now().isoformat()
        }
        print(f"📊 {test_name}: {metrics}")
    
    def measure_response_time(self, func, *args, **kwargs):
        """测量函数响应时间"""
        start = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start
            return {"success": True, "duration": duration, "result": result}
        except Exception as e:
            duration = time.time() - start
            return {"success": False, "duration": duration, "error": str(e)}
    
    def test_database_performance(self):
        """测试数据库性能"""
        print("🔍 测试数据库性能...")
        
        # 测试单次查询性能
        single_query_times = []
        for i in range(10):
            result = self.measure_response_time(get_all_customers)
            if result["success"]:
                single_query_times.append(result["duration"])
        
        # 测试批量查询性能
        batch_query_times = []
        for i in range(5):
            start = time.time()
            try:
                customers = get_all_customers()
                enterprises = get_all_enterprises()
                industries = get_all_industries()
                duration = time.time() - start
                batch_query_times.append(duration)
            except Exception as e:
                print(f"批量查询失败: {e}")
        
        # 测试搜索性能
        search_times = []
        test_keywords = ["海尔", "华为", "腾讯", "阿里", "百度"]
        for keyword in test_keywords:
            result = self.measure_response_time(search_customers_by_name, keyword)
            if result["success"]:
                search_times.append(result["duration"])
        
        metrics = {
            "single_query": {
                "avg_time": statistics.mean(single_query_times) if single_query_times else 0,
                "min_time": min(single_query_times) if single_query_times else 0,
                "max_time": max(single_query_times) if single_query_times else 0,
                "success_rate": len(single_query_times) / 10 * 100
            },
            "batch_query": {
                "avg_time": statistics.mean(batch_query_times) if batch_query_times else 0,
                "min_time": min(batch_query_times) if batch_query_times else 0,
                "max_time": max(batch_query_times) if batch_query_times else 0,
                "success_rate": len(batch_query_times) / 5 * 100
            },
            "search_query": {
                "avg_time": statistics.mean(search_times) if search_times else 0,
                "min_time": min(search_times) if search_times else 0,
                "max_time": max(search_times) if search_times else 0,
                "success_rate": len(search_times) / len(test_keywords) * 100
            }
        }
        
        self.log_result("数据库性能", metrics)
        return metrics
    
    def test_business_service_performance(self):
        """测试业务服务性能"""
        print("🧠 测试业务服务性能...")
        
        enterprise_service = EnterpriseService()
        
        # 测试企业名称提取性能
        extraction_times = []
        test_inputs = [
            "查询海尔集团的信息",
            "华为技术有限公司怎么样",
            "腾讯控股的详细资料",
            "阿里巴巴集团的业务范围",
            "百度公司的发展历程"
        ]
        
        for input_text in test_inputs:
            result = self.measure_response_time(
                enterprise_service.search_service.extract_company_name_from_input,
                input_text
            )
            if result["success"]:
                extraction_times.append(result["duration"])
        
        # 测试本地数据库搜索性能
        local_search_times = []
        test_companies = ["海尔集团", "华为", "腾讯", "阿里巴巴", "百度"]
        
        for company in test_companies:
            result = self.measure_response_time(
                enterprise_service.search_local_database,
                company
            )
            if result["success"]:
                local_search_times.append(result["duration"])
        
        metrics = {
            "name_extraction": {
                "avg_time": statistics.mean(extraction_times) if extraction_times else 0,
                "min_time": min(extraction_times) if extraction_times else 0,
                "max_time": max(extraction_times) if extraction_times else 0,
                "success_rate": len(extraction_times) / len(test_inputs) * 100
            },
            "local_search": {
                "avg_time": statistics.mean(local_search_times) if local_search_times else 0,
                "min_time": min(local_search_times) if local_search_times else 0,
                "max_time": max(local_search_times) if local_search_times else 0,
                "success_rate": len(local_search_times) / len(test_companies) * 100
            }
        }
        
        self.log_result("业务服务性能", metrics)
        return metrics
    
    def test_concurrent_performance(self):
        """测试并发性能"""
        print("⚡ 测试并发性能...")
        
        def worker_task(task_id):
            """工作线程任务"""
            start = time.time()
            try:
                # 模拟并发查询
                customers = get_all_customers()
                enterprises = get_all_enterprises()
                
                # 模拟业务处理
                enterprise_service = EnterpriseService()
                result = enterprise_service.search_service.extract_company_name_from_input(
                    f"查询任务{task_id}的企业信息"
                )
                
                duration = time.time() - start
                return {"task_id": task_id, "success": True, "duration": duration}
            except Exception as e:
                duration = time.time() - start
                return {"task_id": task_id, "success": False, "duration": duration, "error": str(e)}
        
        # 测试不同并发级别
        concurrency_levels = [1, 5, 10, 20]
        concurrent_results = {}
        
        for level in concurrency_levels:
            print(f"  测试并发级别: {level}")
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=level) as executor:
                futures = [executor.submit(worker_task, i) for i in range(level)]
                results = [future.result() for future in as_completed(futures)]
            
            total_time = time.time() - start_time
            successful_tasks = [r for r in results if r["success"]]
            failed_tasks = [r for r in results if not r["success"]]
            
            if successful_tasks:
                task_times = [r["duration"] for r in successful_tasks]
                concurrent_results[f"level_{level}"] = {
                    "total_time": total_time,
                    "avg_task_time": statistics.mean(task_times),
                    "min_task_time": min(task_times),
                    "max_task_time": max(task_times),
                    "success_rate": len(successful_tasks) / level * 100,
                    "throughput": level / total_time,  # 任务/秒
                    "failed_count": len(failed_tasks)
                }
            else:
                concurrent_results[f"level_{level}"] = {
                    "total_time": total_time,
                    "success_rate": 0,
                    "failed_count": len(failed_tasks),
                    "error": "所有任务都失败了"
                }
        
        self.log_result("并发性能", concurrent_results)
        return concurrent_results
    
    def test_memory_usage(self):
        """测试内存使用情况"""
        print("💾 测试内存使用情况...")
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 执行一系列操作并监控内存
        memory_samples = [initial_memory]
        
        # 大量数据查询
        for i in range(10):
            customers = get_all_customers()
            enterprises = get_all_enterprises()
            current_memory = process.memory_info().rss / 1024 / 1024
            memory_samples.append(current_memory)
            time.sleep(0.1)
        
        # 业务服务操作
        enterprise_service = EnterpriseService()
        for i in range(5):
            result = enterprise_service.search_service.extract_company_name_from_input(
                f"测试内存使用情况 {i}"
            )
            current_memory = process.memory_info().rss / 1024 / 1024
            memory_samples.append(current_memory)
            time.sleep(0.1)
        
        final_memory = process.memory_info().rss / 1024 / 1024
        
        metrics = {
            "initial_memory_mb": initial_memory,
            "final_memory_mb": final_memory,
            "peak_memory_mb": max(memory_samples),
            "memory_increase_mb": final_memory - initial_memory,
            "avg_memory_mb": statistics.mean(memory_samples),
            "memory_samples": len(memory_samples)
        }
        
        self.log_result("内存使用", metrics)
        return metrics
    
    def test_system_resources(self):
        """测试系统资源使用"""
        print("🖥️ 测试系统资源使用...")
        
        # CPU使用率
        cpu_percent_before = psutil.cpu_percent(interval=1)
        
        # 执行一些CPU密集型操作
        start_time = time.time()
        for i in range(100):
            customers = get_all_customers()
            # 模拟一些计算
            _ = sum(range(1000))
        
        cpu_percent_after = psutil.cpu_percent(interval=1)
        execution_time = time.time() - start_time
        
        # 内存信息
        memory = psutil.virtual_memory()
        
        # 磁盘信息
        disk = psutil.disk_usage('/')
        
        metrics = {
            "cpu_usage": {
                "before_percent": cpu_percent_before,
                "after_percent": cpu_percent_after,
                "increase_percent": cpu_percent_after - cpu_percent_before
            },
            "memory": {
                "total_gb": memory.total / 1024 / 1024 / 1024,
                "available_gb": memory.available / 1024 / 1024 / 1024,
                "used_percent": memory.percent
            },
            "disk": {
                "total_gb": disk.total / 1024 / 1024 / 1024,
                "free_gb": disk.free / 1024 / 1024 / 1024,
                "used_percent": (disk.used / disk.total) * 100
            },
            "execution_time": execution_time
        }
        
        self.log_result("系统资源", metrics)
        return metrics
    
    def generate_performance_report(self):
        """生成性能报告"""
        total_time = time.time() - self.start_time
        
        # 计算综合评分
        scores = {}
        
        # 数据库性能评分 (基于平均响应时间)
        if "数据库性能" in self.results:
            db_perf = self.results["数据库性能"]
            avg_time = db_perf.get("single_query", {}).get("avg_time", 1)
            # 响应时间越短分数越高 (满分100，0.1秒以下为满分)
            db_score = max(0, min(100, (0.1 - avg_time) / 0.1 * 100))
            scores["数据库性能"] = db_score
        
        # 业务服务性能评分
        if "业务服务性能" in self.results:
            service_perf = self.results["业务服务性能"]
            avg_time = service_perf.get("name_extraction", {}).get("avg_time", 1)
            service_score = max(0, min(100, (0.5 - avg_time) / 0.5 * 100))
            scores["业务服务性能"] = service_score
        
        # 并发性能评分
        if "并发性能" in self.results:
            concurrent_perf = self.results["并发性能"]
            # 基于最高并发级别的成功率
            max_level_key = max([k for k in concurrent_perf.keys() if k.startswith("level_")])
            success_rate = concurrent_perf[max_level_key].get("success_rate", 0)
            concurrent_score = success_rate
            scores["并发性能"] = concurrent_score
        
        # 综合评分
        overall_score = statistics.mean(scores.values()) if scores else 0
        
        report = {
            "performance_test": {
                "timestamp": datetime.now().isoformat(),
                "total_duration": f"{total_time:.3f}s",
                "overall_score": f"{overall_score:.1f}/100"
            },
            "scores": scores,
            "detailed_results": self.results,
            "recommendations": self.generate_recommendations()
        }
        
        return report
    
    def generate_recommendations(self):
        """生成性能优化建议"""
        recommendations = []
        
        # 数据库性能建议
        if "数据库性能" in self.results:
            db_perf = self.results["数据库性能"]
            avg_time = db_perf.get("single_query", {}).get("avg_time", 0)
            if avg_time > 0.5:
                recommendations.append("数据库查询响应时间较慢，建议添加索引或优化查询语句")
            if db_perf.get("single_query", {}).get("success_rate", 100) < 95:
                recommendations.append("数据库查询成功率较低，建议检查连接池配置")
        
        # 并发性能建议
        if "并发性能" in self.results:
            concurrent_perf = self.results["并发性能"]
            for level_key, metrics in concurrent_perf.items():
                if isinstance(metrics, dict) and metrics.get("success_rate", 100) < 90:
                    recommendations.append(f"高并发场景下成功率较低，建议优化资源管理和错误处理")
                    break
        
        # 内存使用建议
        if "内存使用" in self.results:
            memory_metrics = self.results["内存使用"]
            memory_increase = memory_metrics.get("memory_increase_mb", 0)
            if memory_increase > 100:
                recommendations.append("内存使用增长较大，建议检查是否存在内存泄漏")
        
        if not recommendations:
            recommendations.append("系统性能表现良好，无需特别优化")
        
        return recommendations
    
    def run_all_benchmarks(self):
        """运行所有性能测试"""
        print("🚀 开始性能基准测试...")
        print("=" * 60)
        
        try:
            # 运行各项测试
            self.test_database_performance()
            self.test_business_service_performance()
            self.test_concurrent_performance()
            self.test_memory_usage()
            self.test_system_resources()
            
            # 生成报告
            report = self.generate_performance_report()
            
            # 保存报告
            report_file = f"logs/performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.makedirs("logs", exist_ok=True)
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            print("=" * 60)
            print("📊 性能测试结果汇总:")
            print(f"   总耗时: {report['performance_test']['total_duration']}")
            print(f"   综合评分: {report['performance_test']['overall_score']}")
            print()
            print("📈 各项性能评分:")
            for metric, score in report['scores'].items():
                print(f"   {metric}: {score:.1f}/100")
            print()
            print("💡 优化建议:")
            for i, rec in enumerate(report['recommendations'], 1):
                print(f"   {i}. {rec}")
            print()
            print(f"📄 详细报告已保存: {report_file}")
            
            return report
            
        except Exception as e:
            print(f"❌ 性能测试异常: {str(e)}")
            return None


def main():
    """主函数"""
    print("📊 Phase 6.2: 性能基准测试")
    print("评估系统响应时间、并发能力和资源使用情况")
    print()
    
    benchmark = PerformanceBenchmark()
    report = benchmark.run_all_benchmarks()
    
    if report:
        overall_score = float(report['performance_test']['overall_score'].split('/')[0])
        if overall_score >= 80:
            print("\n🎉 系统性能表现优秀！")
            return 0
        elif overall_score >= 60:
            print("\n✅ 系统性能表现良好，有优化空间。")
            return 0
        else:
            print("\n⚠️ 系统性能需要优化，请参考建议进行改进。")
            return 1
    else:
        print("\n❌ 性能测试失败，请检查系统配置。")
        return 1


if __name__ == "__main__":
    exit(main())