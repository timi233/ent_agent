# 部署指南

## 📋 概述

本文档详细描述了城市大脑企业信息处理系统的部署方案，包括开发环境、测试环境和生产环境的部署配置。

## 🏗️ 系统架构部署图

```mermaid
graph TB
    subgraph "负载均衡层"
        LB[Nginx负载均衡器]
    end
    
    subgraph "应用层"
        FE1[前端服务1]
        FE2[前端服务2]
        BE1[后端服务1]
        BE2[后端服务2]
    end
    
    subgraph "缓存层"
        REDIS[Redis集群]
    end
    
    subgraph "数据层"
        DB[MySQL主从集群]
    end
    
    subgraph "外部服务"
        BOCHAAI[博查AI API]
        DEEPSEEK[DeepSeek API]
    end
    
    LB --> FE1
    LB --> FE2
    LB --> BE1
    LB --> BE2
    
    BE1 --> REDIS
    BE2 --> REDIS
    BE1 --> DB
    BE2 --> DB
    
    BE1 --> BOCHAAI
    BE1 --> DEEPSEEK
    BE2 --> BOCHAAI
    BE2 --> DEEPSEEK
```

## 🐳 Docker容器化部署

### 后端Dockerfile
```dockerfile
# Dockerfile.backend
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建日志目录
RUN mkdir -p /app/logs

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 9003

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:9003/health || exit 1

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9003", "--workers", "4"]
```

### 前端Dockerfile
```dockerfile
# Dockerfile.frontend
FROM node:18-alpine AS builder

WORKDIR /app

# 复制package文件
COPY package*.json ./

# 安装依赖
RUN npm ci --only=production

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# 生产环境镜像
FROM nginx:alpine

# 复制构建结果
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制nginx配置
COPY nginx.conf /etc/nginx/nginx.conf

# 暴露端口
EXPOSE 80

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]
```

### Docker Compose完整配置
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  # Nginx负载均衡器
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - frontend1
      - frontend2
      - backend1
      - backend2
    restart: unless-stopped
    networks:
      - city_brain_network

  # 前端服务
  frontend1:
    build:
      context: ./city_brain_frontend
      dockerfile: Dockerfile
    restart: unless-stopped
    networks:
      - city_brain_network

  frontend2:
    build:
      context: ./city_brain_frontend
      dockerfile: Dockerfile
    restart: unless-stopped
    networks:
      - city_brain_network

  # 后端服务
  backend1:
    build:
      context: ./city_brain_system
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=mysql+asyncio://city_brain_user:${DB_PASSWORD}@mysql-master:3306/city_brain_db
      - REDIS_HOST=redis-master
      - REDIS_PORT=6379
      - BOCHAAI_API_KEY=${BOCHAAI_API_KEY}
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - LOG_LEVEL=INFO
    volumes:
      - ./logs/backend:/app/logs
    depends_on:
      - mysql-master
      - redis-master
    restart: unless-stopped
    networks:
      - city_brain_network

  backend2:
    build:
      context: ./city_brain_system
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=mysql+asyncio://city_brain_user:${DB_PASSWORD}@mysql-master:3306/city_brain_db
      - REDIS_HOST=redis-master
      - REDIS_PORT=6379
      - BOCHAAI_API_KEY=${BOCHAAI_API_KEY}
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - LOG_LEVEL=INFO
    volumes:
      - ./logs/backend:/app/logs
    depends_on:
      - mysql-master
      - redis-master
    restart: unless-stopped
    networks:
      - city_brain_network

  # MySQL主从集群
  mysql-master:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
      MYSQL_DATABASE: city_brain_db
      MYSQL_USER: city_brain_user
      MYSQL_PASSWORD: ${DB_PASSWORD}
      MYSQL_REPLICATION_USER: replication_user
      MYSQL_REPLICATION_PASSWORD: ${REPLICATION_PASSWORD}
    command: >
      --server-id=1
      --log-bin=mysql-bin
      --binlog-format=ROW
      --gtid-mode=ON
      --enforce-gtid-consistency=ON
      --log-slave-updates=ON
      --binlog-do-db=city_brain_db
    volumes:
      - mysql_master_data:/var/lib/mysql
      - ./mysql/master.cnf:/etc/mysql/conf.d/master.cnf
      - ./logs/mysql:/var/log/mysql
    ports:
      - "3306:3306"
    restart: unless-stopped
    networks:
      - city_brain_network

  mysql-slave:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
      MYSQL_DATABASE: city_brain_db
      MYSQL_USER: city_brain_user
      MYSQL_PASSWORD: ${DB_PASSWORD}
    command: >
      --server-id=2
      --relay-log=mysql-relay-bin
      --log-bin=mysql-bin
      --binlog-format=ROW
      --gtid-mode=ON
      --enforce-gtid-consistency=ON
      --log-slave-updates=ON
      --read-only=ON
      --skip-slave-start
    volumes:
      - mysql_slave_data:/var/lib/mysql
      - ./mysql/slave.cnf:/etc/mysql/conf.d/slave.cnf
    depends_on:
      - mysql-master
    restart: unless-stopped
    networks:
      - city_brain_network

  # Redis主从集群
  redis-master:
    image: redis:7-alpine
    command: >
      redis-server
      --appendonly yes
      --appendfsync everysec
      --save 900 1
      --save 300 10
      --save 60 10000
      --maxmemory 2gb
      --maxmemory-policy allkeys-lru
    volumes:
      - redis_master_data:/data
      - ./logs/redis:/var/log/redis
    ports:
      - "6379:6379"
    restart: unless-stopped
    networks:
      - city_brain_network

  redis-slave:
    image: redis:7-alpine
    command: >
      redis-server
      --slaveof redis-master 6379
      --appendonly yes
      --appendfsync everysec
      --save 900 1
      --save 300 10
      --save 60 10000
      --maxmemory 1gb
      --maxmemory-policy allkeys-lru
    volumes:
      - redis_slave_data:/data
    depends_on:
      - redis-master
    restart: unless-stopped
    networks:
      - city_brain_network

  # 监控服务
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    restart: unless-stopped
    networks:
      - city_brain_network

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
    restart: unless-stopped
    networks:
      - city_brain_network

