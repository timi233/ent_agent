# 公司相关 API 文档

基础信息
- 前缀：/api/v1/company
- 依赖：RequestLogger、RateLimiter、ServiceContainer（EnterpriseService、AnalysisService）

接口一：POST /process
- 请求模型：CompanyRequest
  - body: {"input_text": "查询海尔集团"}
- 响应模型：CompanyResponse
  - { "status": "success|error", "message": "...", "data": { "company_name": "...", ... }, "timestamp": "ISO" }
- 说明：
  - 通过 EnterpriseService.process_company_info 完成企业信息处理
  - 异常返回 400，携带 ErrorResponse 风格

接口二：POST /process/progressive
- 请求模型：ProgressiveCompanyRequest
  - body: {"input_text": "查询海尔集团", "disable_cache": false, "enable_network": true}
- 响应模型：ProgressiveStageData
  - { "stage": 1..4, "status": "processing|completed|error", "message": "...", "data": { "final_result": {...} }, "timestamp": "ISO" }
- 说明：
  - 阶段1：公司名提取
  - 阶段1.5：缓存命中（TTL=90天，标准化键）
  - 阶段2：本地库搜索
  - 阶段3：轻量化快速路径（必要字段兜底；可选联网补全）
  - 阶段4：完成并返回 final_result
  - 降级策略：外部依赖失败不阻塞，保留基本结果

接口三：GET /search?q=关键词
- 响应模型：CompanyResponse
- 说明：
  - 关键词为空返回 400
  - 内部复用 EnterpriseService.process_company_info

接口四：POST /update
- 请求模型：UpdateCompanyRequest
  - body: {"customer_id": 123, "updates": {...}}
- 响应模型：UpdateCompanyResponse
- 说明：
  - 用于更新本地企业信息；失败返回 400

接口五：POST /chain-leader/update
- 请求模型：ChainLeaderUpdateRequest
  - body: {"company_name": "...", "updates": {...}}
- 响应模型：ChainLeaderUpdateResponse
- 说明：
  - 专用于链主企业数据更新；失败返回 400

接口六：GET /config
- 返回：{status, data: {cache_enabled}, timestamp}
- 说明：前端获取公司模块配置，如缓存开关

健康检查（参考）
- /api/v1/health
- /api/v1/health/detailed
- /api/v1/health/ready
- /api/v1/health/live

联调提示
- 建议前端通过代理将 /api 指向后端端口
- 关键调用：POST /api/v1/company/process/progressive
- 测试环境可覆盖依赖：NoOpRequestLogger、DummyEnterpriseService、DummyAnalysisService，避免外部服务波动

示例请求（渐进式）
curl -X POST http://localhost:9003/api/v1/company/process/progressive \
  -H "Content-Type: application/json" \
  -d '{"input_text": "查询海尔集团"}'

示例响应（摘自本机 Smoke Test，字段可能随数据来源变化）
{
  "stage": 4,
  "status": "completed",
  "message": "企业信息轻量化处理完成（快速路径）",
  "data": {
    "final_result": {
      "company_name": "查询海尔集团",
      "summary": "企业名称：查询海尔集团。当前为快速路径结果，详细信息待后续阶段补充。",
      "details": {
        "name": "查询海尔集团",
        "industry": "家电电子",
        "industry_brain": "本城市暂无相关产业大脑",
        "revenue_info": "根据搜索结果，无法获取海尔集团2021-2023年的具体营收数据。",
        "company_status": "暂无排名信息",
        "data_source": "quick_path"
      },
      "news": {
        "summary": "## 最新商业动态 ...",
        "references": [{ "title": "...", "url": "..." }]
      },
      "schema_version": "v1"
    }
  },
  "timestamp": "2025-09-30T...Z"
}