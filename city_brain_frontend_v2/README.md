# City Brain Frontend v2

全新 Vue 3 + Vite 前端实现，围绕城市大脑重构的后端领域重新设计。本文档概述安装、开发、目录结构与常用命令。

## 环境准备
- Node.js 18+（建议 LTS）
- npm 9+ 或 pnpm/yarn（项目脚本默认 npm）
- 已配置后端 `.env`，确保 `city_brain_system_refactored` API 正常运行

### 本地启动
```bash
npm install
npm run dev
```
默认端口 `9002`，可在 `vite.config.ts` 调整。

### 代码质量
```bash
npm run lint     # ESLint + Prettier 检查
npm run test     # Vitest + @testing-library
npm run storybook # Storybook 组件文档（端口 7007）
```

## 目录结构
- `src/assets/styles`：设计令牌、全局样式
- `src/components`
  - `base/` 基础 UI（卡片、空状态）
  - `layout/` 布局框架（AppShell、TopBar、Sidebar）
  - `data/` 数据展示（表格、图表、动态表单、地图占位）
  - `feedback/` 反馈组件（Toast）
- `src/views`：按领域划分（dashboard、insights、operations、planning、admin）
- `src/stores`：Pinia Store；含单元测试示例
- `src/composables`：组合式函数封装加载、筛选、通知等逻辑
- `src/services`：API 封装，与后端 DTO 对齐
- `docs/`：设计方案与实施待办

## 环境变量
在根目录复制 `.env.example` 为 `.env`，并根据实际 API/
WebSocket 地址调整。

```bash
VITE_API_BASE_URL=http://localhost:9003/api
VITE_WEBSOCKET_URL=ws://localhost:9003/ws/notifications
```

## 与后端集成
- 所有接口约定返回 JSON，与 `city_brain_system_refactored` 服务保持字段一致
- 鉴权 token 将通过 Pinia identity store 注入 axios 拦截器（`utils/apiClient.ts`）
- WebSocket 用于实时通知（`useNotifications`），规划模块待接入地图 SDK

## 下一步
1. 对接真实 API/WS，补充错误兜底与状态管理
2. 替换 `CityMapCanvas` 为实际地图组件，支持图层高亮/可视化
3. 扩展端到端测试（Cypress/Lighthouse）并纳入 CI Pipeline
