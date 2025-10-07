# 外部服务日志与敏感信息保护

目标：在与外部 API（LLM、BochaAI）交互时，日志清晰可控，避免泄露敏感信息。

- 打印与日志
  - 禁止使用 `print`；统一使用 `logging.getLogger(__name__)`
  - 已修复文件：
    - `infrastructure/external/llm_client.py`（__main__ 段）
    - `infrastructure/external/bocha_client.py`（__main__ 段）
    - `infrastructure/external/service_manager.py`（__main__ 段）

- 敏感信息
  - 禁止在日志中输出明文 `api_key`、`secret`、`password`
  - `get_client_info()` 仅暴露 `has_api_key: bool` 等非敏感字段
  - 请求头设置通过会话管理器注入，不记录完整头部

- 异常处理与重试
  - 优先捕获具体异常：`requests.Timeout`、`ConnectionError`、`HTTP >= 500` 等
  - 认证错误（401/403）不重试，及时失败返回
  - 响应解析失败（JSONDecodeError）不重试，直接记录错误
  - 指数退避重试（已实现）

- 健康检查
  - `health_check()` 使用轻量请求，失败时返回 False 并记录错误
  - 上层 `ServiceManager` 聚合健康信息并统一格式化输出

- 后续优化建议
  - 为 `except Exception` 分支做细化分类，统一错误码与结构化错误日志
  - 在配置层集中管理外部服务的开关、超时与最大重试次数