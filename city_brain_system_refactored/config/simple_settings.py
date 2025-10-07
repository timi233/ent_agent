"""
简化的配置管理模块
不依赖外部库，纯Python实现
"""
import os
from typing import Optional

# 加载.env文件
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # 如果没有python-dotenv，手动加载.env文件
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()


class DatabaseSettings:
    """数据库配置"""
    def __init__(self):
        self.host = os.getenv('DB_HOST', "localhost")
        self.port = int(os.getenv('DB_PORT', 3306))
        self.username = os.getenv('DB_USERNAME', "City_Brain_user_mysql")
        self.password = os.getenv('DB_PASSWORD', "CityBrain@2024")
        self.database = os.getenv('DB_DATABASE', "City_Brain_DB")
        self.charset = os.getenv('DB_CHARSET', "utf8mb4")
        
        # 连接池配置
        self.pool_size = int(os.getenv('DB_POOL_SIZE', 10))
        self.max_overflow = int(os.getenv('DB_MAX_OVERFLOW', 20))
        self.pool_timeout = int(os.getenv('DB_POOL_TIMEOUT', 30))
        self.pool_recycle = int(os.getenv('DB_POOL_RECYCLE', 3600))


class BochaAPISettings:
    """博查AI API配置"""
    def __init__(self):
        self.base_url = os.getenv('BOCHA_BASE_URL', "https://api.bochaai.com/v1/web-search")
        self.api_key = os.getenv('BOCHA_API_KEY', "your_bocha_api_key_here")
        self.timeout = int(os.getenv('BOCHA_TIMEOUT', 30))
        self.max_retries = int(os.getenv('BOCHA_MAX_RETRIES', 3))
        self.retry_delay = float(os.getenv('BOCHA_RETRY_DELAY', 1.0))


class LLMAPISettings:
    """大语言模型API配置"""
    def __init__(self):
        self.base_url = os.getenv('LLM_BASE_URL', "https://api.deepseek.com")
        self.api_key = os.getenv('LLM_API_KEY', "your_deepseek_api_key_here")
        self.model = os.getenv('LLM_MODEL', "deepseek-chat")
        self.timeout = int(os.getenv('LLM_TIMEOUT', 60))
        self.max_retries = int(os.getenv('LLM_MAX_RETRIES', 3))
        self.retry_delay = float(os.getenv('LLM_RETRY_DELAY', 2.0))
        
        # 模型参数
        self.temperature = float(os.getenv('LLM_TEMPERATURE', 0.7))
        self.max_tokens = int(os.getenv('LLM_MAX_TOKENS', 2000))


class AppSettings:
    """应用配置"""
    def __init__(self):
        self.app_name = os.getenv('APP_NAME', "城市大脑企业信息处理系统")
        self.app_version = os.getenv('APP_VERSION', "2.0.0")
        self.debug = os.getenv('APP_DEBUG', 'False').lower() == 'true'
        
        # 服务器配置
        self.host = os.getenv('APP_HOST', "0.0.0.0")
        self.port = int(os.getenv('APP_PORT', 9003))
        
        # 日志配置
        self.log_level = os.getenv('APP_LOG_LEVEL', "INFO")
        self.log_file = os.getenv('APP_LOG_FILE', None)


class Settings:
    """主配置类"""
    def __init__(self):
        self.database = DatabaseSettings()
        self.bocha_api = BochaAPISettings()
        self.llm_api = LLMAPISettings()
        self.app = AppSettings()


# 全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取配置实例"""
    return settings


def validate_settings() -> bool:
    """验证配置的有效性"""
    try:
        # 验证数据库配置
        if not settings.database.host:
            raise ValueError("数据库主机地址不能为空")

        if not settings.database.username:
            raise ValueError("数据库用户名不能为空")

        if not settings.database.database:
            raise ValueError("数据库名称不能为空")

        return True

    except Exception as e:
        print(f"配置验证失败: {e}")
        return False


def load_settings() -> Settings:
    """加载配置（用于兼容性）"""
    return settings


def get_simple_config() -> Settings:
    """获取简化配置实例（用于兼容性）"""
    return settings
