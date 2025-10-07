import logging
import os
from datetime import datetime
from pathlib import Path

class CityBrainLogger:
    def __init__(self, log_dir="logs"):
        """初始化城市大脑日志系统"""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # 创建不同类型的日志文件
        self.setup_loggers()
    
    def setup_loggers(self):
        """设置不同类型的日志记录器"""
        # 主日志记录器
        self.main_logger = self._create_logger(
            'city_brain_main',
            self.log_dir / f"city_brain_{datetime.now().strftime('%Y%m%d')}.log"
        )
        
        # 企业查询日志记录器
        self.company_logger = self._create_logger(
            'company_query',
            self.log_dir / f"company_queries_{datetime.now().strftime('%Y%m%d')}.log"
        )
        
        # LLM分析日志记录器
        self.llm_logger = self._create_logger(
            'llm_analysis',
            self.log_dir / f"llm_analysis_{datetime.now().strftime('%Y%m%d')}.log"
        )
        
        # 错误日志记录器
        self.error_logger = self._create_logger(
            'errors',
            self.log_dir / f"errors_{datetime.now().strftime('%Y%m%d')}.log",
            level=logging.ERROR
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
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        
        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def log_company_query(self, company_name, query_type, result, duration=None):
        """记录企业查询日志"""
        log_msg = f"企业查询 - 公司: {company_name}, 类型: {query_type}, 结果: {result}"
        if duration:
            log_msg += f", 耗时: {duration:.2f}秒"
        self.company_logger.info(log_msg)
    
    def log_llm_analysis(self, company_name, analysis_type, prompt_length, response_length, duration=None):
        """记录LLM分析日志"""
        log_msg = f"LLM分析 - 公司: {company_name}, 类型: {analysis_type}, Prompt长度: {prompt_length}, 响应长度: {response_length}"
        if duration:
            log_msg += f", 耗时: {duration:.2f}秒"
        self.llm_logger.info(log_msg)
    
    def log_progressive_stage(self, company_name, stage, stage_name, data_summary):
        """记录渐进式处理阶段"""
        log_msg = f"渐进式处理 - 公司: {company_name}, 阶段{stage}: {stage_name}, 数据摘要: {data_summary}"
        self.main_logger.info(log_msg)
    
    def log_error(self, error_type, error_msg, company_name=None, context=None):
        """记录错误日志"""
        log_msg = f"错误 - 类型: {error_type}, 消息: {error_msg}"
        if company_name:
            log_msg += f", 公司: {company_name}"
        if context:
            log_msg += f", 上下文: {context}"
        self.error_logger.error(log_msg)
    
    def log_api_request(self, endpoint, company_name, request_data, response_status):
        """记录API请求日志"""
        log_msg = f"API请求 - 端点: {endpoint}, 公司: {company_name}, 请求数据: {request_data}, 响应状态: {response_status}"
        self.main_logger.info(log_msg)
    
    def log_database_query(self, query_type, table_name, conditions, result_count):
        """记录数据库查询日志"""
        log_msg = f"数据库查询 - 类型: {query_type}, 表: {table_name}, 条件: {conditions}, 结果数量: {result_count}"
        self.main_logger.info(log_msg)
    
    def log_web_search(self, company_name, search_type, query, result_count, duration=None):
        """记录网络搜索日志"""
        log_msg = f"网络搜索 - 公司: {company_name}, 类型: {search_type}, 查询: {query}, 结果数量: {result_count}"
        if duration:
            log_msg += f", 耗时: {duration:.2f}秒"
        self.main_logger.info(log_msg)

# 全局日志实例
city_brain_logger = CityBrainLogger()