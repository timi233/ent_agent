# 城市大脑企业信息处理系统端口配置说明

## 端口分配

为了避免与系统中已有的服务冲突，本系统使用以下端口配置：

| 服务 | 端口 | 用途 |
|------|------|------|
| 前端开发服务器 | 9002 | Vue.js开发服务器 |
| 后端API服务 | 9003 | FastAPI后端服务 |

## 端口映射

### Docker部署端口映射

```yaml
# docker-compose.yml
services:
  backend:
    ports:
      - "9003:8000"  # 主机端口:容器端口
      
  frontend:
    ports:
      - "9002:3000"  # 主机端口:容器端口
```

### Vite代理配置

```javascript
// vite.config.js
server: {
  port: 9002,
  proxy: {
    '/api': {
      target: 'http://localhost:9003',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, '')
    }
  }
}
```

## 访问地址

启动成功后，可以通过以下地址访问系统：

- **前端界面**: http://localhost:9002
- **后端API文档**: http://localhost:9003/docs
- **后端健康检查**: http://localhost:9003/api/v1/health

## 端口冲突处理

### 检查端口占用

```bash
# 检查特定端口是否被占用
lsof -i :9002
lsof -i :9003

# 检查多个端口
netstat -tuln | grep -E ":(9002|9003)"
```

### 停止占用端口的进程

```bash
# 停止前端服务
pkill -f "vite"

# 停止后端服务
pkill -f "uvicorn.*9003"

# 强制停止特定PID的进程
kill -9 <PID>
```

### 修改端口配置

如果需要修改端口，需要更新以下文件：

1. **前端配置**:
   - `city_brain_frontend/vite.config.js` - 开发服务器端口和代理配置
   - `city_brain_frontend/docker-compose.yml` - Docker端口映射

2. **后端配置**:
   - `city_brain_system/start.sh` - 启动脚本端口
   - `city_brain_system/Dockerfile` - Docker暴露端口
   - `city_brain_frontend/docker-compose.yml` - Docker端口映射

3. **启动脚本**:
   - `start.sh` - 日常启动脚本
   - `quick_start.sh` - 快速启动脚本
   - `stop.sh` - 停止脚本
   - `start_city_brain.sh` - 完整功能启动脚本

## 防火墙配置

如果需要从外部访问服务，确保防火墙允许相应端口：

```bash
# Ubuntu/Debian
sudo ufw allow 9002
sudo ufw allow 9003

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=9002/tcp
sudo firewall-cmd --permanent --add-port=9003/tcp
sudo firewall-cmd --reload
```

## 故障排除

### 服务无法启动

1. 检查端口是否被占用
2. 检查防火墙设置
3. 查看日志文件:
   - 前端日志: `/home/server/code/city_brain_frontend/frontend.log`
   - 后端日志: `/home/server/code/city_brain_system/backend.log`

### 无法访问服务

1. 检查服务是否正常启动
2. 检查网络连接
3. 验证端口配置是否正确