# 城市大脑企业信息处理系统启动指南

## 系统启动脚本说明

本项目提供了多个启动脚本来方便地启动和管理城市大脑企业信息处理系统。

### 脚本列表

1. **start.sh** - 日常使用的一键启动脚本（推荐）
2. **stop.sh** - 停止所有服务的脚本
3. **quick_start.sh** - 快速启动脚本（会自动安装依赖）
4. **start_city_brain.sh** - 完整功能的启动脚本

## 使用方法

### 1. 日常启动（推荐）

```bash
# 启动系统
./start.sh

# 停止系统
./stop.sh
```

### 2. 首次启动（需要安装依赖）

```bash
# 首次启动，会自动安装依赖
./quick_start.sh

# 停止系统
./stop.sh
```

### 3. 完整功能启动

```bash
# 查看帮助
./start_city_brain.sh help

# 启动系统
./start_city_brain.sh start

# 查看状态
./start_city_brain.sh status

# 重启系统
./start_city_brain.sh restart

# 停止系统
./start_city_brain.sh stop
```

## 访问地址

启动成功后，可以通过以下地址访问系统：

- **前端界面**: http://localhost:9002
- **后端API文档**: http://localhost:9003/docs
- **后端健康检查**: http://localhost:9003/api/v1/health

## 日志文件

系统运行时会产生日志文件，便于排查问题：

- **前端日志**: `/home/server/code/city_brain_frontend/frontend.log`
- **后端日志**: `/home/server/code/city_brain_system/backend.log`

## 注意事项

1. 确保端口9000和9001未被其他程序占用
2. 首次运行时可能需要一些时间来安装依赖
3. 如果启动失败，请检查日志文件以获取详细信息
4. 建议在稳定的网络环境下首次启动，以便正确下载依赖

## 故障排除

### 端口被占用

如果提示端口被占用，可以手动停止占用端口的进程：

```bash
# 查看占用端口的进程
lsof -i :9000
lsof -i :9001

# 停止进程（将<PID>替换为实际的进程ID）
kill -9 <PID>
```

### 依赖安装失败

如果依赖安装失败，请检查网络连接并手动安装：

```bash
# 后端依赖
cd /home/server/code/city_brain_system
pip install -r requirements.txt

# 前端依赖
cd /home/server/code/city_brain_frontend
npm install
```

### 服务无法访问

如果服务无法访问，请检查：

1. 服务是否正常启动
2. 防火墙设置
3. 系统资源是否充足