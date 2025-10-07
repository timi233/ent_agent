"""
日志管理工具
重构自原有的 utils/logger.py，增强日志功能和配置管理
"""
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import json

from config.settings import get_settings

settings = get_settings()


class CityBrainLogger:
    """城市大脑日志管理器"""
    
    def __init__(self, log_dir: Optional[str] = None):
        """
        初始化城市大脑日志系统
        
        Args:
            log_dir: 日志目录，如果为None则使用配置中的目录
        """
        self.log_dir = Path(log_dir or settings.LOG_DIR)
        self.log_dir.mkdir(exist_ok=True)
        
        # 创建不同类型的日志文件
        self.setup_loggers()
    
    def setup_loggers(self):
        """设置不同类型的日志记录器"""
        today = datetime.now().strftime('%Y%m%d')
        
        # 主日志记录器
        self.main_logger = self._create_logger(
            'city_brain_main',
            self.log_dir / f"city_brain_{today}.log"
        )
        
        # 企业查询日志记录器
        self.company_logger = self._create_logger(
            'company_query',
            self.log_dir / f"company_queries_{today}.log"
        )
        
        # LLM分析日志记录器
        self.llm_logger = self._create_logger(
            'llm_analysis',
            self.log_dir / f"llm_analysis_{today}.log"
        )
        
        # 错误日志记录器
        self.error_logger = self._create_logger(
            'errors',
            self.log_dir / f"errors_{today}.log",
            level=logging.ERROR
        )
        
        # API请求日志记录器
        self.api_logger = self._create_logger(
            'api_requests',
            self.log_dir / f"api_requests_{today}.log"
        )
        
        # 数据库操作日志记录器
        self.db_logger = self._create_logger(
            'database',
            self.log_dir / f"database_{today}.log"
        )
    
    def _create_logger(self, name: str, log_file: Path, level: int = logging.INFO) -> logging.Logger:
        """
        创建日志记录器
        
        Args:
            name: 日志记录器名称
            log_file: 日志文件路径
            level: 日志级别
            
        Returns:
            配置好的日志记录器
        """
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # 避免重复添加处理器
        if logger.handlers:
            return logger
        
        # 文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        
        # 控制台处理器（仅在开发环境）
        if settings.ENVIRONMENT == "development":
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            
            # 格式化器
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # 文件格式化器（包含更多信息）
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def log_company_query(self, company_name: str, query_type: str, result: str, duration: Optional[float] = None):
        """
        记录企业查询日志
        
        Args:
            company_name: 企业名称
            query_type: 查询类型
            result: 查询结果
            duration: 查询耗时（秒）
        """
        log_data = {
            'company': company_name,
            'type': query_type,
            'result': result,
            'duration': duration
        }
        
        log_msg = f"企业查询 - {json.dumps(log_data, ensure_ascii=False)}"
        self.company_logger.info(log_msg)
    
    def log_llm_analysis(self, company_name: str, analysis_type: str, prompt_length: int, 
                        response_length: int, duration: Optional[float] = None):
        """
        记录LLM分析日志
        
        Args:
            company_name: 企业名称
            analysis_type: 分析类型
            prompt_length: 提示词长度
            response_length: 响应长度
            duration: 分析耗时（秒）
        """
        log_data = {
            'company': company_name,
            'type': analysis_type,
            'prompt_length': prompt_length,
            'response_length': response_length,
            'duration': duration
        }
        
        log_msg = f"LLM分析 - {json.dumps(log_data, ensure_ascii=False)}"
        self.llm_logger.info(log_msg)
    
    def log_progressive_stage(self, company_name: str, stage: int, stage_name: str, data_summary: str):
        """
        记录渐进式处理阶段
        
        Args:
            company_name: 企业名称
            stage: 阶段编号
            stage_name: 阶段名称
            data_summary: 数据摘要
        """
        log_data = {
            'company': company_name,
            'stage': stage,
            'stage_name': stage_name,
            'data_summary': data_summary
        }
        
        log_msg = f"渐进式处理 - {json.dumps(log_data, ensure_ascii=False)}"
        self.main_logger.info(log_msg)
    
    def log_error(self, error_type: str, error_msg: str, company_name: Optional[str] = None, 
                  context: Optional[Dict[str, Any]] = None):
        """
        记录错误日志
        
        Args:
            error_type: 错误类型
            error_msg: 错误消息
            company_name: 相关企业名称
            context: 错误上下文信息
        """
        log_data = {
            'type': error_type,
            'message': error_msg,
            'company': company_name,
            'context': context
        }
        
        log_msg = f"错误 - {json.dumps(log_data, ensure_ascii=False)}"
        self.error_logger.error(log_msg)
    
    def log_api_request(self, endpoint: str, company_name: str, request_data: Dict[str, Any], 
                       response_status: int, duration: Optional[float] = None):
        """
        记录API请求日志
        
        Args:
            endpoint: API端点
            company_name: 企业名称
            request_data: 请求数据
            response_status: 响应状态码
            duration: 请求耗时（秒）
        """
        log_data = {
            'endpoint': endpoint,
            'company': company_name,
            'request_data': request_data,
            'response_status': response_status,
            'duration': duration
        }
        
        log_msg = f"API请求 - {json.dumps(log_data, ensure_ascii=False)}"
        self.api_logger.info(log_msg)
    
    def log_database_query(self, query_type: str, table_name: str, conditions: str, 
                          result_count: int, duration: Optional[float] = None):
        """
        记录数据库查询日志
        
        Args:
            query_type: 查询类型
            table_name: 表名
            conditions: 查询条件
            result_count: 结果数量
            duration: 查询耗时（秒）
        """
        log_data = {
            'type': query_type,
            'table': table_name,
            'conditions': conditions,
            'result_count': result_count,
            'duration': duration
        }
        
        log_msg = f"数据库查询 - {json.dumps(log_data, ensure_ascii=False)}"
        self.db_logger.info(log_msg)
    
    def log_web_search(self, company_name: str, search_type: str, query: str, 
                      result_count: int, duration: Optional[float] = None):
        """
        记录网络搜索日志
        
        Args:
            company_name: 企业名称
            search_type: 搜索类型
            query: 搜索查询
            result_count: 结果数量
            duration: 搜索耗时（秒）
        """
        log_data = {
            'company': company_name,
            'type': search_type,
            'query': query,
            'result_count': result_count,
            'duration': duration
        }
        
        log_msg = f"网络搜索 - {json.dumps(log_data, ensure_ascii=False)}"
        self.main_logger.info(log_msg)
    
    def log_workflow_stage(self, company_name: str, workflow_id: str, stage: str, 
                          status: str, data: Optional[Dict[str, Any]] = None):
        """
        记录工作流阶段日志
        
        Args:
            company_name: 企业名称
            workflow_id: 工作流ID
            stage: 阶段名称
            status: 状态
            data: 相关数据
        """
        log_data = {
            'company': company_name,
            'workflow_id': workflow_id,
            'stage': stage,
            'status': status,
            'data': data
        }
        
        log_msg = f"工作流 - {json.dumps(log_data, ensure_ascii=False)}"
        self.main_logger.info(log_msg)


# 全局日志实例
_logger_instance = None

def get_logger() -> CityBrainLogger:
    """获取全局日志实例"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = CityBrainLogger()
    return _logger_instance

# 向后兼容
city_brain_logger = get_logger()
