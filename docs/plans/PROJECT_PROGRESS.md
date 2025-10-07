2025-09-29 联调摘要（更新）
- 后端与前端
  - 后端服务稳定运行于 9010；健康检查 /api/v1/health 正常；前端代理 /api → 9010。
  - 前端“使用本地缓存”开关已生效：disable_cache = !useLocalCache，enable_network = true。
- 渐进式接口 /api/v1/company/process/progressive
  - 阶段2命中本地库（示例：青岛啤酒股份有限公司），融合 address、chain_status、data_source=local_db，并保持行业轻量推断“食品饮料制造业”。
  - 地区字段修复：只提取“市”
    - 地址/描述均仅提取“XX市”，不解析区县；返回前新增规范化，折叠末尾重复“市”（如“青岛市市”→“青岛市”）。
    - 当前“青岛啤酒”返回 details.district_name = “青岛市”。
  - 链主状态：本地 chain_leader_id 存在时，chain_status=“链主”已生效。
  - 联网补全：
    - revenue_info 成功从外部补全（示例：2021-2023 营收数据已填充）。
    - company_status 仍可能“暂无排名信息”（外部返回不足/不稳定时降级）。
- 外部密钥加载修复
  - 修复 bocha_client.py 与 llm_client.py：优先使用 config.settings.get_settings()（会读取 city_brain_system_refactored/.env 的 BOCHA_API_KEY/LLM_API_KEY），仅在失败时回退 simple_settings。
- 数据库层导入修复
  - 修复绝对导入为包内导入，避免“初始化真实客户仓储失败，回退Mock”。涉及：simple_connection.py、standalone_queries.py、queries.py。
  - standalone_queries 现可延迟导入真实 CustomerRepository；本地库命中已验证。
- 缓存与快速路径
  - 保持缓存策略：TTL=90天，标准化公司名作为键，schema_version 控制升级。
  - 已支持禁用缓存与启用联网的开关参数：disable_cache、enable_network，用于联调与绕过缓存。

近期修复细节记录
- company.py
  - 新增当仅有地址或描述时的“市”提取，弃用区/县提取；修正正则与组选择导致的“市市”问题；返回前做 normalize 折叠末尾“市”。
  - 融合逻辑确保仅当 district_name 为空时回填，避免二次覆盖。
- settings.py
  - 确保 _load_env_keys_from_dotenv 在 Settings 初始化时注入 BOCHA/LLM 密钥；被外部客户端读取。
- 前端 Home.vue
  - 开关初始化从 /api/v1/company/config 读取，提交 progressive 请求时携带 disable_cache / enable_network。

验证结果（青岛啤酒）
- 命中本地库：true；address: “青岛市市北区登州路56号”
- district_name: “青岛市”（只提取市，重复后缀已规范）
- chain_status: “链主”
- industry_chain: “现代轻工”
- industry_brain: 本城市暂无相关产业大脑（本地 brain_name/brain_id 均未命中）
- revenue_info: 已补全（联网）
- company_status: 暂无排名信息（待外部解析增强）

后续计划
1) 行业大脑 industry_brain 补全
   - 仅本地匹配策略：先用本地 brain_name；若为空且存在 brain_id，则通过本地映射（ID → 名称）回填。
   - 若以上均未命中，不再做任何推断或派生，直接返回“本城市暂无相关产业大脑”。
2) 企业地位 company_status
   - 优化 ranking_service 解析与兼容：增加重试、超时、结构容错（多来源解析 description/title/snippets）。
   - 若外部仍为空，提供简要占位但不影响其它字段。
3) 仓储与连接健壮性
   - 如需真实 MySQL 访问：确保安装 mysql-connector-python 并正确配置 simple_settings/database（已提供连接池封装）。
   - 完善 standalone_queries 的日志提示，便于快速甄别是否走 Mock。
4) 文档与运营工具
   - 缓存清理 API：POST /api/v1/company/cache/purge（按 normalize 名称清理）。
   - 在文档中补充字段来源优先级：local_db > network > derived，且仅在为空时回填。
   - 前端显示字段说明：对来源/推断/联网补全打 tag，便于运营识别。

操作指引
- 启动后端：uvicorn main:app --host 0.0.0.0 --port 9010
- 健康检查：GET /api/v1/health
- 渐进式测试（禁用缓存、启用联网）：
  curl -X POST http://127.0.0.1:9010/api/v1/company/process/progressive \
    -H 'Content-Type: application/json' \
    -d '{"input_text":"青岛啤酒","disable_cache":true,"enable_network":true}'

历史摘要（原文如下）
2025-09-29 联调摘要
- 修复数据库配置导入路径，接入真实仓储查询（standalone_queries 使用 CustomerRepository）。
- 渐进式接口 /api/v1/company/process/progressive：
  - 阶段2正确命中本地数据库（示例：青岛啤酒股份有限公司）。
  - 快速路径阶段融合本地数据：填充 company_name、address、chain_status、data_source=local_db。
  - 追加轻量行业推断（get_company_industry），当前示例行业：食品饮料制造业。
- 后端服务重启至 9010 端口，前端代理保持 /api → 9010，联调验证通过。

后续计划
- 新增缓存清理API：POST /api/v1/company/cache/purge，按标准化公司名删除缓存记录（normalize 作为键），用于运营侧强制失效缓存并触发最新查询。
- 缓存策略：新增 QD_company_cache 表，命中则直接返回；TTL=90天，避免三个月内重复计算。
  - 缓存键标准化：对公司名进行 normalize 后查询/写入，减少后缀差异带来的重复。
  - schema_version: 在缓存payload中加入版本字段，便于后续字段升级与批量失效。
- 进一步填充区域（district_name）与行业脑（brain_name）字段的 JOIN 来源，完善 final_result.details。
- 对链主企业补充更详细状态与等级信息（如有）。
- 增强数据增强服务的轻量化路径，丰富字段但避免外部耗时调用。
- 前端展示联调：确保“查询企业信息”页面正确显示本地融合后的细节字段。