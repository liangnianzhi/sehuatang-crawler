# Sehuatang 爬虫系统 v3.0.0

[![Docker Hub](https://img.shields.io/badge/Docker%20Hub-wyh3210277395%2Fsehuatang--crawler-blue)](https://hub.docker.com/r/wyh3210277395/sehuatang-crawler)
[![Telegram](https://img.shields.io/badge/Telegram-群组-blue)](https://t.me/sehuangtangcrawler)

一个专为影视爱好者设计的磁力链接爬取、管理和推送工具，支持自动推送到下载器，配合MDC刮削和Emby影视库建立完整的自动化工作流。

## 🎯 使用场景

### 📺 完整工作流程
1. **自动爬取** → 定时爬取最新磁力链接
2. **智能筛选** → 在数据总览中筛选喜欢的番号
3. **一键推送** → 批量推送到下载器（qBittorrent等）
4. **自动刮削** → 利用用MDC等项目监控下载目录进行元数据刮削
5. **影视库建立** → 在Emby中建立完整的影视库

### 🔄 典型使用场景

**场景一：日常追新**
- 设置定时任务，每天自动爬取最新内容
- 在数据总览中快速筛选喜欢的番号
- 一键推送到下载器开始下载
- 下载完成后利用mdc等刮削器自动刮削并添加到Emby

**场景二：批量收藏**
- 使用强大的筛选功能找出特定演员或系列作品
- 批量选择并推送到下载器
- 统一管理下载进度和元数据

**场景三：补全收藏**
- 搜索特定番号或关键词
- 筛选出高质量的资源
- 批量推送下载并刮削

**场景四：云端下载（计划中）**
- 直接推送到115网盘进行离线下载
- 无需本地下载器，节省带宽和存储
- 支持批量推送和定时推送

**场景五：智能推送（计划中）**
- 设置定时推送规则，自动推送符合条件的磁力链接
- 基于用户偏好智能推荐内容
- 多种通知方式及时提醒

## 🎉 核心功能

### 📊 智能爬虫系统
- **多线程爬取**：支持并发控制，提高爬取效率
- **代理支持**：内置代理配置，确保稳定访问
- **智能重试**：自动处理网络异常和重试机制
- **实时监控**：实时查看爬虫状态和日志

### 🔍 强大的数据筛选
- **多维度筛选**：按番号、演员、大小、日期、分类等条件筛选
- **高级搜索**：支持关键词搜索、正则表达式匹配
- **智能排序**：按大小、日期、热度等多种方式排序
- **标签系统**：支持自定义标签分类管理

### 🔗 磁力链接推送
- **一键推送**：在数据总览中直接点击推送到下载器
- **批量推送**：支持批量选择磁力链接推送到下载器
- **推送历史**：记录推送历史，避免重复推送
- **下载器管理**：支持qBittorrent、Transmission、Aria2等多种下载器
- **云端下载**：支持推送到115网盘等云端下载服务（计划中）
- **定时推送**：设置定时规则自动推送符合条件的磁力链接（计划中）

### 📋 批量操作功能
- **批量复制**：一键复制多个磁力链接到剪贴板
- **批量删除**：支持批量删除不需要的数据
- **批量导出**：导出筛选结果到文件
- **批量推送**：批量推送到下载器

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
services:
  sehuatang-app:
    image: wyh3210277395/sehuatang-crawler:latest
    container_name: sehuatang-app
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      # 数据库配置
      - DATABASE_HOST=postgres
      - DATABASE_PORT=5432
      - DATABASE_NAME=sehuatang_db
      - DATABASE_USER=postgres
      - DATABASE_PASSWORD=sehuatang123
      
      # 应用配置
      - APP_HOST=0.0.0.0
      - APP_PORT=8000
      - APP_RELOAD=false
      - DEBUG=false
      
      # 代理配置 - 支持多种格式
      # 可以通过环境变量覆盖，例如：
      # docker-compose up -e HTTP_PROXY=http://your-proxy:port
      - HTTP_PROXY=${HTTP_PROXY:-}
      - HTTPS_PROXY=${HTTPS_PROXY:-}
      - http_proxy=${http_proxy:-}
      - https_proxy=${https_proxy:-}
      - NO_PROXY=${NO_PROXY:-localhost,127.0.0.1,postgres,192.168.0.0/16,10.0.0.0/8,172.16.0.0/12}
      
    volumes:
      # 数据持久化
      - ./data:/app/data
      - ./logs:/app/logs
      
    depends_on:
      - postgres
      
    networks:
      - sehuatang-network

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
    networks:
      - sehuatang-network

volumes:
  postgres_data:

networks:
  sehuatang-network:
    driver: bridge
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
- **磁力链接列表**：显示所有爬取的磁力链接，包含番号、演员、大小等信息
- **高级筛选**：按番号、演员、大小、日期、分类等条件筛选
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
- **定时推送**：设置定时推送规则，自动推送符合条件的磁力链接（计划中）
- **智能调度**：基于下载器状态和网络状况智能调整推送时间（计划中）

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

**推送失败**
- 检查下载器连接配置
- 确认下载器服务正常运行
- 查看推送日志

## 📞 技术支持

- **Telegram群组**：[@sehuangtangcrawler](https://t.me/sehuangtangcrawler)
- **Docker Hub**：[镜像地址](https://hub.docker.com/r/wyh3210277395/sehuatang-crawler)
- **GitHub Issues**：[提交问题](https://github.com/wyh3210277395/sehuatang-crawler/issues)

## 🔄 更新日志

### v3.0.0 (2024-08-29)

- 🚀 前后端合一部署
- 📊 实时监控和日志
- 🔧 智能代理配置
- 📋 数据管理和操作
- ⏰ 定时任务系统
- 🔗 磁力链接推送功能
- 🔍 强大的数据筛选功能

### 🚧 未来版本规划

#### v3.1.0 (计划中)
- ☁️ **115离线下载支持**：直接推送到115网盘进行离线下载
- ⏰ **定时推送功能**：设置定时任务自动推送磁力链接到下载器
- 📱 **移动端APP**：原生移动端应用，随时随地管理
- 🔔 **推送通知**：微信、Telegram、邮件等多种通知方式

#### v3.2.0 (计划中)
- 🎯 **智能推荐**：基于用户偏好推荐相关内容
- 📊 **数据分析**：详细的下载统计和趋势分析
- 🔄 **自动同步**：与多个下载器自动同步状态
- 🌐 **多站点支持**：支持更多磁力链接站点

#### v3.3.0 (计划中)
- 🤖 **AI智能筛选**：AI辅助内容筛选和分类
- 📋 **收藏夹功能**：个人收藏夹和分享功能
- 🔗 **API开放**：提供完整的API接口供第三方调用
- 🎨 **主题市场**：多种UI主题可选

---

**Sehuatang 爬虫系统** - 让影视资源管理更简单、更高效！

⭐ 如果这个项目对你有帮助，请给我们一个Star！
