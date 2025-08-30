# Sehuatang 爬虫系统 v3.0.0

[![Docker Hub](https://img.shields.io/badge/Docker%20Hub-wyh3210277395%2Fsehuatang--crawler-blue)](https://hub.docker.com/r/wyh3210277395/sehuatang-crawler)
[![Telegram](https://img.shields.io/badge/Telegram-群组-blue)](https://t.me/sehuangtangcrawler)

一个强大的磁力链接爬取、管理和推送工具，支持自动推送到下载器，具备强大的数据筛选和批量操作功能，专为NAS环境优化。

## 🎉 主要功能

### 📊 智能爬虫系统
- **多线程爬取**：支持并发控制，提高爬取效率
- **代理支持**：内置代理配置，确保稳定访问
- **智能重试**：自动处理网络异常和重试机制
- **实时监控**：实时查看爬虫状态和日志

### 🔗 磁力链接推送
- **自动推送**：爬取完成后在数据总揽展示对应的番号女优图片等信息
- **批量推送**：支持批量选择磁力链接推送到下载器
- **推送历史**：记录推送历史，避免重复推送
- **下载器管理**：支持多种下载器配置和管理

### 🔍 强大的数据筛选
- **多维度筛选**：按标题、大小、日期、分类等条件筛选
- **高级搜索**：支持关键词搜索、正则表达式匹配
- **智能排序**：按大小、日期、热度等多种方式排序
- **标签系统**：支持自定义标签分类管理

### 📋 批量操作功能
- **批量复制**：一键复制多个磁力链接到剪贴板
- **批量删除**：支持批量删除不需要的数据
- **批量导出**：导出筛选结果到文件
- **批量推送**：批量推送到下载器

### 📊 数据总览分析
- **实时统计**：显示总数据量、今日新增、热门分类等
- **趋势分析**：数据增长趋势图表
- **分类统计**：各分类数据分布统计
- **大小分析**：文件大小分布统计

### ⏰ 定时任务系统
- **定时爬取**：设置定时任务自动爬取新内容
- **智能调度**：支持多种时间间隔（小时、天、周）
- **任务监控**：实时查看任务执行状态和结果
- **失败重试**：自动重试失败的任务

### 🎨 现代化界面
- **苹果风格UI**：现代化的设计语言，支持主题切换
- **响应式布局**：完美适配桌面和移动设备
- **实时交互**：流畅的动画效果和用户反馈

## 🚀 快速部署

### Docker部署（推荐）

```bash
# 1. 拉取镜像
docker pull wyh3210277395/sehuatang-crawler:latest

# 2. 创建docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  sehuatang-app:
    image: wyh3210277395/sehuatang-crawler:latest
    container_name: sehuatang-app
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - DATABASE_HOST=postgres
      - DATABASE_PORT=5432
      - DATABASE_NAME=sehuatang_db
      - DATABASE_USER=postgres
      - DATABASE_PASSWORD=sehuatang123
      - APP_HOST=0.0.0.0
      - APP_PORT=8000
      - APP_RELOAD=false
      - DEBUG=false
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - postgres

  postgres:
    image: postgres:15-alpine
    container_name: sehuatang-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_DB=sehuatang_db
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=sehuatang123
      - POSTGRES_INITDB_ARGS=--encoding=UTF8 --lc-collate=C --lc-ctype=C
      - LANG=C.UTF-8
      - LC_ALL=C.UTF-8
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
EOF

# 3. 启动服务
docker-compose up -d

# 4. 访问应用
echo "应用已启动，访问地址: http://localhost:8000"
```

## 🌐 访问地址

- **应用界面**：http://localhost:8000
- **API文档**：http://localhost:8000/docs

## 📋 系统要求

- **Docker**：20.10+
- **Docker Compose**：2.0+
- **内存**：至少2GB
- **存储**：至少10GB

## 🛠️ 常用命令

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f sehuatang-app

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 更新镜像
docker-compose pull && docker-compose up -d
```

## 📊 功能模块

### 🏠 仪表板
- **数据统计**：总数据量、今日新增、热门分类统计
- **实时监控**：爬虫状态、系统性能、网络连接状态
- **快速操作**：一键启动爬虫、查看最新数据

### 🕷️ 爬虫管理
- **爬虫控制**：启动/停止爬虫，设置并发数量
- **实时日志**：查看爬虫运行日志，监控爬取进度
- **代理配置**：设置代理服务器，确保稳定访问
- **Cookies管理**：自动收集和管理网站Cookies

### 📋 数据总览
- **磁力链接列表**：显示所有爬取的磁力链接
- **高级筛选**：按标题、大小、日期、分类等条件筛选
- **批量操作**：批量复制、删除、推送磁力链接
- **搜索功能**：关键词搜索、正则表达式匹配

### ⚙️ 系统设置
- **下载器配置**：配置qBittorrent等下载器连接
- **代理设置**：配置HTTP代理服务器
- **推送设置**：设置自动推送规则和条件
- **系统日志**：查看系统运行日志和错误信息

### ⏰ 定时任务
- **任务创建**：创建定时爬取任务
- **调度配置**：设置执行时间和频率
- **任务监控**：查看任务执行状态和历史
- **失败处理**：配置失败重试和通知机制

## 🔒 安全建议

1. **修改默认密码**：更改数据库和应用默认密码
2. **配置反向代理**：使用Nginx等反向代理
3. **启用SSL**：配置HTTPS证书
4. **定期备份**：设置自动备份策略

## 🐛 常见问题

**容器启动失败**
```bash
docker-compose logs sehuatang-app
```

**数据库连接失败**
```bash
docker-compose logs postgres
```

**爬虫无法启动**
- 检查代理配置
- 检查网络连接
- 查看爬虫日志

## 📞 技术支持

- **Telegram群组**：[@sehuangtangcrawler](https://t.me/sehuangtangcrawler)
- **Docker Hub**：[镜像地址](https://hub.docker.com/r/wyh3210277395/sehuatang-crawler)
- **GitHub Issues**：[提交问题](https://github.com/wyh3210277395/sehuatang-crawler/issues)

## 🔄 更新日志

### v3.0.0 (2024-08-29)
- 🎉 首次发布
- 🎨 苹果风格UI设计
- 🚀 前后端合一部署
- 📊 实时监控和日志
- 🔧 智能代理配置
- 📋 数据管理和操作
- ⏰ 定时任务系统

---

**Sehuatang 爬虫系统** - 让数据获取更简单、更高效！

⭐ 如果这个项目对你有帮助，请给我们一个Star！
