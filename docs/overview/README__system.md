# 城市大脑企业信息处理系统

[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.104.1-green.svg)](https://fastapi.tiangolo.com/)

一个智能信息处理平台，旨在通过结合本地数据库、联网搜索和大语言模型技术，为用户提供企业及其关联产业信息的结构化总结。

## 功能特性

- **企业名称提取**: 从用户输入中自动提取企业名称
- **本地数据库查询**: 查询企业相关信息
- **联网搜索补充**: 使用博查AI搜索API补充缺失信息
- **智能摘要生成**: 利用DeepSeek大语言模型生成结构化摘要
- **RESTful API**: 提供易于集成的API接口

## 技术栈

- **后端框架**: FastAPI
- **数据库**: MySQL
- **搜索引擎**: 博查AI搜索API
- **大语言模型**: DeepSeek API
- **部署**: Docker & Docker Compose

## 系统架构

```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   用户输入      │───▶│  信息提取模块    │───▶│ 数据库查询模块   │
└─────────────────┘    └──────────────────┘    └──────────────────┘
                                                                  │
                                                                  ▼
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   联网搜索      │◀───│  数据处理中心    │───▶│   本地数据库     │
└─────────────────┘    └──────────────────┘    └──────────────────┘
        │                       │
        ▼                       ▼
┌─────────────────┐    ┌──────────────────┐
│  大语言模型     │◀───│  结果输出模块    │
└─────────────────┘    └──────────────────┘
```

## 快速开始

### 1. 克隆项目

```bash
git clone <项目地址>
cd city_brain_system
```

### 2. 配置环境

```bash
# 复制环境变量文件
cp .env.example .env

# 编辑.env文件，填入实际的API密钥
nano .env
```

### 3. 启动服务

```bash
# 使用Docker Compose启动（推荐）
docker-compose up -d

# 或者使用启动脚本
./start.sh
```

## API接口

### 健康检查

```
GET /api/v1/health
```

### 处理企业信息

```
POST /api/v1/process-company
```

**请求参数**:
```json
{
  "input_text": "我想了解阿里巴巴集团的相关信息"
}
```

**响应示例**:
```json
{
  "status": "success",
  "data": {
    "customer_name": "阿里巴巴集团",
    "industry_name": "互联网",
    "brain_name": "电子商务产业大脑",
    "chain_leader_name": "阿里巴巴集团",
    "district_name": "杭州市"
  },
  "summary": "阿里巴巴集团是一家知名的互联网公司...",
  "source": "local_with_web_supplement"
}
```

## 部署说明

详细部署说明请查看 [DEPLOYMENT.md](DEPLOYMENT.md) 文件。

## 目录结构

```
city_brain_system/
├── api/                 # API接口层
│   ├── bocha_client.py  # 博查API客户端
│   ├── llm_client.py    # LLM API客户端
│   └── routes.py        # API路由
├── config/              # 配置文件
│   └── config.ini       # 系统配置
├── database/            # 数据库相关
│   ├── connection.py    # 数据库连接
│   └── queries.py       # 数据库查询
├── services/            # 核心业务逻辑
│   └── company_service.py # 公司信息服务
├── tests/               # 测试文件
│   └── test_api.py      # API测试
├── utils/               # 工具函数
│   └── text_extractor.py # 文本提取工具
├── .env                 # 环境变量文件
├── .env.example         # 环境变量示例
├── DEPLOYMENT.md        # 部署说明
├── Dockerfile           # Docker配置
├── docker-compose.yml   # Docker Compose配置
├── main.py              # 应用入口
├── README.md            # 项目说明
├── requirements.txt     # 依赖列表
├── start.sh             # 启动脚本
└── test_system.py       # 系统测试脚本
```

## 开发指南

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行测试

```bash
python -m pytest tests/
```

### 代码格式化

```bash
# 格式化代码
black .

# 检查代码质量
flake8
```

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 许可证

本项目采用MIT许可证，详情请查看 [LICENSE](LICENSE) 文件。