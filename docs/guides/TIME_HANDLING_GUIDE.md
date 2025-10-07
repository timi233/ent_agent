# 时间处理规范（UTC）

目标：全局统一使用时区感知的 UTC 时间，避免 naive datetime 与弃用 API，确保跨服务一致性。

- 统一函数
  - 使用 `infrastructure.utils.datetime_utils.now_utc()` 生成时间戳
  - 禁止使用 `datetime.utcnow()` 与 `datetime.now()`（无时区）
  - 如需字符串，使用 `now_utc().isoformat()`

- Pydantic 默认值
  - 使用 `Field(default_factory=now_UTC)`（注意：在代码中实际函数名为 `now_utc`）
  - 禁止 `lambda: datetime.now(timezone.utc)`

- 端点与响应
  - 所有 API 响应与日志时间均使用 `now_utc()`
  - 健康检查（health）与企业接口（company）已统一

- 测试与验证
  - 修改后运行 `pytest -q` 验证
  - 当前状态：全仓库已移除 `utcnow()`，默认时间统一，测试通过

- 迁移注意
  - 如需与数据库或外部 API 交互，保存/解析均以 ISO8601 UTC 字符串或带 tzinfo 的 datetime
  - 前端显示时再按用户时区转换