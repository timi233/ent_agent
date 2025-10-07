# AS和IPG商机数据集成总结

## 完成时间
2025-10-07

## 数据概览

### 数据库统计
- **AS系统商机**: 448条记录 (447个独立客户)
- **IPG系统商机**: 1,678条记录 (1,672个独立客户)
- **总计**: 2,126条商机记录
- **数据库**: feishu_crm (Docker MySQL)

### 数据表结构
1. `as_opportunities` - AS系统商机表
2. `ipg_clients` - IPG系统客户/商机表
3. `sync_tasks` - 同步任务日志表
4. `data_quality_metrics` - 数据质量监控表
5. `v_opportunities_unified` - 统一查询视图

---

## 后端集成

### 新增文件

#### 1. 数据模型
**文件**: `city_brain_system_refactored/infrastructure/database/models/opportunities.py`

**包含**:
- `ASOpportunity` - AS系统商机模型 (dataclass)
- `IPGClient` - IPG系统客户/商机模型 (dataclass)

**主要字段**:
- AS: customer_name, product_name, budget, partner_name, area, status等
- IPG: client_name, sell_product, agent_num, reseller_name, trade, location等

#### 2. 数据仓储
**文件**: `city_brain_system_refactored/infrastructure/database/repositories/opportunities_repository.py`

**类**: `OpportunitiesRepository`

**主要方法**:
- AS商机:
  - `find_as_opportunities_by_customer()` - 按客户名称查询
  - `search_as_opportunities()` - 关键词搜索
  - `get_as_opportunities_by_partner()` - 按合作伙伴查询
  - `get_as_opportunities_by_area()` - 按地区查询

- IPG商机:
  - `find_ipg_clients_by_name()` - 按客户名称查询
  - `search_ipg_clients()` - 关键词搜索
  - `get_ipg_clients_by_reseller()` - 按代理商查询
  - `get_ipg_clients_by_province()` - 按省份查询

- 统计:
  - `get_as_statistics()` - AS商机统计
  - `get_ipg_statistics()` - IPG商机统计

#### 3. API端点
**文件**: `city_brain_system_refactored/api/v1/endpoints/opportunities.py`

**路由前缀**: `/api/v1/opportunities`

**端点列表**:

1. **综合查询** (推荐)
   ```
   GET /api/v1/opportunities/search?company_name={企业名称}&limit_per_source=10
   ```
   - 同时查询AS和IPG两个系统
   - 返回包含两个系统数据的统一响应

2. **AS商机查询**
   ```
   GET /api/v1/opportunities/as/search?customer_name={客户名称}
   GET /api/v1/opportunities/as/search?keyword={关键词}
   GET /api/v1/opportunities/as/search?partner={合作伙伴}
   GET /api/v1/opportunities/as/search?area={地区}
   ```

3. **IPG商机查询**
   ```
   GET /api/v1/opportunities/ipg/search?client_name={客户名称}
   GET /api/v1/opportunities/ipg/search?keyword={关键词}
   GET /api/v1/opportunities/ipg/search?reseller={代理商}
   GET /api/v1/opportunities/ipg/search?province={省份}
   ```

4. **统计信息**
   ```
   GET /api/v1/opportunities/statistics      # 综合统计
   GET /api/v1/opportunities/as/statistics   # AS统计
   GET /api/v1/opportunities/ipg/statistics  # IPG统计
   ```

5. **健康检查**
   ```
   GET /api/v1/opportunities/health
   ```

### API响应示例

#### 综合查询响应
```json
{
  "success": true,
  "company_name": "山东华特磁电",
  "summary": {
    "as_count": 0,
    "ipg_count": 1,
    "total_count": 1
  },
  "data": {
    "as_opportunities": [],
    "ipg_clients": [
      {
        "id": 1,
        "rid": 185861,
        "client_name": "山东华特磁电集团股份有限公司",
        "client_type": "私营",
        "trade": "机械/重工",
        "sell_product": "IP-guard V4",
        "agent_num": 700,
        "status": "报备成功",
        "reseller_name": "山东普悦天诚...",
        "location_province": "山东",
        "location_city": "潍坊",
        "create_time": "2025-09-30T14:59:01",
        ...
      }
    ]
  }
}
```

#### 统计信息响应
```json
{
  "success": true,
  "data": {
    "as": {
      "total_count": 448,
      "unique_customers": 447,
      "partner_count": 1,
      "area_count": 1,
      "total_budget": 8450.0,
      "avg_budget": 18.86
    },
    "ipg": {
      "total_count": 1678,
      "unique_clients": 1672,
      "reseller_count": 9,
      "province_count": 12,
      "total_agents": 390282,
      "avg_agents": 232.59
    },
    "total_opportunities": 2126
  }
}
```

---

## 前端集成

### 新增文件

#### 1. 商机展示组件
**文件**: `city_brain_frontend/src/components/OpportunitiesSection.vue`

**功能**:
- 统一展示AS和IPG两个系统的商机数据
- 分系统展示，带有系统标识徽章
- 支持加载状态、错误状态、空数据状态
- 响应式卡片布局

