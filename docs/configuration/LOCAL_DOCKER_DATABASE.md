# Local Docker Database Setup

本指南说明如何让系统直接连接到本地已经运行的 Docker MySQL 实例，而无需再新建容器。

## 1. 确认已有容器

```bash
# 查看正在运行的 MySQL 容器
docker ps --filter "ancestor=mysql" --format "table {{.ID}}\t{{.Image}}\t{{.Names}}\t{{.Ports}}"
```

记录容器名称（例如 `mysql-prod`）以及端口映射（如 `0.0.0.0:3306->3306/tcp`）。如果宿主机暴露的端口不是 3306，请将其记下用于后续配置。

## 2. 校验连接信息

```bash
# 查询容器实际监听端口
docker inspect -f '{{range .NetworkSettings.Ports}}{{(index . 0).HostIp}}:{{(index . 0).HostPort}}{{end}}' <容器名称>

# 验证是否可以从宿主机连接
mysql -h 127.0.0.1 -P 3306 -u City_Brain_user_mysql -pCityBrain@2024 City_Brain_DB -e "SHOW TABLES;"
```

如需导入项目提供的结构/样例数据，可执行：

```bash
mysql -h 127.0.0.1 -P 3306 -u City_Brain_user_mysql -pCityBrain@2024 < scripts/init_database.sql
```

## 3. 配置后端环境变量

在 `city_brain_system_refactored/.env` 或系统环境变量中对照端口进行设置（以下示例假设宿主机端口为 3306）：

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USERNAME=City_Brain_user_mysql
DB_PASSWORD=CityBrain@2024
DB_DATABASE=City_Brain_DB
```

若容器未映射到宿主机，可使用 `host.docker.internal` 或容器内部网络地址（`docker inspect <容器名称> | grep IPAddress`）并相应调整 `DB_HOST`。

更新配置后重启 FastAPI 服务，系统即可直接从该 Docker MySQL 实例读取数据。

## 4. 常见排查步骤

- 检查容器状态：`docker ps | grep mysql`
- 查看容器日志：`docker logs <容器名称>`
- 确认端口未被占用：`lsof -i :3306`
- 重新导入基础数据：`mysql ... < scripts/init_database.sql`

通过以上步骤即可让后端复用现有的 Docker MySQL 数据源进行开发与调试。
