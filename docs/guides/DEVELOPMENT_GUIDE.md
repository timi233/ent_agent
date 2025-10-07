# 城市大脑企业信息处理系统 开发指南

## 📋 概述

本文档为开发人员提供详细的开发指南，包括项目结构、开发环境搭建、编码规范和最佳实践。

**系统版本**: 1.0.0  
**更新时间**: 2025年9月28日

## 🏗️ 项目架构

### 架构模式

本项目采用**清洁架构**（Clean Architecture）模式，遵循以下原则：

- **依赖倒置**: 高层模块不依赖低层模块
- **单一职责**: 每个模块只负责一个功能
- **开闭原则**: 对扩展开放，对修改封闭
- **接口隔离**: 客户端不应该依赖它不需要的接口

### 目录结构

```
city_brain_system_refactored/
├── api/                        # API层 - 处理HTTP请求
│   ├── __init__.py
│   ├── router.py              # 顶级路由聚合
│   └── v1/                    # API版本1
│       ├── __init__.py
│       ├── dependencies.py    # 依赖注入
│       ├── endpoints/         # API端点
│       │   ├── __init__.py
│       │   ├── company.py     # 企业相关接口
│       │   └── health.py      # 健康检查接口
│       └── schemas/           # 请求/响应模型
│           ├── __init__.py
│           └── company.py
├── domain/                     # 领域层 - 业务逻辑
│   ├── __init__.py
│   └── services/              # 领域服务
│       ├── __init__.py
│       ├── enterprise_service.py      # 企业服务主逻辑
│       ├── search_service.py          # 搜索服务
│       ├── data_enhancement_service.py # 数据增强服务
│       └── analysis_service.py        # 分析服务
├── infrastructure/             # 基础设施层
│   ├── __init__.py
│   ├── database/              # 数据访问层
│   │   ├── __init__.py
│   │   ├── connection.py      # 数据库连接
│   │   ├── standalone_queries.py # 向后兼容查询接口
│   │   ├── models/            # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── customer.py
│   │   │   ├── enterprise.py
│   │   │   ├── industry.py
│   │   │   ├── industry_brain.py
│   │   │   ├── area.py
│   │   │   └── relations.py
│   │   └── repositories/      # 数据仓储
│   │       ├── __init__.py
│   │       ├── base_repository.py
│   │       ├── customer_repository.py
│   │       ├── enterprise_repository.py
│   │       ├── industry_repository.py
│   │       └── area_repository.py
│   ├── external/              # 外部服务
│   │   ├── __init__.py
│   │   ├── bocha_client.py    # 博查AI客户端
│   │   ├── llm_client.py      # LLM客户端
│   │   ├── service_manager.py # 服务管理器
│   │   ├── news_service.py    # 新闻服务
│   │   ├── ranking_service.py # 排名服务
│   │   └── revenue_service.py # 营收服务
│   └── utils/                 # 工具类
│       ├── __init__.py
│       ├── logger.py          # 日志工具
│       ├── text_processor.py  # 文本处理
│       └── address_processor.py # 地址处理
├── config/                     # 配置管理
│   ├── __init__.py
│   ├── simple_settings.py     # 简化配置管理
│   ├── settings.py            # 详细配置
│   └── database.py            # 数据库配置
├── tests/                      # 测试文件
│   ├── __init__.py
│   ├── integration/           # 集成测试
│   └── unit/                  # 单元测试
├── docs/                       # 文档
├── logs/                       # 日志文件
├── main.py                     # 应用入口
├── requirements.txt            # 依赖列表
└── .env.example               # 环境变量模板
```

## 🛠️ 开发环境搭建

### 1. 环境要求

- **Python**: 3.8+
- **数据库**: MySQL 8.0+
- **IDE**: PyCharm, VSCode, 或其他Python IDE
- **Git**: 版本控制

### 2. 本地开发环境

```bash
# 1. 克隆项目
git clone <repository_url>
cd city_brain_system_refactored

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等

# 5. 初始化数据库
# 确保MySQL服务运行，并创建相应的数据库

# 6. 运行测试
python test_infrastructure.py
python test_data_layer_complete.py

# 7. 启动开发服务器
python main.py
```

### 3. IDE配置

#### PyCharm配置

1. **项目解释器**: 选择虚拟环境中的Python解释器
2. **代码风格**: 设置为PEP 8
3. **导入优化**: 启用自动导入排序
4. **类型检查**: 启用类型提示检查

#### VSCode配置

**.vscode/settings.json**:
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true
}
```

## 📝 编码规范

### 1. Python代码规范

遵循 **PEP 8** 标准：

```python
# 好的示例
class EnterpriseService:
    """企业服务类，处理企业相关业务逻辑"""
    
    def __init__(self, search_service: SearchService):
        self.search_service = search_service
        self.logger = logging.getLogger(__name__)
    
    def process_company_info(self, user_input: str) -> Dict[str, Any]:
        """
        处理企业信息查询
        
        Args:
            user_input: 用户输入的查询文本
            
        Returns:
            包含企业信息的字典
            
        Raises:
            ValueError: 当输入为空时
        """
        if not user_input or not user_input.strip():
            raise ValueError("输入文本不能为空")
        
        # 业务逻辑实现
        result = self._extract_and_process(user_input.strip())
        return result