**Props**:
- `asOpportunities` - AS商机数组
- `ipgClients` - IPG客户数组
- `loading` - 加载状态
- `error` - 错误状态

**展示内容**:

**AS商机卡片**:
- 客户名称
- 产品名称
- 预算金额
- 合作伙伴
- 所属地区
- 联系方式
- 创建时间
- 状态标签

**IPG商机卡片**:
- 客户名称
- 销售产品
- 授权点数
- 代理商
- 所属行业
- 所在地区
- 联系方式
- 成交信心
- 创建时间
- 状态标签

### 修改文件

#### Home.vue 更新

**主要改动**:

1. **导入新组件**
   ```javascript
   import OpportunitiesSection from '@/components/OpportunitiesSection.vue'
   ```

2. **更新数据结构**
   ```javascript
   data() {
     return {
       sections: {
         opportunities: { loading: false, error: false }
       },
       asOpportunities: [],
       ipgClients: []
     }
   }
   ```

3. **替换API调用**
   - 移除旧的 `fetchCRMOpportunities()` 方法
   - 新增 `fetchOpportunities()` 方法调用新API

4. **模板更新**
   ```vue
   <OpportunitiesSection
     :as-opportunities="asOpportunities"
     :ipg-clients="ipgClients"
     :loading="sections.opportunities.loading"
     :error="sections.opportunities.error"
   />
   ```

---

## 使用指南

### 后端测试

1. **测试健康检查**
   ```bash
   curl http://localhost:9003/api/v1/opportunities/health
   ```

2. **查询企业商机**
   ```bash
   curl "http://localhost:9003/api/v1/opportunities/search?company_name=山东华特磁电"
   ```

3. **查看统计信息**
   ```bash
   curl http://localhost:9003/api/v1/opportunities/statistics
   ```

### 前端使用

1. **访问系统**
   ```
   http://localhost:9002
   ```

2. **查询企业**
   - 输入企业名称（如："山东华特磁电"）
   - 点击"查询企业信息"
   - 系统会并行查询企业基本信息和商机信息

3. **查看结果**
   - 商机信息会在页面顶部优先展示
   - 分为AS系统和IPG系统两个区块
   - 每个商机以卡片形式展示详细信息

---

## 数据流程

```
用户输入企业名称
      ↓
前端并行请求3个接口:
  1. /api/v1/company/process (企业基本信息)
  2. /api/v1/company/process (网络资讯)
  3. /api/v1/opportunities/search (商机数据) ← 新增
      ↓
后端查询feishu_crm数据库:
  - as_opportunities表 (精确+模糊匹配)
  - ipg_clients表 (精确+模糊匹配)
      ↓
返回统一格式数据
      ↓
前端OpportunitiesSection组件渲染:
  - AS系统商机列表 (绿色标识)
  - IPG系统商机列表 (橙色标识)
```

---

## 数据源信息

### AS系统
- **数据来源**: AS合作伙伴商机管理系统
- **数据时间**: 2023-05-04 至 2025-09-29
- **主要内容**: 合作伙伴报备的销售商机
- **关键字段**: 客户名称、产品、预算、合作伙伴、地区

### IPG系统
- **数据来源**: IPG客户管理系统
- **数据时间**: 2020-04-03 至 2025-09-30
- **主要内容**: 代理商客户和销售机会
- **关键字段**: 客户名称、产品、点数、代理商、行业、地区

---

## 特性亮点

### 1. 统一查询
- 一次请求同时查询两个系统
- 自动处理精确匹配和模糊匹配
- 返回结构化的统一数据格式

### 2. 性能优化
- 独立数据库连接池
- 支持并行查询
- 前端异步加载

### 3. 数据完整性
- 保留原始字段信息
- 支持时间格式转换
- 提供数据源标识

### 4. 用户体验
- 分系统展示，清晰明了
- 状态标签颜色区分
- 响应式布局
- 加载骨架屏
- 空数据友好提示

---

## API文档

完整的API文档可以通过Swagger UI访问:
```
http://localhost:9003/docs
```

在文档中查找 **opportunities** 标签下的所有端点。

---

## 技术栈

### 后端
- FastAPI
- MySQL (Docker)
- mysql-connector-python
- Python dataclasses

### 前端
- Vue 3
- Element Plus
- Axios
- Vite

---

## 注意事项

1. **数据库连接**: 确保feishu_crm数据库可访问
2. **查询性能**: 已添加索引优化常见查询
3. **数据更新**: 通过sync_tasks表跟踪数据同步状态
4. **错误处理**: 前后端都有完整的错误处理机制

---

## 下一步建议

1. **数据同步**: 定期运行 `/home/jian/scripts/sync-data/run_pipeline.py` 更新数据
2. **监控**: 通过 `sync_tasks` 表监控数据导入情况
3. **扩展**: 根据需要添加更多筛选条件和排序选项
4. **优化**: 根据用户反馈优化查询性能和展示效果

---

## 联系方式

如有问题或建议，请查看相关文档：
- 后端文档: `/home/jian/code/code/city_brain_system_refactored/`
- 数据同步文档: `/home/jian/scripts/sync-data/QUICK_START.md`
- 重构方案: `/home/jian/scripts/sync-data/REFACTORING_PLAN.md`
