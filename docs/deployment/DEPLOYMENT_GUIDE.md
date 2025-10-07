# 城市大脑企业信息处理系统部署指南

## 概述

本文档提供了城市大脑企业信息处理系统的完整部署指南，包括前端和后端服务的部署方式。

## 系统要求

### 环境要求
- Node.js 16+
- Python 3.11+
- Docker (可选，用于容器化部署)
- npm 8+

### 硬件要求
- CPU: 2核以上
- 内存: 4GB以上
- 硬盘: 10GB以上可用空间

## 项目结构

```
/home/server/code/
├── city_brain_system/     # 后端服务
└── city_brain_frontend/   # 前端应用
```

## 配置准备

### 1. 环境变量配置

在 `city_brain_system/.env` 文件中配置API密钥：

```env
BOCHA_API_KEY=your_bocha_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

### 2. 数据库配置

确保数据库服务正常运行，并在 `city_brain_system/config/config.ini` 中配置正确的连接信息。

## 部署方式

### 方式一：脚本部署（推荐）

使用提供的部署脚本一键部署：

```bash
# 进入前端项目目录
cd /home/server/code/city_brain_frontend

# 完整部署（安装依赖+启动服务）
./deploy.sh deploy

# 查看服务状态
./deploy.sh status

# 停止所有服务
./deploy.sh stop
```

### 方式二：手动部署

#### 1. 启动后端服务

```bash
# 进入后端项目目录
cd /home/server/code/city_brain_system

# 启动后端服务
uvicorn main:app --host 0.0.0.0 --port 8001
```

#### 2. 启动前端服务

```bash
# 进入前端项目目录
cd /home/server/code/city_brain_frontend

# 安装依赖
npm install

# 启动开发服务器
npm run start
```

### 方式三：Docker部署

#### 1. 构建并启动服务

```bash
# 进入前端项目目录
cd /home/server/code/city_brain_frontend

# 使用docker-compose启动服务
docker-compose up -d
```

#### 2. 查看日志

```bash
# 查看后端服务日志
docker-compose logs backend

# 查看前端服务日志
docker-compose logs frontend
```

#### 3. 停止服务

```bash
# 停止所有服务
docker-compose down
```

## 访问应用

部署完成后，可以通过以下URL访问应用：

- 前端界面: http://localhost:9002
- 后端API文档: http://localhost:9003/docs
- 后端健康检查: http://localhost:9003/api/v1/health

## 服务管理

### 启动服务

```bash
# 使用部署脚本启动
./deploy.sh deploy

# 或分别启动前后端
./deploy.sh start-backend
./deploy.sh start-frontend
```

### 停止服务

```bash
# 使用部署脚本停止
./deploy.sh stop
```

### 查看状态

```bash
# 查看服务状态
./deploy.sh status
```

## 故障排除

### 常见问题

1. **端口被占用**
   - 检查端口占用情况: `lsof -i :9003` 或 `lsof -i :9002`
   - 停止占用进程: `kill -9 <PID>`

2. **API调用失败**
   - 检查后端服务是否正常运行
   - 检查网络连接
   - 验证API密钥是否正确配置

3. **前端页面无法访问**
   - 检查前端服务是否正常启动
   - 检查浏览器控制台错误信息
   - 确认代理配置是否正确

### 日志查看

```bash
# 查看后端日志
tail -f /home/server/code/city_brain_system/server.log

# 查看前端日志
tail -f /home/server/code/city_brain_frontend/frontend.log
```

## 性能优化建议

1. **使用生产构建**
   - 使用 `npm run build` 构建生产版本
   - 使用专业的Web服务器（如Nginx）提供静态文件

2. **启用缓存**
   - 在Nginx中配置静态资源缓存
   - 启用浏览器缓存策略

3. **负载均衡**
   - 对于高并发场景，考虑使用负载均衡器

## 安全建议

1. **API密钥保护**
   - 不要在代码中硬编码API密钥
   - 使用环境变量或密钥管理服务

2. **访问控制**
   - 在生产环境中配置适当的访问控制策略
   - 使用HTTPS加密传输

3. **定期更新**
   - 定期更新依赖包以修复安全漏洞
   - 关注官方安全公告

## 备份与恢复

### 数据备份

```bash
# 备份数据库
mysqldump -h 192.168.101.13 -u City_Brain_user_mysql -p City_Brain_DB > backup.sql
```

### 配置备份

```bash
# 备份配置文件
cp /home/server/code/city_brain_system/config/config.ini config.ini.backup
cp /home/server/code/city_brain_system/.env .env.backup
```

## 监控与维护

### 健康检查

定期检查服务健康状态：

```bash
# 检查后端健康
curl http://localhost:9003/api/v1/health

# 检查前端服务
curl http://localhost:9002
```

### 性能监控

- 监控CPU和内存使用情况
- 监控API响应时间
- 监控数据库性能

## 升级指南

### 版本升级步骤

1. 备份当前配置和数据
2. 停止当前服务
3. 拉取最新代码
4. 安装新依赖
5. 更新配置文件（如有必要）
6. 启动服务
7. 验证功能

```bash
# 升级步骤示例
cd /home/server/code/city_brain_system
git pull
pip install -r requirements.txt

cd /home/server/code/city_brain_frontend
git pull
npm install

# 重启服务
/home/server/code/city_brain_frontend/deploy.sh stop
/home/server/code/city_brain_frontend/deploy.sh deploy
```