```

### 2. 命名规范

- **类名**: 使用PascalCase（如：`EnterpriseService`）
- **函数名**: 使用snake_case（如：`process_company_info`）
- **变量名**: 使用snake_case（如：`user_input`）
- **常量名**: 使用UPPER_CASE（如：`MAX_RETRY_COUNT`）
- **私有方法**: 以单下划线开头（如：`_extract_and_process`）

### 3. 类型注解

```python
from typing import Dict, List, Optional, Union, Any

def search_companies(
    query: str,
    limit: Optional[int] = None,
    filters: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """搜索企业信息"""
    pass

class CompanyResponse:
    def __init__(
        self,
        status: str,
        data: Optional[Dict[str, Any]] = None,
        message: str = ""
    ):
        self.status = status
        self.data = data
        self.message = message
```

### 4. 错误处理

```python
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def process_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """处理数据的示例函数"""
    try:
        # 验证输入
        if not data:
            raise ValueError("数据不能为空")
        
        # 业务逻辑
        result = perform_business_logic(data)
        
        logger.info(f"数据处理成功: {len(result)} 条记录")
        return {"status": "success", "data": result}
        
    except ValueError as e:
        logger.error(f"输入验证失败: {str(e)}")
        return {"status": "error", "message": str(e)}
    
    except Exception as e:
        logger.error(f"数据处理异常: {str(e)}", exc_info=True)
        return {"status": "error", "message": "内部处理错误"}
```

## 🧪 测试指南

### 1. 测试结构

```
tests/
├── unit/                      # 单元测试
│   ├── test_services.py      # 服务层测试
│   ├── test_repositories.py  # 仓储层测试
│   └── test_utils.py         # 工具类测试
├── integration/              # 集成测试
│   ├── test_api_endpoints.py # API集成测试
│   └── test_database.py      # 数据库集成测试
└── conftest.py               # 测试配置
```

### 2. 单元测试示例

```python
import unittest
from unittest.mock import Mock, patch
from domain.services.enterprise_service import EnterpriseService

class TestEnterpriseService(unittest.TestCase):
    
    def setUp(self):
        """测试前置设置"""
        self.mock_search_service = Mock()
        self.service = EnterpriseService(self.mock_search_service)
    
    def test_process_company_info_success(self):
        """测试企业信息处理成功场景"""
        # 准备测试数据
        user_input = "查询海尔集团"
        expected_result = {"status": "success", "data": {"name": "海尔集团"}}
        
        # 设置mock行为
        self.mock_search_service.extract_company_name_from_input.return_value = {
            "status": "success",
            "name": "海尔集团"
        }
        
        # 执行测试
        result = self.service.process_company_info(user_input)
        
        # 验证结果
        self.assertEqual(result["status"], "success")
        self.assertIn("data", result)
        
        # 验证mock调用
        self.mock_search_service.extract_company_name_from_input.assert_called_once_with(user_input)
    
    def test_process_company_info_empty_input(self):
        """测试空输入处理"""
        with self.assertRaises(ValueError):
            self.service.process_company_info("")
    
    @patch('domain.services.enterprise_service.logger')
    def test_process_company_info_exception_handling(self, mock_logger):
        """测试异常处理"""
        # 设置mock抛出异常
        self.mock_search_service.extract_company_name_from_input.side_effect = Exception("测试异常")
        
        # 执行测试
        result = self.service.process_company_info("测试输入")
        
        # 验证异常被正确处理
        self.assertEqual(result["status"], "error")
        mock_logger.error.assert_called()

if __name__ == '__main__':
    unittest.main()
```

### 3. 集成测试示例

```python
import asyncio
import pytest
from fastapi.testclient import TestClient
from main import app

class TestAPIIntegration:
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        return TestClient(app)
    
    def test_health_check(self, client):
        """测试健康检查接口"""
        response = client.get("/api/v1/health/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_company_process_endpoint(self, client):
        """测试企业信息处理接口"""
        payload = {"input_text": "查询测试企业"}
        response = client.post("/api/v1/company/process", json=payload)
        
        assert response.status_code in [200, 400]  # 可能因为外部服务不可用返回400
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
```

### 4. 运行测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试文件
python -m pytest tests/unit/test_services.py

# 运行带覆盖率的测试
python -m pytest tests/ --cov=. --cov-report=html

# 运行现有的测试脚本
python test_infrastructure.py
python test_data_layer_complete.py
python test_external_services.py
python test_integration_e2e.py
```

## 🔧 开发工具

### 1. 代码质量工具

```bash
# 安装开发工具
pip install black isort flake8 mypy pytest pytest-cov

# 代码格式化
black .
isort .

# 代码检查
flake8 .
mypy .
```

### 2. 预提交钩子

**.pre-commit-config.yaml**:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3.8

  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203]
```

### 3. 调试技巧

```python
import logging
import pdb

# 设置调试日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_function():
    # 添加断点
    pdb.set_trace()
    
    # 详细日志
    logger.debug("调试信息: 变量值为 %s", variable_value)
    
    # 性能监控
    import time
    start_time = time.time()
    # ... 执行代码 ...
    logger.info("执行耗时: %.3f秒", time.time() - start_time)
```

## 📚 最佳实践

### 1. 依赖注入

```python
# 好的做法：使用依赖注入
class EnterpriseService:
    def __init__(
        self,
        search_service: SearchService,
        data_enhancement_service: DataEnhancementService,
        analysis_service: AnalysisService
    ):
        self.search_service = search_service
        self.data_enhancement_service = data_enhancement_service
        self.analysis_service = analysis_service

# 避免的做法：直接实例化依赖
class BadEnterpriseService:
    def __init__(self):
        self.search_service = SearchService()  # 硬编码依赖
```

### 2. 配置管理

```python
# 好的做法：使用配置类
from config.simple_settings import load_settings

settings = load_settings()
database_url = settings.database_url

# 避免的做法：直接使用环境变量
import os
database_url = os.getenv("DATABASE_URL")  # 缺少默认值和验证
```

### 3. 错误处理

```python
# 好的做法：具体的异常处理
try:
    result = external_api_call()
except requests.ConnectionError:
    logger.error("网络连接失败")
    return {"status": "error", "message": "网络连接失败"}
except requests.Timeout:
    logger.error("请求超时")
    return {"status": "error", "message": "请求超时"}
except Exception as e:
    logger.error(f"未知错误: {str(e)}", exc_info=True)
    return {"status": "error", "message": "内部错误"}

# 避免的做法：捕获所有异常
try:
    result = external_api_call()
except Exception:
    return {"status": "error"}  # 信息不足
```

### 4. 日志记录

```python
import logging

logger = logging.getLogger(__name__)

def process_data(data):
    logger.info(f"开始处理数据，记录数: {len(data)}")
    
    try:
        # 处理逻辑
        result = perform_processing(data)
        logger.info(f"数据处理完成，结果数: {len(result)}")
        return result
    
    except Exception as e:
        logger.error(f"数据处理失败: {str(e)}", exc_info=True)
        raise
```

## 🚀 性能优化

### 1. 数据库优化

```python
# 使用连接池
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    database_url,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)

