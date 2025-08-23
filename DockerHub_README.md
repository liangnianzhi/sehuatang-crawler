# 🚀 色花堂磁力链接爬虫工具 v2.1.0

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![React](https://img.shields.io/badge/React-18.0+-61dafb.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ed.svg)
![License](https://img.shields.io/badge/License-Study%20Only-red.svg)

**功能强大的磁力链接爬虫工具，支持多主题爬取、代理设置、定时任务和实时日志监控**

</div>

---

## 🎯 项目简介

色花堂磁力链接爬虫工具是一个基于Python + React的现代化Web应用，提供强大的磁力链接爬取功能。支持多主题、多模式、代理设置、定时任务等高级功能，让您轻松获取所需的磁力链接。

## ✨ 核心特性

### 🎪 爬取功能
- 🎭 **多主题支持**: 支持亚洲无码、亚洲有码、国产原创等7个主题
- 🔥 **双模式爬取**: 普通模式 + 热门模式，满足不同需求
- 📄 **批量页面爬取**: 支持指定页面范围，高效批量处理
- 📊 **实时进度显示**: 实时显示爬取进度和结果统计

### ⚙️ 高级功能
- 🌐 **代理支持**: 支持HTTP/HTTPS/SOCKS5代理
- 💾 **代理持久化**: 代理设置自动保存，无需重复配置
- ⏰ **定时任务**: 支持每日、每周、间隔执行
- 🔄 **任务管理**: 完整的任务生命周期管理

### 🎨 用户界面
- 🎨 **现代化UI**: 基于React + Ant Design的美观界面
- 📱 **响应式设计**: 完美适配桌面和移动设备
- 🧭 **多页面导航**: 首页和设置页面分离设计
- ⚡ **实时更新**: 任务状态和日志实时更新

## 🚀 快速开始

### 方式一：Docker运行（推荐）

```bash
# 拉取最新镜像
docker pull wyh3210277395/sehuatang-crawler:latest

# 运行容器
docker run -d \
  --name sehuatang-crawler \
  -p 5000:5000 \
  -v ./data:/app/data \
  -v ./logs:/app/logs \
  wyh3210277395/sehuatang-crawler:latest
```

### 方式二：Docker Compose运行

```yaml
# docker-compose.yml
version: '3.8'
services:
  sehuatang-crawler:
    image: wyh3210277395/sehuatang-crawler:latest
    container_name: sehuatang-crawler
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - PYTHONUNBUFFERED=1
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

```bash
# 启动服务
docker-compose up -d
```

### 方式三：指定版本运行

```bash
# 拉取特定版本
docker pull wyh3210277395/sehuatang-crawler:v2.1.0

# 运行容器
docker run -d --name sehuatang-crawler -p 5000:5000 wyh3210277395/sehuatang-crawler:v2.1.0
```

## 🌐 访问应用

启动成功后，打开浏览器访问：
```
http://localhost:5000
```

## 📖 使用指南

### 1️⃣ 基本爬取
1. 访问应用首页
2. 选择要爬取的主题
3. 选择爬取模式（普通/热门）
4. 设置页面范围（普通模式）
5. 配置代理（如需要）
6. 点击"开始爬取"

### 2️⃣ 代理设置
1. 点击左侧"设置"菜单
2. 在代理设置区域启用代理
3. 输入代理地址（格式：`http://host:port` 或 `socks5://host:port`）
4. 点击"保存代理设置"

### 3️⃣ 定时任务
1. 在设置页面点击"新建定时任务"
2. 配置任务名称、主题、模式、页面范围
3. 选择调度类型：
   - **每日执行**: 每天固定时间执行
   - **每周执行**: 每周固定时间执行
   - **间隔执行**: 按指定间隔时间执行
4. 设置执行时间
5. 保存任务

### 4️⃣ 任务监控
- **实时日志**: 首页实时显示操作日志
- **任务列表**: 查看所有爬取任务状态
- **下载结果**: 任务完成后可下载磁力链接文件

## 🏗️ 技术架构

### 后端技术栈
- **Python 3.9+**: 主要开发语言
- **Flask 2.0+**: Web框架
- **Selenium 4.0+**: 网页自动化
- **Chrome/ChromeDriver**: 浏览器引擎
- **BeautifulSoup4**: HTML解析

### 前端技术栈
- **React 18.0+**: 前端框架
- **Ant Design 5.0+**: UI组件库
- **dayjs**: 日期处理

### 容器化技术
- **Docker**: 容器化部署
- **多阶段构建**: 优化镜像大小
- **健康检查**: 自动监控服务状态

## 📊 功能对比

| 功能 | v1.0 | v2.0 | v2.1.0 |
|------|------|------|--------|
| 基础爬取 | ✅ | ✅ | ✅ |
| 多主题支持 | ✅ | ✅ | ✅ |
| 热门模式 | ❌ | ✅ | ✅ |
| 代理支持 | ❌ | ✅ | ✅ |
| 多页面爬取 | ❌ | ✅ | ✅ |
| 定时任务 | ❌ | ❌ | ✅ |
| 设置页面 | ❌ | ❌ | ✅ |
| 实时日志 | ❌ | ❌ | ✅ |

## 🔧 配置说明

### 环境变量
```bash
FLASK_ENV=production          # Flask环境
PYTHONUNBUFFERED=1           # Python输出缓冲
HTTP_PROXY=http://host:port  # HTTP代理
HTTPS_PROXY=http://host:port # HTTPS代理
NO_PROXY=localhost,127.0.0.1 # 不使用代理的地址
```

### 数据卷
```bash
./data:/app/data    # 爬取结果文件
./logs:/app/logs    # 应用日志文件
```

## 📝 更新日志

### v2.1.0 (2024-08-23) 🆕
- ✨ 新增设置页面
- ✨ 新增代理配置持久化
- ✨ 新增定时任务管理
- ✨ 新增实时日志显示
- ✨ 新增多页面导航
- 🔧 优化用户界面
- 🔧 修复下载文件名问题

### v2.0.0 (2024-08-23)
- ✨ 新增代理支持
- ✨ 新增多页面爬取
- ✨ 新增热门模式
- 🔧 移除Nginx依赖
- 🔧 优化Docker构建

### v1.0.0 (2024-08-23)
- 🎉 初始版本发布
- ✨ 基础爬取功能
- ✨ Web界面
- ✨ Docker支持

## 🔒 安全说明

<div align="center">

⚠️ **重要提醒**

</div>

- 🎓 本工具仅供学习和研究使用
- 📜 请遵守当地法律法规
- ⚠️ 使用者需自行承担使用风险
- 🚫 请勿用于商业用途

## 🤝 支持与反馈

如果您在使用过程中遇到问题或有改进建议，欢迎：

- 📧 提交Issue
- 🔄 提交Pull Request
- 💬 参与讨论

## 📄 许可证

本项目仅供学习和研究使用，请遵守相关法律法规。

---

<div align="center">

**享受爬取之旅！** 🚀

Made with ❤️ by [wyh3210277395](https://hub.docker.com/u/wyh3210277395)

</div>
