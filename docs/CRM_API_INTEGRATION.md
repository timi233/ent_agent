# CRM 商机数据接口集成文档

## 概述

本文档描述了如何使用 CRM 商机数据接口，该接口提供了按企业名称搜索商机、获取项目状态列表等功能。

## 接口列表

### 1. 健康检查
```
GET /api/v1/crm/health
```

**响应示例：**
```json
{
  "status": "healthy",
  "database": "CRM_Feishu_DB",
  "host": "192.168.101.13:3306",
  "message": "CRM数据库连接正常",
  "timestamp": "2025-09-30T04:46:11.093102Z"
}
```

### 2. 获取项目状态列表
```
GET /api/v1/crm/statuses
```

**响应示例：**
```json
{
  "statuses": ["丢单", "参与", "可控", "必签"]
}
```

### 3. 搜索商机数据
```
GET /api/v1/crm/opportunities?company_name={企业名称}&status={项目状态}&page={页码}&page_size={每页大小}
```

**参数说明：**
- `company_name`（可选）：企业名称，支持模糊匹配
- `status`（可选）：项目状态过滤
- `page`（可选）：页码，从1开始，默认1
- `page_size`（可选）：每页大小，1-100，默认20

**响应示例：**
```json
{
  "opportunities": [
    {
      "opportunity_name": "青岛东亿供热管理有限公司-参与-绿盟零信任...",
      "customer_name": "青岛东亿供热管理有限公司",
      "status": "参与",
      "product": null,
      "description": "绿盟零信任",
      "owner_name": "纪壮",
      "expected_amount_wan": "4",
      "contract_opportunity_name": null,
      "id": "recuTZVqDdJwdX",
      "created_time": "2025-08-16T09:56:58",
      "expected_deal_date": "2025-09-30T00:00:00",
      "updated_at": "2025-09-27T05:00:08"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 3,
    "total_count": 881,
    "total_pages": 294,
    "has_next": true,
    "has_prev": false
  }
}
```

### 4. 获取商机详情
```
GET /api/v1/crm/opportunities/{opportunity_id}
```

**响应示例：**
```json
{
  "opportunity_name": "青岛东亿供热管理有限公司-参与-绿盟零信任...",
  "customer_name": "青岛东亿供热管理有限公司",
  "status": "参与",
  "product": null,
  "description": "绿盟零信任",
  "owner_name": "纪壮",
  "expected_amount_wan": "4",
  "contract_opportunity_name": null,
  "id": "recuTZVqDdJwdX",
  "created_time": "2025-08-16T09:56:58",
  "expected_deal_date": "2025-09-30T00:00:00",
  "updated_at": "2025-09-27T05:00:08",
  "record_data": { /* 原始JSON数据 */ },
  "created_at": "2025-08-16T09:56:58"
}
```

## 前端集成示例

### Vue.js 集成示例

```javascript
// 在 Home.vue 中添加 CRM 商机数据获取
async function fetchCRMOpportunities(companyName) {
  try {
    const response = await axios.get('/api/v1/crm/opportunities', {
      params: {
        company_name: companyName,
        page: 1,
        page_size: 10
      }
    });
    
    return response.data;
  } catch (error) {
    console.error('获取CRM商机数据失败:', error);
    throw error;
  }
}

// 在企业查询结果中展示商机数据
async function processCompanyWithCRM(companyName) {
  // 并行获取企业信息和CRM商机数据
  const [companyInfo, crmData] = await Promise.allSettled([
    fetchCompanyInfo(companyName),
    fetchCRMOpportunities(companyName)
  ]);
  
  // 处理结果
  if (companyInfo.status === 'fulfilled') {
    // 展示企业信息
    displayCompanyInfo(companyInfo.value);
  }
  
  if (crmData.status === 'fulfilled') {
    // 展示CRM商机数据
    displayCRMOpportunities(crmData.value);
  }
}
```

### 数据字段说明

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `opportunity_name` | string | 机会名称 |
| `customer_name` | string | 客户名称 |
| `status` | string | 项目状态（丢单/参与/可控/必签） |
| `product` | string | 产品 |
| `description` | string | 商机描述 |
| `owner_name` | string | 商机创建人 |
| `expected_amount_wan` | string | 预计合同额（万元） |
| `contract_opportunity_name` | string | 合同管理-商机名称 |
| `created_time` | datetime | 商机创建时间 |
| `expected_deal_date` | datetime | 预计交易日期 |
| `updated_at` | datetime | 更新时间 |

## 使用场景

1. **企业查询增强**：在查询企业信息时，同时展示该企业的商机数据
2. **商机管理**：独立的商机数据查询和管理界面
3. **数据分析**：基于商机数据进行统计分析和报表生成

## 注意事项

1. 所有接口均为只读，不支持数据修改
2. 分页查询建议每页不超过100条记录
3. 企业名称搜索支持模糊匹配，会匹配包含关键词的所有企业
4. 时间字段均为 ISO 8601 格式的 UTC 时间

## 错误处理

接口可能返回的错误状态码：
- `404`：未找到指定的商机
- `500`：服务器内部错误（数据库连接失败等）

错误响应格式：
```json
{
  "detail": "错误描述信息"
}