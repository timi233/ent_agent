# 部署说明

## 环境要求

- Python 3.11+
- pip包管理器
- Docker (可选，用于容器化部署)

## 本地部署

### 1. 克隆项目

```bash
git clone <项目地址>
cd city_brain_system
```

### 2. 配置环境变量

```bash
# 复制环境变量文件
cp .env.example .env

# 编辑.env文件，填入实际的API密钥
nano .env
```

### 3. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/Mac:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 4. 启动服务

```bash
# 使用启动脚本
./start.sh

# 或者直接使用uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Docker部署

### 1. 构建并启动容器

```bash
docker-compose up -d
```

### 2. 查看日志

```bash
docker-compose logs -f
```

## API使用

系统启动后，可以通过以下URL访问：

- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/api/v1/health
- 公司信息处理: POST http://localhost:8000/api/v1/process-company

### 示例请求

```bash
curl -X POST http://localhost:8000/api/v1/process-company \
  -H \"Content-Type: application/json\" \
  -d '{\"input_text\": \"我想了解阿里巴巴集团的相关信息\"}'
```

## 配置说明

### 数据库配置

在 `config/config.ini` 文件中配置数据库连接信息：

```ini
[database]
host = 192.168.101.13
username = City_Brain_user_mysql
password = CityBrain123@
database = City_Brain_DB
```

### API密钥配置

在 `.env` 文件中配置API密钥：

```env
BOCHA_API_KEY=your_actual_bocha_api_key_here
DEEPSEEK_API_KEY=your_actual_deepseek_api_key_here
```