volumes:
  mysql_master_data:
  mysql_slave_data:
  redis_master_data:
  redis_slave_data:
  prometheus_data:
  grafana_data:

networks:
  city_brain_network:
    driver: bridge
```

## 🔧 Nginx配置

### 负载均衡配置
```nginx
# nginx/nginx.conf
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    'rt=$request_time uct="$upstream_connect_time" '
                    'uht="$upstream_header_time" urt="$upstream_response_time"';

    access_log /var/log/nginx/access.log main;

    # 基础配置
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;

    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # 上游服务器配置
    upstream frontend_servers {
        least_conn;
        server frontend1:80 max_fails=3 fail_timeout=30s;
        server frontend2:80 max_fails=3 fail_timeout=30s;
    }

    upstream backend_servers {
        least_conn;
        server backend1:9003 max_fails=3 fail_timeout=30s;
        server backend2:9003 max_fails=3 fail_timeout=30s;
    }

    # 限流配置
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;

    # 主服务器配置
    server {
        listen 80;
        server_name your-domain.com;

        # 重定向到HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        # SSL配置
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_session_timeout 1d;
        ssl_session_cache shared:SSL:50m;
        ssl_session_tickets off;

        # 现代SSL配置
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # HSTS
        add_header Strict-Transport-Security "max-age=63072000" always;

        # 前端静态资源
        location / {
            proxy_pass http://frontend_servers;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # 缓存配置
            location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
                expires 1y;
                add_header Cache-Control "public, immutable";
            }
        }

        # API接口
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://backend_servers;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # 超时配置
            proxy_connect_timeout 30s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
            
            # 缓冲配置
            proxy_buffering on;
            proxy_buffer_size 4k;
            proxy_buffers 8 4k;
        }

        # 登录接口特殊限流
        location /api/auth/login {
            limit_req zone=login burst=5 nodelay;
            
            proxy_pass http://backend_servers;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # 健康检查
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }

        # 监控端点
        location /metrics {
            allow 127.0.0.1;
            allow 10.0.0.0/8;
            deny all;
            
            proxy_pass http://backend_servers/metrics;
        }
    }
}
```

## 🚀 部署脚本

### 自动化部署脚本
```bash
#!/bin/bash
# deploy.sh

