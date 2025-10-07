# API密钥加载问题修复总结

## 问题描述

在运行端到端集成测试时，发现"博查AI搜索失败: API密钥无效或已过期"的错误，尽管用户已经将正确的API密钥更新到`.env`文件中。

## 根本原因

**问题核心：Python模块导入顺序**

1. **`.env`文件加载时机问题**：
   - `.env`文件需要通过`load_dotenv()`加载到环境变量中
   - 但`load_dotenv()`必须在任何使用`os.getenv()`的模块**导入之前**调用

2. **配置模块的加载时机**：
   - `config/settings.py`在类定义时使用`os.getenv()`读取环境变量
   - `infrastructure/external/bocha_client.py`在模块级别导入settings并使用其值
   - 如果这些模块在`load_dotenv()`之前被导入，`os.getenv()`返回`None`，导致使用默认值

3. **测试文件缺少`.env`加载**：
   - `test_e2e_integration.py`没有在文件开头调用`load_dotenv()`
   - `test_phase5_complete.py`也没有调用`load_dotenv()`
   - 这导致测试运行时API密钥未被正确加载

## 解决方案

### 修复1: test_e2e_integration.py

在文件开头，sys.path设置之后，立即加载环境变量：

```python
import sys
import os
import json
import time
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 加载环境变量 - 必须在导入其他模块之前
from dotenv import load_dotenv
load_dotenv()

# 然后才导入项目模块
from api.v1.dependencies import get_enterprise_service_refactored
...
```

### 修复2: test_phase5_complete.py

同样的修复方式：

```python
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 加载环境变量 - 必须在导入其他模块之前
from dotenv import load_dotenv
load_dotenv()

# 然后才导入项目模块
...
```

## 验证结果

修复后，API密钥正确加载：

```
=== API Keys Verification ===
✓ .env BOCHA_API_KEY: sk-a7700f379bd14d81a7afbb8e0c5ca2e3
✓ bocha_client DEFAULT_API_KEY: sk-a7700f379bd14d81a7afbb8e0c5ca2e3

✓ .env LLM_API_KEY: sk-43d6f975872c40969842811c419e4d7d
✓ llm_client DEFAULT_API_KEY: sk-43d6f975872c40969842811c419e4d7d

✅ BOCHA API keys match!
✅ LLM API keys match!
```

## 最佳实践

### 正确的加载顺序

任何Python脚本或测试文件，都应该遵循以下顺序：

1. **标准库导入** (sys, os等)
2. **路径设置** (sys.path.insert)
3. **加载环境变量** (`load_dotenv()`)
4. **第三方库导入**
5. **项目模块导入**

### 示例模板

```python
#!/usr/bin/env python3
"""
脚本/测试文件描述
"""

# 1. 标准库导入
import sys
import os

# 2. 路径设置（如果需要）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 3. 加载环境变量 - 关键步骤！
from dotenv import load_dotenv
load_dotenv()

# 4. 第三方库导入
import requests
import json

# 5. 项目模块导入
from api.v1.dependencies import get_enterprise_service_refactored
from infrastructure.external.bocha_client import BochaAIClient

# ... 其余代码
```

## 已有的正确实现

`main.py`已经正确实现了这个模式：

```python
import os
from datetime import datetime
from dotenv import load_dotenv
from infrastructure.utils.datetime_utils import now_utc

# 加载环境变量
load_dotenv()

from fastapi import FastAPI, Request
# ... 其他导入
```

这确保了FastAPI应用启动时API密钥被正确加载。

## 技术细节

### 为什么顺序很重要？

Python在导入模块时会执行模块级别的代码。当`config/settings.py`被导入时：

```python
class BochaAPISettings(BaseSettings):
    api_key: str = Field(default=os.getenv("BOCHA_API_KEY", "your_bocha_api_key_here"))
```

这行代码在类定义时执行`os.getenv("BOCHA_API_KEY")`：
- 如果**之前**调用了`load_dotenv()`：返回`.env`中的值
- 如果**没有**调用`load_dotenv()`：返回`None`，使用默认值`"your_bocha_api_key_here"`

### 配置加载流程

```
1. load_dotenv()
   ↓
2. .env文件内容 → 环境变量 (BOCHA_API_KEY=sk-xxx)
   ↓
3. import config.settings
   ↓
4. os.getenv("BOCHA_API_KEY") → 读取环境变量 → 获得正确的密钥
   ↓
5. BochaAPISettings.api_key = "sk-xxx"
```

如果跳过步骤1，步骤4将返回`None`。

## 受影响的文件

### 已修复
- ✅ `test_e2e_integration.py` - 添加了`load_dotenv()`
- ✅ `test_phase5_complete.py` - 添加了`load_dotenv()`

### 已正确实现
- ✅ `main.py` - 已在文件开头调用`load_dotenv()`

### 可能需要检查的文件
其他测试文件或脚本如果直接导入配置模块，也需要确保先调用`load_dotenv()`：
- `test_infrastructure.py`
- `test_external_services.py`
- `test_api_keys.py`
- `simple_test.py`

## 总结

**问题**：API密钥在测试中未被正确加载

**原因**：测试文件在导入使用`os.getenv()`的模块之前，没有调用`load_dotenv()`

**解决**：在所有测试文件开头，紧接着`sys.path`设置后，立即调用`load_dotenv()`

**结果**：API密钥现在正确从`.env`文件加载，匹配用户更新的值

---

**修复时间**: 2025-10-02
**修复人**: Claude Code Assistant
**验证状态**: ✅ 已验证，API密钥加载正确
