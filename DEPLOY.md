# 部署指南

## 🚀 快速部署

### 1. 环境要求

- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **操作系统**: Linux, macOS, Windows 10+

### 2. 一键部署

#### Linux/macOS
```bash
# 克隆项目
git clone <repository-url>
cd sehuatang-crawler

# 给启动脚本执行权限
chmod +x start.sh

# 一键启动
./start.sh
```

#### Windows
```cmd
# 克隆项目
git clone <repository-url>
cd sehuatang-crawler

# 一键启动
start.bat
```

### 3. 手动部署

```bash
# 1. 创建目录
mkdir -p data logs

# 2. 构建镜像
docker-compose build

# 3. 启动服务
docker-compose up -d

# 4. 查看状态
docker-compose ps

# 5. 查看日志
docker-compose logs -f
```

## 🔧 配置说明

### 环境变量

在 `docker-compose.yml` 中可以配置以下环境变量：

```yaml
environment:
  - FLASK_ENV=production          # Flask环境
  - PYTHONUNBUFFERED=1           # Python输出缓冲
  - MAX_WORKERS=3                # 最大并发任务数
  - TASK_TIMEOUT=3600            # 任务超时时间（秒）
```

### 端口配置

默认端口为5000，如需修改：

```yaml
ports:
  - "8080:5000"  # 将外部端口改为8080
```

### 数据持久化

```yaml
volumes:
  - ./data:/app/data    # 数据目录
  - ./logs:/app/logs    # 日志目录
```

## 📊 监控和维护

### 健康检查

```bash
# 检查服务状态
curl http://localhost:5000/api/health

# 查看容器状态
docker-compose ps

# 查看资源使用
docker stats
```

### 日志管理

```bash
# 查看实时日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f sehuatang-crawler

# 查看错误日志
docker-compose logs --tail=100 | grep ERROR
```

### 备份和恢复

```bash
# 备份数据
tar -czf backup_$(date +%Y%m%d).tar.gz data/

# 恢复数据
tar -xzf backup_20241201.tar.gz
```

## 🔒 安全配置

### 1. 防火墙设置

```bash
# 只允许特定IP访问
iptables -A INPUT -p tcp --dport 5000 -s 192.168.1.0/24 -j ACCEPT
iptables -A INPUT -p tcp --dport 5000 -j DROP
```

### 2. 反向代理（推荐）

使用Nginx作为反向代理：

```bash
# 启动带Nginx的完整服务
docker-compose --profile nginx up -d
```

### 3. SSL证书

```bash
# 生成自签名证书
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem -out ssl/cert.pem

# 启动HTTPS服务
docker-compose --profile nginx up -d
```

## 🐛 故障排除

### 常见问题

1. **端口被占用**
```bash
# 查看端口占用
lsof -i :5000

# 停止占用进程
sudo kill -9 <PID>
```

2. **Docker权限问题**
```bash
# 添加用户到docker组
sudo usermod -aG docker $USER

# 重新登录或重启
sudo systemctl restart docker
```

3. **内存不足**
```bash
# 增加Docker内存限制
# 在Docker Desktop设置中调整内存限制
```

4. **Chrome启动失败**
```bash
# 检查Chrome安装
docker-compose exec sehuatang-crawler google-chrome --version

# 重新构建镜像
docker-compose build --no-cache
```

### 性能优化

1. **增加并发数**
```yaml
environment:
  - MAX_WORKERS=5
```

2. **调整内存限制**
```yaml
deploy:
  resources:
    limits:
      memory: 2G
    reservations:
      memory: 1G
```

3. **使用SSD存储**
```yaml
volumes:
  - /ssd/data:/app/data
```

## 📈 扩展部署

### 多实例部署

```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  sehuatang-crawler:
    scale: 3
    deploy:
      replicas: 3
```

### 负载均衡

```bash
# 使用Nginx负载均衡
upstream backend {
    server sehuatang-crawler_1:5000;
    server sehuatang-crawler_2:5000;
    server sehuatang-crawler_3:5000;
}
```

### 数据库集成

```yaml
# 添加PostgreSQL
services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: sehuatang
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

## 🔄 更新部署

```bash
# 1. 拉取最新代码
git pull

# 2. 重新构建
docker-compose build

# 3. 重启服务
docker-compose down
docker-compose up -d

# 4. 验证更新
curl http://localhost:5000/api/health
```

## 📞 技术支持

如遇到问题，请：

1. 查看日志：`docker-compose logs -f`
2. 检查状态：`docker-compose ps`
3. 提交Issue并提供错误信息
4. 联系技术支持

---

**注意**: 请确保在生产环境中配置适当的安全措施，包括防火墙、SSL证书和访问控制。