set -e

# 配置变量
PROJECT_NAME="city-brain"
DOCKER_REGISTRY="your-registry.com"
VERSION=${1:-latest}
ENVIRONMENT=${2:-production}

echo "🚀 开始部署城市大脑系统 - 版本: $VERSION, 环境: $ENVIRONMENT"

# 检查必要的环境变量
check_env_vars() {
    local required_vars=(
        "DB_PASSWORD"
        "DB_ROOT_PASSWORD"
        "REPLICATION_PASSWORD"
        "BOCHAAI_API_KEY"
        "DEEPSEEK_API_KEY"
        "GRAFANA_PASSWORD"
    )
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            echo "❌ 环境变量 $var 未设置"
            exit 1
        fi
    done
    
    echo "✅ 环境变量检查通过"
}

# 构建镜像
build_images() {
    echo "🔨 构建Docker镜像..."
    
    # 构建后端镜像
    docker build -t $DOCKER_REGISTRY/$PROJECT_NAME-backend:$VERSION ./city_brain_system
    
    # 构建前端镜像
    docker build -t $DOCKER_REGISTRY/$PROJECT_NAME-frontend:$VERSION ./city_brain_frontend
    
    echo "✅ 镜像构建完成"
}

# 推送镜像到仓库
push_images() {
    echo "📤 推送镜像到仓库..."
    
    docker push $DOCKER_REGISTRY/$PROJECT_NAME-backend:$VERSION
    docker push $DOCKER_REGISTRY/$PROJECT_NAME-frontend:$VERSION
    
    echo "✅ 镜像推送完成"
}

# 部署服务
deploy_services() {
    echo "🚀 部署服务..."
    
    # 创建必要的目录
    mkdir -p logs/{nginx,backend,mysql,redis}
    mkdir -p mysql nginx/ssl monitoring/{prometheus,grafana}
    
    # 停止现有服务
    docker-compose -f docker-compose.prod.yml down
    
    # 启动新服务
    docker-compose -f docker-compose.prod.yml up -d
    
    echo "✅ 服务部署完成"
}

# 等待服务启动
wait_for_services() {
    echo "⏳ 等待服务启动..."
    
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -f http://localhost/health > /dev/null 2>&1; then
            echo "✅ 服务启动成功"
            return 0
        fi
        
        echo "尝试 $attempt/$max_attempts - 等待服务启动..."
        sleep 10
        ((attempt++))
    done
    
    echo "❌ 服务启动超时"
    exit 1
}

# 运行健康检查
health_check() {
    echo "🔍 运行健康检查..."
    
    # 检查前端
    if curl -f http://localhost/ > /dev/null 2>&1; then
        echo "✅ 前端服务正常"
    else
        echo "❌ 前端服务异常"
        exit 1
    fi
    
    # 检查后端API
    if curl -f http://localhost/api/health > /dev/null 2>&1; then
        echo "✅ 后端API正常"
    else
        echo "❌ 后端API异常"
        exit 1
    fi
    
    # 检查数据库连接
    if docker-compose -f docker-compose.prod.yml exec -T backend1 python -c "
import asyncio
from database.connection import get_database
async def test():
    db = await get_database()
    await db.execute('SELECT 1')
    print('Database OK')
asyncio.run(test())
" > /dev/null 2>&1; then
        echo "✅ 数据库连接正常"
    else
        echo "❌ 数据库连接异常"
        exit 1
    fi
    
    echo "✅ 健康检查通过"
}

# 清理旧镜像
cleanup() {
    echo "🧹 清理旧镜像..."
    
    # 删除未使用的镜像
    docker image prune -f
    
    # 删除未使用的容器
    docker container prune -f
    
    echo "✅ 清理完成"
}

