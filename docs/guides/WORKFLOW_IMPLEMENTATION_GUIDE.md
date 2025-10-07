# 工作流程实现指南

## 📋 概述

基于用户提供的细化工作流程图，本文档提供了具体的实现指南，包括代码示例、配置说明和最佳实践。

## 🔄 完整工作流程实现

### 主控制器实现
```python
# controllers/enterprise_workflow_controller.py
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
import logging

from services.enterprise_service import EnterpriseService
from services.parallel_task_orchestrator import ParallelTaskOrchestrator
from services.new_enterprise_discovery import NewEnterpriseDiscoveryService
from utils.workflow_logger import WorkflowLogger

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/workflow", tags=["企业信息工作流"])

class EnterpriseWorkflowController:
    def __init__(self):
        self.enterprise_service = EnterpriseService()
        self.orchestrator = ParallelTaskOrchestrator()
        self.discovery_service = NewEnterpriseDiscoveryService()
        self.workflow_logger = WorkflowLogger()

@router.post("/process")
async def process_enterprise_workflow(
    enterprise_name: str,
    force_refresh: bool = False
) -> Dict[str, Any]:
    """
    企业信息处理工作流程主入口
    """
    controller = EnterpriseWorkflowController()
    
    try:
        # 记录工作流开始
        workflow_id = await controller.workflow_logger.start_workflow(enterprise_name)
        
        # 执行完整工作流程
        result = await controller.execute_complete_workflow(
            enterprise_name, 
            workflow_id, 
            force_refresh
        )
        
        # 记录工作流完成
        await controller.workflow_logger.complete_workflow(workflow_id, result)
        
        return {
            "workflow_id": workflow_id,
            "status": "success",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"工作流程执行失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"工作流程执行失败: {str(e)}")

class EnterpriseWorkflowController:
    async def execute_complete_workflow(self, enterprise_name: str, 
                                      workflow_id: str, 
                                      force_refresh: bool = False) -> Dict[str, Any]:
        """
        执行完整的企业信息处理工作流程
        """
        workflow_context = {
            "workflow_id": workflow_id,
            "enterprise_name": enterprise_name,
            "start_time": datetime.now(),
            "force_refresh": force_refresh,
            "steps": []
        }
        
        try:
            # 步骤1: 在本地DB搜索企业主体记录
            search_result = await self._step1_search_local_enterprise(
                enterprise_name, workflow_context
            )
            
            if not search_result["found"]:
                # 记录未找到企业
                workflow_context["steps"].append({
                    "step": "enterprise_not_found",
                    "timestamp": datetime.now().isoformat(),
                    "message": "本地数据库中未找到企业记录"
                })
                
                # 执行【新企业发现】流程
                discovery_result = await self._execute_new_enterprise_discovery(
                    enterprise_name, workflow_context
                )
                
                return {
                    "workflow_type": "new_enterprise_discovery",
                    "enterprise_name": enterprise_name,
                    "result": discovery_result,
                    "workflow_context": workflow_context
                }
            
            # 企业存在，执行并行处理流程
            enterprise_id = search_result["enterprise_id"]
            
            # 阶段一: 并行任务分发与执行
            stage1_result = await self._execute_stage1_parallel_processing(
                enterprise_id, enterprise_name, workflow_context
            )
            
            # 阶段二: 同步等待与依赖分析
            stage2_result = await self._execute_stage2_dependency_analysis(
                stage1_result, workflow_context
            )
            
            # 阶段三: 结果汇总
            final_result = await self._execute_stage3_result_integration(
                stage1_result, stage2_result, workflow_context
            )
            
            return {
                "workflow_type": "existing_enterprise_processing",
                "enterprise_id": enterprise_id,
                "enterprise_name": enterprise_name,
                "stage1_result": stage1_result,
                "stage2_result": stage2_result,
                "final_result": final_result,
                "workflow_context": workflow_context
            }
            
        except Exception as e:
            workflow_context["error"] = str(e)
            workflow_context["status"] = "failed"
            raise

    async def _step1_search_local_enterprise(self, enterprise_name: str, 
                                           context: Dict[str, Any]) -> Dict[str, Any]:
        """
        步骤1: 在本地DB搜索企业主体记录
        """
        step_start = datetime.now()
        
        try:
            # 搜索本地企业记录
            enterprises = await self.enterprise_service.search_enterprises_by_name(
                enterprise_name, exact_match=True
            )
            
            if enterprises:
                # 找到企业记录
                enterprise = enterprises[0]  # 取第一个匹配结果
                
                step_result = {
                    "step": "search_local_enterprise",
                    "found": True,
                    "enterprise_id": enterprise["id"],
                    "enterprise_data": enterprise,
                    "execution_time": (datetime.now() - step_start).total_seconds(),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # 未找到企业记录
                step_result = {
                    "step": "search_local_enterprise",
                    "found": False,
                    "enterprise_id": None,
                    "enterprise_data": None,
                    "execution_time": (datetime.now() - step_start).total_seconds(),
                    "timestamp": datetime.now().isoformat()
                }
            
            context["steps"].append(step_result)
            return step_result
            
        except Exception as e:
            step_result = {
                "step": "search_local_enterprise",
                "found": False,
                "error": str(e),
                "execution_time": (datetime.now() - step_start).total_seconds(),
                "timestamp": datetime.now().isoformat()
            }
            context["steps"].append(step_result)
            raise

    async def _execute_new_enterprise_discovery(self, enterprise_name: str, 
                                              context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行【新企业发现】流程 - 全面联网搜索
        """
        step_start = datetime.now()
        
        try:
            # 使用新企业发现服务进行全面搜索
            discovery_result = await self.discovery_service.discover_new_enterprise(
                enterprise_name
            )
            
            step_result = {
                "step": "new_enterprise_discovery",
                "status": "completed",
                "discovery_data": discovery_result,
                "execution_time": (datetime.now() - step_start).total_seconds(),
                "timestamp": datetime.now().isoformat()
            }
            
            context["steps"].append(step_result)
            return step_result
            
        except Exception as e:
            step_result = {
                "step": "new_enterprise_discovery",
                "status": "failed",
                "error": str(e),
                "execution_time": (datetime.now() - step_start).total_seconds(),
                "timestamp": datetime.now().isoformat()
            }
            context["steps"].append(step_result)
            raise

    async def _execute_stage1_parallel_processing(self, enterprise_id: int, 
                                                enterprise_name: str,
                                                context: Dict[str, Any]) -> Dict[str, Any]:
        """
        阶段一: 并行任务分发与执行
        """
        stage_start = datetime.now()
        
        try:
            # 使用任务编排器执行6个并行泳道
            stage1_result = await self.orchestrator.execute_parallel_lanes(
                enterprise_id, enterprise_name, context.get("force_refresh", False)
            )
            
            step_result = {
                "step": "stage1_parallel_processing",
                "status": "completed",
                "lane_results": stage1_result,
                "execution_time": (datetime.now() - stage_start).total_seconds(),
                "timestamp": datetime.now().isoformat()
            }
            
            context["steps"].append(step_result)
            return stage1_result
            
        except Exception as e:
            step_result = {
                "step": "stage1_parallel_processing",
                "status": "failed",
                "error": str(e),
                "execution_time": (datetime.now() - stage_start).total_seconds(),
                "timestamp": datetime.now().isoformat()
            }
            context["steps"].append(step_result)
            raise

    async def _execute_stage2_dependency_analysis(self, stage1_result: Dict[str, Any],
                                                context: Dict[str, Any]) -> Dict[str, Any]:
        """
        阶段二: 同步等待与依赖分析
        """
        stage_start = datetime.now()
        
        try:
            # 等待泳道A和泳道B完成，获取区域信息和产业信息
            lane_a_result = stage1_result.get("lane_a")
            lane_b_result = stage1_result.get("lane_b")
            
            if (lane_a_result and lane_a_result.get("status") == "completed" and
                lane_b_result and lane_b_result.get("status") == "completed"):
                
                # 执行本地产业大脑与产业链定位分析
                ecosystem_analysis = await self.orchestrator.execute_ecosystem_positioning_analysis(
                    region_info=lane_a_result.get("data"),
                    industry_info=lane_b_result.get("data")
                )
                
                step_result = {
                    "step": "stage2_dependency_analysis",
                    "status": "completed",
                    "ecosystem_positioning": ecosystem_analysis,
                    "dependencies_met": True,
                    "execution_time": (datetime.now() - stage_start).total_seconds(),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # 依赖条件未满足
                step_result = {
                    "step": "stage2_dependency_analysis",
                    "status": "skipped",
                    "ecosystem_positioning": None,
                    "dependencies_met": False,
                    "reason": "泳道A或泳道B未成功完成",
                    "execution_time": (datetime.now() - stage_start).total_seconds(),
                    "timestamp": datetime.now().isoformat()
                }
            
            context["steps"].append(step_result)
            return step_result
            
        except Exception as e:
            step_result = {
                "step": "stage2_dependency_analysis",
                "status": "failed",
                "error": str(e),
                "execution_time": (datetime.now() - stage_start).total_seconds(),
                "timestamp": datetime.now().isoformat()
            }
            context["steps"].append(step_result)
            raise

    async def _execute_stage3_result_integration(self, stage1_result: Dict[str, Any],
                                               stage2_result: Dict[str, Any],
                                               context: Dict[str, Any]) -> Dict[str, Any]:
        """
        阶段三: 结果汇总
        """
        stage_start = datetime.now()
        
        try:
            # 等待所有泳道和阶段二分析全部完成
            all_results = {
                "lane_a": stage1_result.get("lane_a"),
                "lane_b": stage1_result.get("lane_b"),
                "lane_c": stage1_result.get("lane_c"),
                "lane_d": stage1_result.get("lane_d"),
                "lane_e": stage1_result.get("lane_e"),
                "lane_f": stage1_result.get("lane_f"),
                "ecosystem_positioning": stage2_result.get("ecosystem_positioning")
            }
            
            # 整合所有输出，生成最终结构化报告（只对结构进行check）
            integrated_report = await self._generate_integrated_report(
                all_results, context
            )
            
            step_result = {
                "step": "stage3_result_integration",
                "status": "completed",
                "integrated_report": integrated_report,
                "data_completeness": self._calculate_completeness(all_results),
                "execution_time": (datetime.now() - stage_start).total_seconds(),
                "timestamp": datetime.now().isoformat()
            }
            
            context["steps"].append(step_result)
            return step_result
            
        except Exception as e:
            step_result = {
                "step": "stage3_result_integration",
                "status": "failed",
                "error": str(e),
                "execution_time": (datetime.now() - stage_start).total_seconds(),
                "timestamp": datetime.now().isoformat()
            }
            context["steps"].append(step_result)
            raise

    async def _generate_integrated_report(self, all_results: Dict[str, Any],
                                        context: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成整合报告（只对结构进行check，不需要code）
        """
        try:
            # 结构检查和验证
            report_structure = {
                "enterprise_info": {
                    "name": context["enterprise_name"],
                    "processing_timestamp": datetime.now().isoformat(),
                    "workflow_id": context["workflow_id"]
                },
                "data_sections": {},
                "structure_validation": {},
                "completeness_analysis": {},
                "quality_assessment": {}
            }
            
            # 对每个数据源进行结构检查
            for source_name, source_result in all_results.items():
                if source_result and source_result.get("status") == "completed":
                    # 结构验证
                    structure_check = self._validate_data_structure(
                        source_name, source_result.get("data")
                    )
                    
                    report_structure["data_sections"][source_name] = {
                        "status": "available",
                        "data_type": self._identify_data_type(source_result.get("data")),
                        "structure_valid": structure_check["is_valid"],
                        "validation_details": structure_check
                    }
                    
                    report_structure["structure_validation"][source_name] = structure_check
                else:
                    report_structure["data_sections"][source_name] = {
                        "status": "unavailable",
                        "reason": source_result.get("error", "未知错误") if source_result else "结果为空"
                    }
                    
                    report_structure["structure_validation"][source_name] = {
                        "is_valid": False,
                        "issues": ["数据不可用"]
                    }
            
            # 完整性分析
            report_structure["completeness_analysis"] = self._analyze_data_completeness(
                report_structure["data_sections"]
            )
            
            # 质量评估
            report_structure["quality_assessment"] = self._assess_data_quality(
                report_structure["structure_validation"]
            )
            
            return report_structure
            
        except Exception as e:
            return {
                "error": f"报告生成失败: {str(e)}",
                "all_results": all_results,
                "context": context
            }

    def _validate_data_structure(self, source_name: str, data: Any) -> Dict[str, Any]:
        """
        验证数据结构
        """
        validation_result = {
            "is_valid": False,
            "issues": [],
            "structure_info": {},
            "recommendations": []
        }
        
        try:
            if data is None:
                validation_result["issues"].append("数据为空")
                return validation_result
            
            if isinstance(data, dict):
                # 检查字典结构
                validation_result["structure_info"] = {
                    "type": "object",
                    "keys": list(data.keys()),
                    "key_count": len(data.keys()),
                    "nested_objects": sum(1 for v in data.values() if isinstance(v, dict)),
                    "arrays": sum(1 for v in data.values() if isinstance(v, list))
                }
                
                # 根据数据源检查必需字段
                required_fields = self._get_required_fields_by_source(source_name)
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    validation_result["issues"].append(f"缺少必需字段: {', '.join(missing_fields)}")
                else:
                    validation_result["is_valid"] = True
                
                # 检查数据质量
                if data.get("error"):
                    validation_result["issues"].append(f"数据包含错误信息: {data['error']}")
                
                if data.get("source") == "none":
                    validation_result["issues"].append("数据源标记为无效")
                    validation_result["recommendations"].append("建议检查数据获取逻辑")
                
            elif isinstance(data, list):
                # 检查数组结构
                validation_result["structure_info"] = {
                    "type": "array",
                    "length": len(data),
                    "item_types": list(set(type(item).__name__ for item in data)) if data else []
                }
                
                if len(data) > 0:
                    validation_result["is_valid"] = True
                else:
                    validation_result["issues"].append("数组为空")
            
            else:
                # 基本数据类型
                validation_result["structure_info"] = {
                    "type": type(data).__name__,
                    "value": str(data)[:100]  # 限制长度
                }
                validation_result["is_valid"] = True
            
            return validation_result
            
        except Exception as e:
            validation_result["issues"].append(f"结构验证异常: {str(e)}")
            return validation_result

    def _identify_data_type(self, data: Any) -> str:
        """
        识别数据类型
        """
        if data is None:
            return "null"
        elif isinstance(data, dict):
            return "object"
        elif isinstance(data, list):
            return "array"
        elif isinstance(data, str):
            return "string"
        elif isinstance(data, (int, float)):
            return "number"
        elif isinstance(data, bool):
            return "boolean"
        else:
            return type(data).__name__

    def _analyze_data_completeness(self, data_sections: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析数据完整性
        """
        total_sections = len(data_sections)
        available_sections = sum(1 for section in data_sections.values() 
                               if section.get("status") == "available")
        
        completeness_score = available_sections / total_sections if total_sections > 0 else 0
        
        return {
            "total_sections": total_sections,
            "available_sections": available_sections,
            "unavailable_sections": total_sections - available_sections,
            "completeness_score": completeness_score,
            "completeness_percentage": f"{completeness_score * 100:.1f}%",
            "completeness_grade": self._grade_completeness(completeness_score)
        }

    def _assess_data_quality(self, structure_validation: Dict[str, Any]) -> Dict[str, Any]:
        """
        评估数据质量
        """
        total_validations = len(structure_validation)
        valid_structures = sum(1 for validation in structure_validation.values()
                             if validation.get("is_valid", False))
        
        quality_score = valid_structures / total_validations if total_validations > 0 else 0
        
        # 收集所有问题
        all_issues = []
        for source_name, validation in structure_validation.items():
            issues = validation.get("issues", [])
            for issue in issues:
                all_issues.append(f"{source_name}: {issue}")
        
        return {
            "total_validations": total_validations,
            "valid_structures": valid_structures,
            "invalid_structures": total_validations - valid_structures,
            "quality_score": quality_score,
            "quality_percentage": f"{quality_score * 100:.1f}%",
            "quality_grade": self._grade_quality(quality_score),
            "issues_summary": all_issues[:10],  # 限制显示前10个问题
            "total_issues": len(all_issues)
        }

    def _grade_completeness(self, score: float) -> str:
        """
        完整性等级评定
        """
        if score >= 0.9:
            return "优秀"
        elif score >= 0.7:
            return "良好"
        elif score >= 0.5:
            return "一般"
        else:
            return "较差"

    def _grade_quality(self, score: float) -> str:
        """
        质量等级评定
        """
        if score >= 0.95:
            return "优秀"
        elif score >= 0.8:
            return "良好"
        elif score >= 0.6:
            return "一般"
        else:
            return "需要改进"

    def _calculate_completeness(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算整体完整性
        """
        total_lanes = len(all_results)
        completed_lanes = sum(1 for result in all_results.values()
                            if result and result.get("status") == "completed")
        
        return {
            "total_lanes": total_lanes,
            "completed_lanes": completed_lanes,
            "completion_rate": completed_lanes / total_lanes if total_lanes > 0 else 0,
            "missing_lanes": [name for name, result in all_results.items()
                            if not result or result.get("status") != "completed"]
        }

    def _get_required_fields_by_source(self, source_name: str) -> List[str]:
        """
        根据数据源获取必需字段
        """
        field_mapping = {
            "lane_a": ["address_info", "region_info"],
            "lane_b": ["industry_info", "position_analysis"],
            "lane_c": ["personnel_scale", "scale_category"],
            "lane_d": ["revenue_info"],
            "lane_e": ["opportunities"],
            "lane_f": ["news_articles", "summary"],
            "ecosystem_positioning": ["ecosystem_analysis"]
        }
        
        return field_mapping.get(source_name, [])
```

