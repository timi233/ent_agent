# 部署指南

本指南介绍如何在本地或服务器上部署后端服务，并进行最小化可用性验证（Smoke Test）。

环境要求
- Python 3.10+（已在本项目测试环境通过）
- 安装依赖：pip install -r requirements.txt
- .env 配置：确保 APP_PORT、HOST 以及外部服务密钥按需设置（示例：APP_PORT=9003）

启动后端（本地）
- 命令：python -m uvicorn main:app --host 0.0.0.0 --port ${APP_PORT:-9003}
- 默认端口：9003（可通过 APP_PORT 环境变量覆盖）

Smoke Test（最小样例）
1) 健康检查
   curl -s http://127.0.0.1:9003/api/v1/health
   预期：返回 {"status":"healthy",...}

2) 公司处理（渐进式）
   curl -s -X POST http://127.0.0.1:9003/api/v1/company/process/progressive \
     -H "Content-Type: application/json" \
     -d '{"input_text":"查询海尔集团"}'
   预期：返回 {"stage":4,"status":"completed",...}，包含 final_result 字段

前端联调提示
- 建议通过 Vite 代理将 /api 指向后端端口（示例：9003）
- 关键调用：POST /api/v1/company/process/progressive
- 避免跨域与路由不一致问题：确保前端请求前缀与后端路由一致（/api/v1）

可观测性与日志
- 标准 RequestLogger 已集成；测试环境可使用 NoOpRequestLogger 覆盖以避免副作用
- 健康检查端点：/api/v1/health、/api/v1/health/detailed、/api/v1/health/ready、/api/v1/health/live

故障排查
- 端口不一致：确认 APP_PORT 与前端代理端口一致
- 依赖问题：使用 httpx.AsyncClient + ASGITransport 进行集成测试更稳定
- 外部服务：对 LLM、新闻等外部调用已实现降级与超时，必要时在测试覆盖中替换为 Dummy 实现