# 主执行流程
main() {
    check_env_vars
    build_images
    
    if [[ "$ENVIRONMENT" == "production" ]]; then
        push_images
    fi
    
    deploy_services
    wait_for_services
    health_check
    cleanup
    
    echo "🎉 部署完成！"
    echo "前端地址: https://your-domain.com"
    echo "监控地址: http://your-domain.com:3000"
    echo "API文档: https://your-domain.com/api/docs"
}

# 执行主流程
main "$@"
```

### 数据库初始化脚本
```bash
#!/bin/bash
# init-database.sh

set -e

echo "🗄️ 初始化数据库..."

# 等待MySQL启动
wait_for_mysql() {
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if docker-compose -f docker-compose.prod.yml exec -T mysql-master mysql -uroot -p$DB_ROOT_PASSWORD -e "SELECT 1" > /dev/null 2>&1; then
            echo "✅ MySQL已启动"
            return 0
        fi
        
        echo "尝试 $attempt/$max_attempts - 等待MySQL启动..."
        sleep 5
        ((attempt++))
    done
    
    echo "❌ MySQL启动超时"
    exit 1
}

# 创建数据库表
create_tables() {
    echo "📋 创建数据库表..."
    
    docker-compose -f docker-compose.prod.yml exec -T mysql-master mysql -uroot -p$DB_ROOT_PASSWORD city_brain_db < database/schema.sql
    
    echo "✅ 数据库表创建完成"
}

# 导入初始数据
import_initial_data() {
    echo "📥 导入初始数据..."
    
    if [[ -f "database/initial_data.sql" ]]; then
        docker-compose -f docker-compose.prod.yml exec -T mysql-master mysql -uroot -p$DB_ROOT_PASSWORD city_brain_db < database/initial_data.sql
        echo "✅ 初始数据导入完成"
    else
        echo "⚠️ 未找到初始数据文件，跳过导入"
    fi
}

# 配置主从复制
setup_replication() {
    echo "🔄 配置MySQL主从复制..."
    
    # 在主服务器上创建复制用户
    docker-compose -f docker-compose.prod.yml exec -T mysql-master mysql -uroot -p$DB_ROOT_PASSWORD -e "
        CREATE USER IF NOT EXISTS 'replication_user'@'%' IDENTIFIED BY '$REPLICATION_PASSWORD';
        GRANT REPLICATION SLAVE ON *.* TO 'replication_user'@'%';
        FLUSH PRIVILEGES;
    "
    
    # 获取主服务器状态
    MASTER_STATUS=$(docker-compose -f docker-compose.prod.yml exec -T mysql-master mysql -uroot -p$DB_ROOT_PASSWORD -e "SHOW MASTER STATUS\G")
    MASTER_LOG_FILE=$(echo "$MASTER_STATUS" | grep "File:" | awk '{print $2}')
    MASTER_LOG_POS=$(echo "$MASTER_STATUS" | grep "Position:" | awk '{print $2}')
    
    # 配置从服务器
    docker-compose -f docker-compose.prod.yml exec -T mysql-slave mysql -uroot -p$DB_ROOT_PASSWORD -e "
        CHANGE MASTER TO
        MASTER_HOST='mysql-master',
        MASTER_USER='replication_user',
        MASTER_PASSWORD='$REPLICATION_PASSWORD',
        MASTER_LOG_FILE='$MASTER_LOG_FILE',
        MASTER_LOG_POS=$MASTER_LOG_POS;
        START SLAVE;
    "
    
    echo "✅ MySQL主从复制配置完成"
}

# 主执行流程
main() {
    wait_for_mysql
    create_tables
    import_initial_data
    setup_replication
    
    echo "🎉 数据库初始化完成！"
}

main "$@"
```

## 📊 监控配置

### Prometheus配置
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

scrape_configs:
  - job_name: 'city-brain-backend'
    static_configs:
      - targets: ['backend1:9003', 'backend2:9003']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:80']
    metrics_path: '/metrics'

  - job_name: 'mysql'
    static_configs:
      - targets: ['mysql-master:3306', 'mysql-slave:3306']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-master:6379', 'redis-slave:6379']

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

---

*文档版本：v1.0*
*更新时间：2025年9月26日*