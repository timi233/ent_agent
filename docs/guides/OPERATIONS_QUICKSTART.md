# 运维快速上手（固定端口）

一键使用
- ./scripts/restart_and_smoke.sh

分步使用
1) 释放端口
   ./scripts/release_ports.sh
2) 启动后端（9003）
   cd city_brain_system_refactored && uvicorn main:app --host 0.0.0.0 --port 9003 --reload
3) 启动前端（9002，strictPort=true）
   cd city_brain_frontend && npm run dev -- --host 0.0.0.0 --port 9002
4) CLI 验收
   ./scripts/smoke_test.sh

说明
- 所有脚本在纯 CLI 环境可用
- 日常巡检建议先 release_ports 再 start_services 再 smoke_test