# 城市大脑系统重构计划

## 📋 重构概述

本重构计划旨在按照最佳实践重新组织现有代码，提高代码的可维护性、可测试性和可扩展性。重构过程将分阶段进行，每次只处理部分模块，便于代码复核和测试。

## 🎯 重构目标

1. **模块化设计**: 按业务功能拆分大型文件
2. **职责分离**: 明确各层职责，降低耦合度
3. **代码复用**: 提取公共逻辑，减少重复代码
4. **测试友好**: 便于单元测试和集成测试
5. **向后兼容**: 保持现有API接口不变

## 📁 新的目录结构

```
city_brain_system_refactored/
├── main.py                          # 应用入口
├── requirements.txt                 # 依赖管理
├── config/                          # 配置管理
│   ├── __init__.py
│   ├── settings.py                  # 应用配置
│   └── database.py                  # 数据库配置
├── api/                             # API接口层
│   ├── __init__.py
│   ├── dependencies.py              # 依赖注入
│   ├── middleware.py                # 中间件
│   └── v1/                          # API版本管理
│       ├── __init__.py
│       ├── company.py               # 企业相关接口
│       ├── health.py                # 健康检查接口
│       └── schemas/                 # 请求/响应模型
│           ├── __init__.py
│           ├── company.py
│           └── common.py
├── core/                            # 核心业务逻辑
│   ├── __init__.py
│   ├── company/                     # 企业业务模块
│   │   ├── __init__.py
│   │   ├── service.py               # 企业服务
│   │   ├── processor.py             # 企业信息处理器
│   │   ├── enhancer.py              # 数据增强器
│   │   └── analyzer.py              # 企业分析器
│   ├── search/                      # 搜索模块
│   │   ├── __init__.py
│   │   ├── web_search.py            # 网络搜索
│   │   └── text_extraction.py       # 文本提取
│   └── ai/                          # AI服务模块
│       ├── __init__.py
│       ├── llm_service.py           # 大语言模型服务
│       └── analysis_service.py      # AI分析服务
├── infrastructure/                  # 基础设施层
│   ├── __init__.py
│   ├── database/                    # 数据库相关
│   │   ├── __init__.py
│   │   ├── connection.py            # 数据库连接
│   │   ├── models/                  # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── customer.py
│   │   │   ├── enterprise.py
│   │   │   └── industry.py
│   │   └── repositories/            # 数据仓储
│   │       ├── __init__.py
│   │       ├── base.py
│   │       ├── customer.py
│   │       └── enterprise.py
│   ├── external/                    # 外部服务
│   │   ├── __init__.py
│   │   ├── bocha_client.py          # 博查AI客户端
│   │   └── llm_client.py            # LLM客户端
│   └── utils/                       # 工具类
│       ├── __init__.py
│       ├── text_processing.py       # 文本处理
│       ├── address_processing.py    # 地址处理
│       └── logging.py               # 日志工具
├── tests/                           # 测试代码
│   ├── __init__.py
│   ├── conftest.py                  # 测试配置
│   ├── unit/                        # 单元测试
│   │   ├── __init__.py
│   │   ├── test_company_service.py
│   │   └── test_repositories.py
│   └── integration/                 # 集成测试
│       ├── __init__.py
│       └── test_api.py
└── docs/                            # 文档
    ├── API.md
    └── DEPLOYMENT.md
```

## 📝 重构任务清单 (TODO List)

### 阶段一: 基础设施搭建 (第1-2天)
- [ ] 1.1 创建新的目录结构
- [ ] 1.2 设置配置管理模块 (config/)
- [ ] 1.3 重构数据库连接和模型 (infrastructure/database/)
- [ ] 1.4 迁移工具类 (infrastructure/utils/)
- [ ] 1.5 编译测试基础设施

### 阶段二: 数据层重构 (第3-4天)
- [ ] 2.1 完善数据模型定义
- [ ] 2.2 重构数据仓储层
- [ ] 2.3 保持向后兼容的查询接口
- [ ] 2.4 编译测试数据层

### 阶段三: 外部服务层重构 (第5天)
- [ ] 3.1 重构博查AI客户端
- [ ] 3.2 重构LLM客户端
- [ ] 3.3 统一外部服务接口
- [ ] 3.4 编译测试外部服务

### 阶段四: 核心业务逻辑重构 (第6-8天)
- [ ] 4.1 拆分企业服务 (company_service.py -> core/company/)
- [ ] 4.2 创建企业信息处理器
- [ ] 4.3 创建数据增强器
- [ ] 4.4 创建企业分析器
- [ ] 4.5 编译测试核心业务逻辑

### 阶段五: API层重构 (第9天)
- [ ] 5.1 重构API路由结构
- [ ] 5.2 创建请求/响应模型
- [ ] 5.3 添加依赖注入
- [ ] 5.4 编译测试API层

### 阶段六: 集成测试和优化 (第10天)
- [ ] 6.1 端到端集成测试
- [ ] 6.2 性能测试和优化
- [ ] 6.3 文档更新
- [ ] 6.4 部署验证

## 🔧 重构原则

1. **渐进式重构**: 每次只重构一个模块，确保系统始终可运行
2. **保持兼容性**: 不改变现有API接口，保证前端正常工作
3. **测试驱动**: 每个阶段完成后进行编译和测试
4. **代码复审**: 每次变更后进行代码审核
5. **文档同步**: 及时更新相关文档

## 📊 当前状态

- **总任务数**: 22个
- **已完成**: 0个
- **进行中**: 0个
- **待开始**: 22个
- **完成率**: 0%

## 🚀 开始重构

重构将从阶段一开始，首先搭建基础设施。每完成一个任务，将更新此文档的状态。

---

*重构计划创建时间: 2025年9月26日*
*预计完成时间: 2025年10月6日*