## 🔧 配置和部署

### 工作流配置
```python
# config/workflow_config.py
from pydantic import BaseSettings
from typing import Dict, Any

class WorkflowConfig(BaseSettings):
    # 并行处理配置
    max_concurrent_lanes: int = 6
    lane_timeout_seconds: int = 30
    
    # 数据过期配置
    address_expiry_years: int = 1
    industry_expiry_years: int = 1
    scale_expiry_months: int = 6
    revenue_expiry_months: int = 6
    
    # 重试配置
    max_retries: int = 3
    retry_delay_seconds: int = 2
    
    # 缓存配置
    enable_result_caching: bool = True
    cache_expiry_hours: int = 24
    
    # 监控配置
    enable_performance_monitoring: bool = True
    log_detailed_execution: bool = True
    
    class Config:
        env_prefix = "WORKFLOW_"
```

### 工作流监控
```python
# monitoring/workflow_monitor.py
import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class WorkflowMetrics:
    workflow_id: str
    enterprise_name: str
    start_time: datetime
    end_time: datetime = None
    status: str = "running"
    stage1_duration: float = 0.0
    stage2_duration: float = 0.0
    stage3_duration: float = 0.0
    total_duration: float = 0.0
    lane_metrics: Dict[str, Any] = None
    error_count: int = 0
    success_rate: float = 0.0

class WorkflowMonitor:
    def __init__(self):
        self.active_workflows: Dict[str, WorkflowMetrics] = {}
        self.completed_workflows: List[WorkflowMetrics] = []
    
    async def start_monitoring(self, workflow_id: str, enterprise_name: str):
        """
        开始监控工作流
        """
        metrics = WorkflowMetrics(
            workflow_id=workflow_id,
            enterprise_name=enterprise_name,
            start_time=datetime.now()
        )
        
        self.active_workflows[workflow_id] = metrics
        return metrics
    
    async def update_stage_metrics(self, workflow_id: str, stage: str, duration: float):
        """
        更新阶段指标
        """
        if workflow_id in self.active_workflows:
            metrics = self.active_workflows[workflow_id]
            
            if stage == "stage1":
                metrics.stage1_duration = duration
            elif stage == "stage2":
                metrics.stage2_duration = duration
            elif stage == "stage3":
                metrics.stage3_duration = duration
    
    async def complete_monitoring(self, workflow_id: str, success: bool):
        """
        完成工作流监控
        """
        if workflow_id in self.active_workflows:
            metrics = self.active_workflows[workflow_id]
            metrics.end_time = datetime.now()
            metrics.total_duration = (metrics.end_time - metrics.start_time).total_seconds()
            metrics.status = "completed" if success else "failed"
            
            # 移动到已完成列表
            self.completed_workflows.append(metrics)
            del self.active_workflows[workflow_id]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        获取性能摘要
        """
        if not self.completed_workflows:
            return {"status": "no_data"}
        
        total_workflows = len(self.completed_workflows)
        successful_workflows = sum(1 for w in self.completed_workflows if w.status == "completed")
        
        avg_duration = sum(w.total_duration for w in self.completed_workflows) / total_workflows
        
        return {
            "total_workflows": total_workflows,
            "successful_workflows": successful_workflows,
            "success_rate": successful_workflows / total_workflows,
            "average_duration": avg_duration,
            "active_workflows": len(self.active_workflows),
            "performance_grade": self._grade_performance(successful_workflows / total_workflows, avg_duration)
        }
    
    def _grade_performance(self, success_rate: float, avg_duration: float) -> str:
        """
        性能等级评定
        """
        if success_rate >= 0.95 and avg_duration <= 30:
            return "优秀"
        elif success_rate >= 0.90 and avg_duration <= 60:
            return "良好"
        elif success_rate >= 0.80 and avg_duration <= 120:
            return "一般"
        else:
            return "需要优化"
```

