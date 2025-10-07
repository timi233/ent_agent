# 城市大脑企业信息处理系统（重构版）总览与状态汇总（2025-09-29）

仅聚焦子项目：city_brain_system_refactored

-------------------------------------------------------------------------------

## 1) 架构与目录（概览）

- 分层架构
  - config（settings、database）
  - api（router、v1/endpoints、schemas、dependencies）
  - core（ai / company / search）
  - domain（services）
  - infrastructure（database: models / repositories / queries；external：bocha、llm 等；utils）
  - tests（unit / integration / 性能）
  - docs（API_DOCUMENTATION、DEPLOYMENT_GUIDE、DEVELOPMENT_GUIDE）
- 兼容策略
  - infrastructure/database/standalone_queries.py 提供向后兼容查询接口
  - enhanced_* 与 simple_* 仓储并行，支持真实库与模拟/独立路径切换

日志位置：city_brain_system_refactored/logs/*（已分模块记录；本次扫描未检出 ERROR/Exception/Traceback）

-------------------------------------------------------------------------------

## 2) 当前运行与联调状态

- 服务端口：9010
- 健康检查：GET /api/v1/health 正常
- 主要接口：POST /api/v1/company/process/progressive（渐进式处理）
- 开关参数：
  - disable_cache：true 时禁用缓存
  - enable_network：true 时启用联网补全
- 联调要点（见 PROGRESS_SUMMARY.md 2025-09-29）
  - 本地库命中示例：青岛啤酒股份有限公司
  - 地区字段：只提取“市”，并折叠“市市”
  - 链主状态：本地 chain_leader_id 存在时返回“链主”
  - revenue_info：可从外部补全；company_status 受外部源稳定性影响，可能为空
  - 外部密钥：优先 settings.get_settings() 读取 .env，失败回退 simple_settings

-------------------------------------------------------------------------------

## 3) 依赖与技术栈（requirements.txt）

- Web：fastapi 0.104.1，uvicorn[standard] 0.24.0
- 数据：sqlalchemy 1.4.x，pymysql 1.1.0，alembic 1.12.x
- 配置：pydantic[dotenv] 1.10.x，python-dotenv 1.0.0
- HTTP：httpx 0.25.x，requests 2.31.0
- 文本/数据：jieba、regex、pandas、numpy
- 缓存/日志：redis 5.0.1，loguru 0.7.2
- 测试/质量：pytest、pytest-asyncio、pytest-cov、black、flake8、mypy

-------------------------------------------------------------------------------

## 4) 阶段进度对齐

- 依据 TODO_LIST.md 与 PROGRESS_SUMMARY.md（2025-09-29 更新）：
  - 阶段一 基础设施：✅ 完成（目录、配置、连接、模型、工具、测试全通过）
  - 阶段二 数据层：✅ 完成（模型/仓储/查询接口与测试）
  - 阶段三 外部服务：✅ 完成（bocha/llm 客户端统一封装、重试、错误处理、测试通过）
  - 阶段五 API 层：✅ 完成（版本化路由、Pydantic 模型、依赖注入、测试）
  - 阶段四 核心业务：⏳ 进行中（处理器/增强器/分析器细化与覆盖测试尚未完结）
  - 阶段六 集成与性能：⏳ 待执行（E2E、性能压测、部署验证与文档同步）

关键已落地能力（摘要）
- 只提取“市”的地址规范化与末尾“市市”折叠
- 本地命中融合策略与字段来源优先级：local_db > network > derived（仅空值回填）
- 缓存策略与清理思路：TTL=90天；键使用标准化公司名；schema_version 控制升级

-------------------------------------------------------------------------------

## 5) 当前问题与关注点（重构版视角）

P1（高优先级）
- 行业大脑字段补全不完整
  - 策略就绪：优先本地 brain_name；若空且有 brain_id，则映射回填；否则返回“本城市暂无相关产业大脑”
  - 需要：补齐 ID→名称映射与仓储读取路径；增加单测
- 排名 company_status 不稳定
  - 需要：ranking_service 增强（重试、超时、结构容错、多来源融合 title/desc/snippets），并在为空时返回可控占位

P2（中优先级）
- 缓存清理能力缺失（运维/联调痛点）
  - 建议新增：POST /api/v1/company/cache/purge（参数：标准化公司名）；返回清理结果计数与版本

P3（低优先级）
- 文档与代码的来源标注说明有待加强
  - 建议：在响应体 details 中加入 source_tags（local_db / network / derived），并在 docs/API_DOCUMENTATION.md 同步

备注
- 本仓扫描未发现重构版错误日志（ERROR/Exception），后续上线前建议开启更细粒度 error 级别与结构化 JSON 日志以便追踪

-------------------------------------------------------------------------------

## 6) 接下来两周行动计划（仅重构版）

本周（W1）
1) 核心业务补齐（阶段四）
   - 完成 company 处理器/增强器/分析器模块拆分与落地
   - 为地址、行业、营收、链主状态等关键环节补充单测与集成测试
2) 排名与稳定性
   - ranking_service 增强：重试/超时/结构容错、多源解析与融合；为空时占位策略
3) 运维能力
   - 新增缓存清理 API：POST /api/v1/company/cache/purge
   - 响应字段 source_tags 输出与文档说明

下周（W2）
4) 行业大脑补全闭环
   - 脑 ID→名称映射与仓储路径打通；回填策略与回归测试
5) 集成与性能（阶段六）
   - E2E 脚本覆盖“青岛啤酒、澳柯玛、青岛海湾化学”
   - 压测 & 缓存命中率验证；完善 TTL/清理生效测试
6) 部署与可观测
   - 部署验证（Dockerfile/compose）；结构化日志 & 指标埋点；文档同步（DEPLOYMENT_GUIDE/DEVELOPMENT_GUIDE）

-------------------------------------------------------------------------------

## 7) 关键端点与命令（速查）

- 启动后端：uvicorn main:app --host 0.0.0.0 --port 9010
- 健康检查：GET /api/v1/health
- 渐进式处理：
  POST /api/v1/company/process/progressive
  body 示例：
  {
    "input_text": "青岛啤酒",
    "disable_cache": true,
    "enable_network": true
  }
- 建议新增：缓存清理
  POST /api/v1/company/cache/purge
  body：{"company_name": "<原始或标准化公司名>"}

-------------------------------------------------------------------------------

## 8) 风险与缓解

- 外部数据不稳定导致字段缺失
  - 缓解：重试+多源容错；为空时占位不影响其它字段
- MySQL 实库接入差异（如开启真实仓储）
  - 缓解：明确配置切换与连通性检查；在 standalone_queries 保留可回退路径
- 缓存一致性（schema_version 升级或清理时）
  - 缓解：加入 schema_version 校验与批量失效策略，提供 purge API

-------------------------------------------------------------------------------

维护者：AI Assistant
最后更新：2025-09-29 15:10 (UTC+8)