# 批量操作
def batch_insert(items):
    with engine.begin() as conn:
        conn.execute(
            insert_statement,
            [item.to_dict() for item in items]
        )
```

### 2. 缓存策略

```python
from functools import lru_cache
import time

# 内存缓存
@lru_cache(maxsize=128)
def get_industry_info(industry_id):
    return fetch_from_database(industry_id)

# 时间缓存
class TimedCache:
    def __init__(self, ttl=300):  # 5分钟TTL
        self.cache = {}
        self.ttl = ttl
    
    def get(self, key):
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key, value):
        self.cache[key] = (value, time.time())
```

### 3. 异步处理

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def process_multiple_companies(company_names):
    """并行处理多个企业"""
    tasks = []
    for name in company_names:
        task = asyncio.create_task(process_single_company(name))
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results

def cpu_intensive_task(data):
    """CPU密集型任务使用线程池"""
    with ThreadPoolExecutor() as executor:
        future = executor.submit(heavy_computation, data)
        return future.result()
```

## 📋 开发流程

### 1. 功能开发流程

1. **需求分析**: 理解业务需求
2. **设计方案**: 设计技术方案
3. **编写测试**: 先写测试用例（TDD）
4. **实现功能**: 编写业务代码
5. **代码审查**: 提交代码审查
6. **集成测试**: 运行集成测试
7. **部署上线**: 部署到生产环境

### 2. Git工作流

```bash
# 创建功能分支
git checkout -b feature/new-company-analysis

# 提交代码
git add .
git commit -m "feat: 添加企业分析功能"

# 推送分支
git push origin feature/new-company-analysis

# 创建Pull Request
# 代码审查通过后合并到主分支
```

### 3. 版本发布

```bash
# 更新版本号
# 在 main.py 和相关配置文件中更新版本

# 创建标签
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin v1.1.0

# 部署到生产环境
```

## 🔍 调试和故障排除

### 1. 常见问题

**导入错误**:
```python
# 确保使用绝对导入
from infrastructure.database.models.customer import Customer
# 而不是相对导入
from .models.customer import Customer
```

**数据库连接问题**:
```python
# 测试数据库连接
from infrastructure.database.connection import test_connection
result = test_connection()
print(f"数据库连接状态: {result}")
```

**外部服务调用失败**:
```python
# 检查外部服务状态
from infrastructure.external.service_manager import ServiceManager
manager = ServiceManager()
health = manager.get_all_service_health()
print(health)
```

### 2. 性能分析

```python
import cProfile
import pstats

def profile_function():
    """性能分析示例"""
    pr = cProfile.Profile()
    pr.enable()
    
    # 执行需要分析的代码
    result = your_function()
    
    pr.disable()
    stats = pstats.Stats(pr)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # 显示前10个最耗时的函数
    
    return result
```

---

**文档版本**: 1.0.0  
**最后更新**: 2025年9月28日