## 📊 使用示例

### API调用示例
```bash
# 处理企业信息工作流
curl -X POST "http://localhost:9003/api/v1/workflow/process" \
  -H "Content-Type: application/json" \
  -d '{
    "enterprise_name": "青岛海尔智家股份有限公司",
    "force_refresh": false
  }'

# 获取工作流状态
curl -X GET "http://localhost:9003/api/v1/workflow/status/{workflow_id}"

# 获取性能监控数据
curl -X GET "http://localhost:9003/api/v1/workflow/metrics"
```

### 响应示例
```json
{
  "workflow_id": "wf_20250926_001",
  "status": "success",
  "result": {
    "workflow_type": "existing_enterprise_processing",
    "enterprise_id": 123,
    "enterprise_name": "青岛海尔智家股份有限公司",
    "stage1_result": {
      "lane_a": {
        "status": "completed",
        "data": {
          "source": "local",
          "address_info": {...},
          "region_info": {...}
        }
      },
      "lane_b": {...},
      "lane_c": {...},
      "lane_d": {...},
      "lane_e": {...},
      "lane_f": {...}
    },
    "stage2_result": {
      "status": "completed",
      "ecosystem_positioning": {...}
    },
    "final_result": {
      "integrated_report": {...},
      "data_completeness": {
        "completion_rate": 0.85,
        "completeness_grade": "良好"
      }
    }
  },
  "timestamp": "2025-09-26T11:30:00Z"
}
```

---

*文档版本：v1.0*
*更新时间：2025年9月26日*