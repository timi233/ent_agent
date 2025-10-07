# Changelog

## 2025-09-30 — 前端首页(Home.vue)分块并行加载优化
- Changed:
  - 新增 `sections` 状态对象：`summary`, `info`, `news`，每块包含 `{ loading, error }`。
  - 在查询开始 (`processCompany`) 将三块置为 `loading`。
  - 在处理成功 (`handleProgressiveUpdate`) 根据返回内容分别结束各块的 `loading` 并清除 `error`。
  - 在处理错误时将三块标记为 `error`。
  - 在清空结果 (`clearResult`) 时重置三块状态。
  - 模板中为公司信息与新闻区块加入条件渲染：
    - 公司信息：`<div class="company-info" v-if="!sections?.info?.loading && !sections?.info?.error">`
    - 新闻区块：`<div class="company-news" v-if="!sections?.news?.loading && !sections?.news?.error && result.data && result.data.news">`
- Motivation:
  - 满足“每一项单独加载，有数据立即展示，未加载完成独立转圈”的交互要求；提升用户等待体验与可用性。
- Impact:
  - 与后端接口保持不变（仍使用 `/api/v1/company/process/progressive`）。
  - 前端呈现更加细化，避免单个分块数据缺失阻塞整体展示。
- Verification:
  - 启动前端，输入企业名称进行查询：
    - 可观察到公司信息与新闻分块独立的 `loading` 骨架或错误提示。
    - 某分块数据返回后立即渲染，其它分块在未完成时继续显示加载。
- Files touched:
  - `city_brain_frontend/src/views/Home.vue`
    - data：新增 `sections` 状态
    - methods：在 `processCompany`, `handleProgressiveUpdate`, `clearResult` 中更新分块状态
    - template：为公司信息与新闻区块添加独立状态门控