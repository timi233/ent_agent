import logging
import os
from datetime import datetime
from pathlib import Path
import json
import inspect
import functools

class AIAssistantLogger:
    def __init__(self, log_dir="logs"):
        """初始化AI助手操作日志系统"""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # 创建AI助手专用日志记录器
        self.setup_logger()
    
    def setup_logger(self):
        """设置AI助手日志记录器"""
        self.ai_logger = self._create_logger(
            'ai_assistant',
            self.log_dir / f"ai_assistant_{datetime.now().strftime('%Y%m%d')}.log"
        )
    
    def _create_logger(self, name, log_file, level=logging.INFO):
        """创建日志记录器"""
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # 避免重复添加处理器
        if logger.handlers:
            return logger
        
        # 文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        
        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def log_user_request(self, request_text, request_type="用户请求"):
        """记录用户请求"""
        log_msg = f"用户请求 - 类型: {request_type}, 内容: {request_text[:200]}{'...' if len(request_text) > 200 else ''}"
        self.ai_logger.info(log_msg)
    
    def log_task_analysis(self, task_description, identified_actions):
        """记录任务分析"""
        log_msg = f"任务分析 - 描述: {task_description}, 识别的操作: {identified_actions}"
        self.ai_logger.info(log_msg)
    
    def log_tool_call(self, tool_name, parameters, purpose):
        """记录工具调用"""
        log_msg = f"工具调用 - 工具: {tool_name}, 目的: {purpose}, 参数: {json.dumps(parameters, ensure_ascii=False)[:100]}{'...' if len(str(parameters)) > 100 else ''}"
        self.ai_logger.info(log_msg)
    
    def log_file_operation(self, operation_type, file_path, description):
        """记录文件操作"""
        log_msg = f"文件操作 - 类型: {operation_type}, 文件: {file_path}, 描述: {description}"
        self.ai_logger.info(log_msg)
    
    def log_code_generation(self, code_type, file_path, lines_count, description):
        """记录代码生成"""
        log_msg = f"代码生成 - 类型: {code_type}, 文件: {file_path}, 行数: {lines_count}, 描述: {description}"
        self.ai_logger.info(log_msg)
    
    def log_system_modification(self, modification_type, component, description):
        """记录系统修改"""
        log_msg = f"系统修改 - 类型: {modification_type}, 组件: {component}, 描述: {description}"
        self.ai_logger.info(log_msg)
    
    def log_problem_solving(self, problem_description, solution_approach, result):
        """记录问题解决过程"""
        log_msg = f"问题解决 - 问题: {problem_description}, 解决方案: {solution_approach}, 结果: {result}"
        self.ai_logger.info(log_msg)
    
    def log_testing_activity(self, test_type, test_target, test_result):
        """记录测试活动"""
        log_msg = f"测试活动 - 类型: {test_type}, 目标: {test_target}, 结果: {test_result}"
        self.ai_logger.info(log_msg)
    
    def log_completion(self, task_summary, completion_status, duration=None):
        """记录任务完成"""
        log_msg = f"任务完成 - 摘要: {task_summary}, 状态: {completion_status}"
        if duration:
            log_msg += f", 耗时: {duration:.2f}秒"
        self.ai_logger.info(log_msg)
    
    def log_error_handling(self, error_type, error_details, resolution_attempt):
        """记录错误处理"""
        log_msg = f"错误处理 - 类型: {error_type}, 详情: {error_details}, 解决尝试: {resolution_attempt}"
        self.ai_logger.error(log_msg)
    
    def log_optimization(self, optimization_type, target, improvement_description):
        """记录优化操作"""
        log_msg = f"系统优化 - 类型: {optimization_type}, 目标: {target}, 改进描述: {improvement_description}"
        self.ai_logger.info(log_msg)

# 全局AI助手日志实例
ai_assistant_logger = AIAssistantLogger()

# 自动日志记录装饰器
def auto_log_operation(operation_type):
    """自动记录操作的装饰器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 获取函数信息
            func_name = func.__name__
            module_name = func.__module__
            
            # 记录操作开始
            ai_assistant_logger.ai_logger.info(f"操作开始 - 类型: {operation_type}, 函数: {module_name}.{func_name}")
            
            try:
                # 执行函数
                result = func(*args, **kwargs)
                
                # 记录操作成功
                ai_assistant_logger.ai_logger.info(f"操作成功 - 类型: {operation_type}, 函数: {module_name}.{func_name}")
                
                return result
            except Exception as e:
                # 记录操作失败
                ai_assistant_logger.ai_logger.error(f"操作失败 - 类型: {operation_type}, 函数: {module_name}.{func_name}, 错误: {str(e)}")
                raise
        
        return wrapper
    return decorator

# 自动记录工具调用的函数
def log_tool_usage(tool_name, parameters, purpose):
    """自动记录工具使用"""
    ai_assistant_logger.log_tool_call(tool_name, parameters, purpose)

# 自动记录文件操作的函数
def log_file_operation_auto(operation_type, file_path, description):
    """自动记录文件操作"""
    ai_assistant_logger.log_file_operation(operation_type, file_path, description)

# 自动记录代码生成的函数
def log_code_generation_auto(code_type, file_path, lines_count, description):
    """自动记录代码生成"""
    ai_assistant_logger.log_code_generation(code_type, file_path, lines_count, description)

# 初始化自动记录功能
def initialize_auto_logging():
    """初始化自动日志记录功能"""
    ai_assistant_logger.ai_logger.info("AI助手自动日志记录系统已启动")
    
    # 记录系统启动信息
    ai_assistant_logger.log_system_modification("系统启动", "AI助手日志系统", "自动日志记录功能已启用")

# 立即初始化自动日志记录
initialize_auto_logging()