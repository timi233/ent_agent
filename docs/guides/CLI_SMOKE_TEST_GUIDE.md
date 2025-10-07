# CLI 烟雾测试与端口固定指南

环境为纯 CLI，无 GUI/MCP。通过固定端口与 curl 验证前后端联调。

固定端口
- 前端：9002（Vite strictPort=true）
- 后端：9003（uvicorn）

常用脚本
- 释放端口：./scripts/release_ports.sh
- 启动服务：./scripts/start_services.sh
- 一键重启并验收：./scripts/restart_and_smoke.sh
- 烟雾测试：./scripts/smoke_test.sh

验收标准
- 首页返回 200 且包含“城市大脑企业信息处理系统”
- /api/v1/health 返回 200
- POST /api/v1/company/process/progressive 返回 200，含快速路径字段

故障处理
- 端口占用：执行 ./scripts/release_ports.sh 后重启
- 后端未启动：确认 uvicorn main:app 监听在 9003
- 前端无法访问：确认 Vite 监听在 9002 且代理指向 9003