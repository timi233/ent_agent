"""
应用配置管理模块
简化版本，兼容不同的Pydantic版本
"""
from typing import Optional
import os

# 兼容不同版本的Pydantic
try:
    from pydantic_settings import BaseSettings
    from pydantic import Field
except ImportError:
    try:
        from pydantic import BaseSettings, Field
    except ImportError:
        # 如果Pydantic不可用，使用简单的配置类
        class BaseSettings:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
        
        def Field(default=None, description=""):
            return default


class DatabaseSettings(BaseSettings):
    """数据库配置"""

    host: str = Field(default="localhost", description="数据库主机地址")
    port: int = Field(default=3306, description="数据库端口")
    username: str = Field(default="City_Brain_user_mysql", description="数据库用户名")
    password: str = Field(default=os.getenv("DB_PASSWORD", "CityBrain@2024"), description="数据库密码")
    database: str = Field(default="City_Brain_DB", description="数据库名称")
    charset: str = Field(default="utf8mb4", description="字符集")

    pool_size: int = Field(default=10, description="连接池大小")
    max_overflow: int = Field(default=20, description="最大溢出连接数")
    pool_timeout: int = Field(default=30, description="连接超时秒数")
    pool_recycle: int = Field(default=3600, description="连接回收秒数")


class BochaAPISettings(BaseSettings):
    """博查AI API配置"""
    # 优先使用环境变量，兼容 .env 注入
    base_url: str = Field(default=os.getenv("BOCHA_BASE_URL", "https://api.bochaai.com/v1/web-search"), description="API地址")
    api_key: str = Field(default=os.getenv("BOCHA_API_KEY", "your_bocha_api_key_here"), description="API密钥")
    timeout: int = Field(default=int(os.getenv("BOCHA_TIMEOUT", 30)), description="请求超时时间")
    max_retries: int = Field(default=int(os.getenv("BOCHA_MAX_RETRIES", 3)), description="最大重试次数")
    retry_delay: float = Field(default=float(os.getenv("BOCHA_RETRY_DELAY", 1.0)), description="重试延迟秒数")


class LLMAPISettings(BaseSettings):
    """大语言模型API配置"""
    # 优先使用环境变量，兼容 .env 注入
    base_url: str = Field(default=os.getenv("LLM_BASE_URL", "https://api.deepseek.com"), description="LLM服务地址")
    api_key: str = Field(default=os.getenv("LLM_API_KEY", "your_deepseek_api_key_here"), description="LLM密钥")
    model: str = Field(default=os.getenv("LLM_MODEL", "deepseek-chat"), description="默认模型")
    timeout: int = Field(default=int(os.getenv("LLM_TIMEOUT", 60)), description="请求超时时间")
    max_retries: int = Field(default=int(os.getenv("LLM_MAX_RETRIES", 3)), description="最大重试次数")
    retry_delay: float = Field(default=float(os.getenv("LLM_RETRY_DELAY", 2.0)), description="重试延迟")

    temperature: float = Field(default=float(os.getenv("LLM_TEMPERATURE", 0.7)), description="采样温度")
    max_tokens: int = Field(default=int(os.getenv("LLM_MAX_TOKENS", 2000)), description="最大token数")


class AppSettings(BaseSettings):
    """应用配置"""

    app_name: str = Field(default="城市大脑企业信息处理系统", description="应用名称")
    app_version: str = Field(default="2.0.0", description="应用版本")
    debug: bool = Field(default=False, description="调试模式")

    host: str = Field(default="0.0.0.0", description="服务绑定地址")
    port: int = Field(default=9003, description="服务端口")

    log_level: str = Field(default="INFO", description="日志级别")
    log_file: Optional[str] = Field(default=None, description="日志文件路径")


class CRMDatabaseSettings(BaseSettings):
    """CRM数据库配置"""
    host: str = Field(default=os.getenv("CRM_DB_HOST", "localhost"), description="CRM数据库主机地址")
    port: int = Field(default=int(os.getenv("CRM_DB_PORT", 3306)), description="CRM数据库端口")
    username: str = Field(default=os.getenv("CRM_DB_USER", os.getenv("DB_USERNAME", "City_Brain_user_mysql")), description="CRM数据库用户名")
    password: str = Field(default=os.getenv("CRM_DB_PASS", os.getenv("DB_PASSWORD", "CityBrain@2024")), description="CRM数据库密码")
    database: str = Field(default=os.getenv("CRM_DB_NAME", os.getenv("DB_DATABASE", "City_Brain_DB")), description="CRM数据库名称")
    charset: str = Field(default=os.getenv("CRM_DB_CHARSET", os.getenv("DB_CHARSET", "utf8mb4")), description="CRM数据库字符集")
    
    pool_size: int = Field(default=5, description="CRM连接池大小")
    max_overflow: int = Field(default=10, description="CRM最大溢出连接数")
    pool_timeout: int = Field(default=30, description="CRM连接超时秒数")
    pool_recycle: int = Field(default=3600, description="CRM连接回收秒数")


class CacheSettings(BaseSettings):
    """缓存配置"""
    enabled: bool = Field(default=(os.getenv("CACHE_ENABLED", "true").lower() == "true"), description="是否启用本地缓存表")
    default_ttl: int = Field(default=int(os.getenv("CACHE_DEFAULT_TTL", 3600)), description="默认缓存过期秒数")
    redis_url: Optional[str] = Field(default=os.getenv("CACHE_REDIS_URL", None), description="Redis连接URL（可选）")
    memory_cache_size: int = Field(default=int(os.getenv("CACHE_MEMORY_CACHE_SIZE", 1000)), description="内存缓存容量（可选）")


class Settings:
    """主配置类"""
    def __init__(self):
        # 子配置
        self.database = DatabaseSettings()
        self.crm_database = CRMDatabaseSettings()
        self.bocha_api = BochaAPISettings()
        self.llm_api = LLMAPISettings()
        self.app = AppSettings()
        self.cache = CacheSettings()

        self.LOG_DIR = os.getenv("LOG_DIR", "logs")
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


def _load_env_keys_from_dotenv():
    """只加载 .env 中的外部服务密钥相关项，避免非兼容内容影响shell环境"""
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    try:
        env_path = os.path.abspath(env_path)
        if not os.path.isfile(env_path):
            return
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip()
                # 仅注入 BOCHA_* 与 LLM_* 密钥相关配置
                if key.startswith("BOCHA_") or key.startswith("LLM_"):
                    # 去除可能的引号
                    if ((val.startswith('"') and val.endswith('"')) or
                        (val.startswith("'") and val.endswith("'"))):
                        val = val[1:-1]
                    os.environ[key] = val
    except Exception:
        # 加载失败不影响后续逻辑
        pass

# 先加载关键密钥
_load_env_keys_from_dotenv()

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
