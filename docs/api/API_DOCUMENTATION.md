# 城市大脑企业信息处理系统 API 文档

## 📋 概述

城市大脑企业信息处理系统提供基于AI的企业信息搜索、分析和增强服务。本文档详细描述了系统的API接口、使用方法和最佳实践。

**版本**: 1.0.0  
**基础URL**: `http://localhost:8000`  
**API前缀**: `/api/v1`

## 🚀 快速开始

### 启动服务

```bash
cd city_brain_system_refactored
python main.py
```

服务将在 `http://localhost:8000` 启动，可以通过以下地址访问：

- **API文档**: http://localhost:8000/docs
- **ReDoc文档**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/api/v1/health

### 基础认证

当前版本暂不需要认证，所有接口都可以直接访问。

## 📚 API 接口

### 1. 健康检查接口

#### 1.1 基础健康检查

**接口**: `GET /api/v1/health/`

**描述**: 检查服务基本健康状态

**响应示例**:
```json
{
  "status": "healthy",
  "timestamp": "2025-09-28T08:00:00.000Z",
  "version": "1.0.0",
  "services": {
    "api": "healthy",
    "timestamp": "2025-09-28T08:00:00.000Z"
  }
}
```

#### 1.2 详细健康检查

**接口**: `GET /api/v1/health/detailed`

**描述**: 检查包括数据库、外部服务和系统资源的详细健康状态

**响应示例**:
```json
{
  "status": "healthy",
  "timestamp": "2025-09-28T08:00:00.000Z",
  "version": "1.0.0",
  "response_time_ms": 45.2,
  "services": {
    "api": "healthy",
    "database": {
      "status": "healthy",
      "message": "数据库连接正常",
      "response_time": "<100ms"
    },
    "external_services": {
      "status": "healthy",
      "message": "所有外部服务正常",
      "services": {
        "bocha_ai": {"status": "healthy"},
        "llm_service": {"status": "healthy"}
      }
    },
    "system_resources": {
      "status": "healthy",
      "message": "系统资源使用正常",
      "details": {
        "cpu_usage": "15.2%",
        "memory_usage": "45.8%",
        "disk_usage": "32.1%"
      }
    }
  }
}
```

#### 1.3 就绪检查

**接口**: `GET /api/v1/health/ready`

**描述**: 检查服务是否已准备好接收流量（Kubernetes就绪探针）

**响应状态码**:
- `200`: 服务就绪
- `503`: 服务未就绪

#### 1.4 存活检查

**接口**: `GET /api/v1/health/live`

**描述**: 检查服务是否存活（Kubernetes存活探针）

**响应状态码**:
- `200`: 服务存活
- `500`: 服务不存活

### 2. 企业信息处理接口

#### 2.1 企业信息处理

**接口**: `POST /api/v1/company/process`

**描述**: 处理企业信息查询请求，返回完整的企业信息分析结果

**请求体**:
```json
{
  "input_text": "查询海尔集团的详细信息"
}
```

**响应示例**:
```json
{
  "status": "success",
  "message": "企业信息处理完成",
  "data": {
    "company_name": "海尔集团",
    "summary": "海尔集团是全球知名的家电制造企业...",
    "details": {
      "name": "海尔集团",
      "address": "青岛市崂山区海尔路1号",
      "industry": "家电制造",
      "registration_capital": "80.09亿元",
      "legal_representative": "梁海山"
    },
    "analysis": {
      "business_scope": "家用电器、商用电器的研发、生产、销售...",
      "competitive_advantages": ["品牌知名度高", "产品线丰富", "国际化程度高"],
      "market_position": "中国家电行业领军企业"
    },
    "news": {
      "summary": "最近新闻摘要...",
      "articles": [
        {
          "title": "海尔集团发布2024年财报",
          "date": "2024-03-15",
          "summary": "营收增长15%..."
        }
      ]
    }
  },
  "timestamp": "2025-09-28T08:00:00.000Z"
}
```

#### 2.2 渐进式企业信息处理

**接口**: `POST /api/v1/company/process/progressive`

**描述**: 提供分阶段的企业信息处理，适用于需要实时反馈的场景

**请求体**:
```json
{
  "input_text": "查询华为技术有限公司的信息"
}
```

**响应示例**:
```json
{
  "stage": 4,
  "status": "completed",
  "message": "企业信息处理完成",
  "data": {
    "company_name": "华为技术有限公司",
    "local_result": {
      "found": true,
      "data": {...}
    },
    "final_result": {
      "company_name": "华为技术有限公司",
      "summary": "...",
      "details": {...}
    }
  },
  "timestamp": "2025-09-28T08:00:00.000Z"
}
```

**处理阶段说明**:
- `stage: 1` - 正在提取公司名称
- `stage: 2` - 正在搜索本地数据库
- `stage: 3` - 正在执行完整企业信息处理
- `stage: 4` - 处理完成

#### 2.3 企业搜索

**接口**: `GET /api/v1/company/search`

**描述**: 根据关键词搜索企业信息

**查询参数**:
- `q` (必需): 搜索关键词

**示例**: `GET /api/v1/company/search?q=腾讯`

**响应示例**:
```json
{
  "status": "success",
  "message": "企业搜索完成",
  "data": {
    "company_name": "腾讯控股有限公司",
    "summary": "...",
    "details": {...}
  },
  "timestamp": "2025-09-28T08:00:00.000Z"
}
```

#### 2.4 更新企业信息

