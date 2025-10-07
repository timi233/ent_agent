# MySQL数据库安装指南

## 一键安装脚本

已为你准备好完整的MySQL数据库安装脚本，只需一条命令即可完成所有配置。

### 快速开始

```bash
# 进入脚本目录
cd /home/jian/code/code/scripts

# 执行安装脚本（需要sudo权限）
sudo bash setup_mysql.sh
```

### 安装脚本会自动完成以下操作：

1. ✅ 更新软件包列表
2. ✅ 安装MySQL服务器
3. ✅ 启动并配置MySQL服务开机自启
4. ✅ 创建数据库 `City_Brain_DB`
5. ✅ 创建用户 `City_Brain_user_mysql`（密码：`CityBrain@2024`）
6. ✅ 导入数据库结构（7个核心表）
7. ✅ 插入示例数据
   - 7个地区（青岛各区）
   - 13个行业分类
   - 6个产业大脑
   - 5个链主企业
   - 10个客户企业
8. ✅ 自动更新项目配置文件（`.env`）
9. ✅ 配置MySQL允许远程连接
10. ✅ 测试数据库连接

### 数据库连接信息

安装完成后，数据库信息如下：

```
主机: localhost
端口: 3306
数据库: City_Brain_DB
用户名: City_Brain_user_mysql
密码: CityBrain@2024
```

### 数据库表结构

| 表名 | 说明 | 示例记录数 |
|------|------|-----------|
| QD_area | 地区信息表 | 7 |
| QD_industry | 行业信息表 | 13 |
| QD_industry_brain | 产业大脑表 | 6 |
| QD_enterprise_chain_leader | 链主企业表 | 5 |
| QD_customer | 客户企业表 | 10 |
| QD_brain_industry_rel | 产业大脑行业关联表 | 7 |
| company_cache | 企业信息缓存表 | 0 |

### 验证安装

安装完成后，可以通过以下方式验证：

#### 1. 使用MySQL命令行
```bash
mysql -u City_Brain_user_mysql -pCityBrain@2024 City_Brain_DB

# 查看所有表
SHOW TABLES;

# 查看客户企业数据
SELECT * FROM QD_customer;

# 使用视图查询完整信息
SELECT * FROM v_customer_full_info;
```

#### 2. 使用Python测试连接
```bash
cd /home/jian/code/code/city_brain_system_refactored

# 测试数据库连接
python3 -c "
from infrastructure.database.connection import test_connection
result = test_connection()
print('数据库连接:', '成功' if result else '失败')
"
```

#### 3. 启动系统测试
```bash
# 启动重构后的后端
cd /home/jian/code/code
./start_refactored_backend.sh

# 测试健康检查接口
curl http://localhost:9003/api/v1/health

# 测试企业查询
curl -X POST http://localhost:9003/api/v1/company/process \
  -H "Content-Type: application/json" \
  -d '{"input_text": "查询海尔集团"}'
```

### 故障排除

#### 问题1: MySQL服务无法启动

```bash
# 查看MySQL状态
sudo systemctl status mysql

# 查看错误日志
sudo tail -f /var/log/mysql/error.log

# 重启MySQL
sudo systemctl restart mysql
```

#### 问题2: 数据库连接失败

```bash
# 检查用户权限
sudo mysql -u root -e "SELECT user, host FROM mysql.user WHERE user='City_Brain_user_mysql';"

# 重新授权
sudo mysql -u root <<EOF
GRANT ALL PRIVILEGES ON City_Brain_DB.* TO 'City_Brain_user_mysql'@'localhost';
FLUSH PRIVILEGES;
EOF
```

#### 问题3: 端口被占用

```bash
# 检查3306端口
sudo netstat -tulnp | grep 3306

# 或使用lsof
sudo lsof -i :3306
```

#### 问题4: 配置文件未更新

```bash
# 手动更新配置文件
nano /home/jian/code/code/city_brain_system_refactored/.env

# 修改以下内容：
DB_HOST=localhost
DB_PORT=3306
DB_USERNAME=City_Brain_user_mysql
DB_PASSWORD=CityBrain@2024
DB_DATABASE=City_Brain_DB
```

### 安全建议

1. **修改默认密码**
   ```bash
   sudo mysql -u root
   ALTER USER 'City_Brain_user_mysql'@'localhost' IDENTIFIED BY '你的新密码';
   FLUSH PRIVILEGES;
   ```

2. **配置防火墙**（如果需要远程访问）
   ```bash
   sudo ufw allow 3306/tcp
   ```

3. **定期备份数据库**
   ```bash
   # 备份数据库
   mysqldump -u City_Brain_user_mysql -pCityBrain@2024 City_Brain_DB > backup_$(date +%Y%m%d).sql

   # 恢复数据库
   mysql -u City_Brain_user_mysql -pCityBrain@2024 City_Brain_DB < backup_20251001.sql
   ```

### 手动安装步骤（可选）

如果自动脚本失败，可以按以下步骤手动安装：

```bash
# 1. 安装MySQL
sudo apt update
sudo apt install -y mysql-server

# 2. 启动服务
sudo systemctl start mysql
sudo systemctl enable mysql

# 3. 登录MySQL（root无密码）
sudo mysql

# 4. 在MySQL命令行中执行
CREATE DATABASE City_Brain_DB DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'City_Brain_user_mysql'@'localhost' IDENTIFIED BY 'CityBrain@2024';
GRANT ALL PRIVILEGES ON City_Brain_DB.* TO 'City_Brain_user_mysql'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# 5. 导入数据库结构
mysql -u City_Brain_user_mysql -pCityBrain@2024 City_Brain_DB < /home/jian/code/code/scripts/init_database.sql

# 6. 验证
mysql -u City_Brain_user_mysql -pCityBrain@2024 City_Brain_DB -e "SHOW TABLES;"
```

### 下一步

数据库安装完成后：

1. ✅ 检查配置文件：`city_brain_system_refactored/.env`
2. ✅ 启动后端服务：`./start_refactored_backend.sh`
3. ✅ 启动前端服务：`cd city_brain_frontend && npm run start`
4. ✅ 访问系统：http://localhost:9002

---

**创建时间**: 2025-10-01
**版本**: 1.0
**维护人**: Claude Code