**接口**: `POST /api/v1/company/update`

**描述**: 更新本地数据库中的企业信息

**请求体**:
```json
{
  "customer_id": 12345,
  "updates": {
    "address": "新的企业地址",
    "phone": "新的联系电话",
    "industry": "更新的行业分类"
  }
}
```

**响应示例**:
```json
{
  "status": "success",
  "message": "企业信息更新完成",
  "data": {
    "customer_id": 12345,
    "updated_fields": ["address", "phone", "industry"],
    "update_time": "2025-09-28T08:00:00.000Z"
  },
  "timestamp": "2025-09-28T08:00:00.000Z"
}
```

#### 2.5 更新链主企业信息

**接口**: `POST /api/v1/company/chain-leader/update`

**描述**: 专门用于更新链主企业的相关信息

**请求体**:
```json
{
  "company_name": "海尔集团",
  "updates": {
    "is_chain_leader": true,
    "chain_type": "家电产业链",
    "leadership_score": 95
  }
}
```

**响应示例**:
```json
{
  "status": "success",
  "message": "链主企业信息更新完成",
  "data": {
    "company_name": "海尔集团",
    "updated_fields": ["is_chain_leader", "chain_type", "leadership_score"],
    "update_time": "2025-09-28T08:00:00.000Z"
  },
  "timestamp": "2025-09-28T08:00:00.000Z"
}
```

## 📝 请求/响应格式

### 通用响应格式

所有API响应都遵循统一的格式：

```json
{
  "status": "success|error|processing",
  "message": "描述信息",
  "data": {}, // 具体数据，可选
  "timestamp": "2025-09-28T08:00:00.000Z"
}
```

### 错误响应格式

当发生错误时，响应格式如下：

```json
{
  "status": "error",
  "message": "错误描述",
  "error_code": "ERROR_CODE",
  "timestamp": "2025-09-28T08:00:00.000Z"
}
```

### 常见错误码

| 错误码 | 描述 | HTTP状态码 |
|--------|------|------------|
| `INVALID_INPUT` | 输入参数无效 | 400 |
| `COMPANY_NOT_FOUND` | 企业信息未找到 | 404 |
| `EXTERNAL_SERVICE_ERROR` | 外部服务调用失败 | 502 |
| `DATABASE_ERROR` | 数据库操作失败 | 500 |
| `INTERNAL_ERROR` | 服务器内部错误 | 500 |

## 🔧 使用示例

### Python 示例

```python
import requests

# 基础健康检查
response = requests.get("http://localhost:8000/api/v1/health/")
print(response.json())

# 企业信息查询
data = {"input_text": "查询阿里巴巴集团的信息"}
response = requests.post("http://localhost:8000/api/v1/company/process", json=data)
print(response.json())

# 企业搜索
response = requests.get("http://localhost:8000/api/v1/company/search?q=百度")
print(response.json())
```

### JavaScript 示例

```javascript
// 企业信息查询
const processCompany = async (inputText) => {
  const response = await fetch('http://localhost:8000/api/v1/company/process', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      input_text: inputText
    })
  });
  
  const result = await response.json();
  return result;
};

// 使用示例
processCompany('查询腾讯控股的详细信息')
  .then(result => console.log(result))
  .catch(error => console.error(error));
```

### cURL 示例

```bash
# 健康检查
curl -X GET "http://localhost:8000/api/v1/health/"

# 企业信息处理
curl -X POST "http://localhost:8000/api/v1/company/process" \
  -H "Content-Type: application/json" \
  -d '{"input_text": "查询华为技术有限公司的信息"}'

# 企业搜索
curl -X GET "http://localhost:8000/api/v1/company/search?q=海尔"
```

## 📊 性能指标

### 响应时间基准

| 接口类型 | 平均响应时间 | 95%分位数 |
|----------|--------------|-----------|
| 健康检查 | < 50ms | < 100ms |
| 企业搜索 | < 500ms | < 1s |
| 企业信息处理 | < 2s | < 5s |
| 数据更新 | < 200ms | < 500ms |

### 并发能力

- **最大并发连接数**: 100
- **推荐并发数**: 20
- **请求限制**: 100 requests/minute per IP

## 🛡️ 安全考虑

### 输入验证

- 所有输入都经过严格验证
- 防止SQL注入和XSS攻击
- 输入长度限制：文本输入最大1000字符

### 错误处理

- 不暴露敏感的系统信息
- 统一的错误响应格式
- 详细的日志记录（不包含敏感数据）

### 限流机制

- IP级别的请求限制
- 防止恶意请求和DDoS攻击
- 超出限制时返回429状态码

## 🔄 版本控制

### 当前版本: v1

- 所有接口都在 `/api/v1` 路径下
- 向后兼容性保证
- 废弃接口会提前通知

### 版本升级策略

- 主版本升级：破坏性变更
- 次版本升级：新功能添加
- 补丁版本：错误修复

## 📞 支持与联系

### 技术支持

- **文档**: http://localhost:8000/docs
- **问题反馈**: 通过系统日志查看详细错误信息
- **监控**: 通过健康检查接口监控系统状态

### 系统监控

建议设置以下监控：

```bash
# 健康检查监控
curl -f http://localhost:8000/api/v1/health/ready || exit 1

# 详细健康检查
curl -f http://localhost:8000/api/v1/health/detailed
```

---

**最后更新**: 2025年9月28日  
**文档版本**: 1.0.0