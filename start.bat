@echo off
chcp 65001 >nul

echo ==========================================
echo 色花堂磁力链接爬虫工具
echo ==========================================

REM 检查Docker是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker未安装，请先安装Docker Desktop
    pause
    exit /b 1
)

REM 检查Docker Compose是否安装
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose未安装，请先安装Docker Compose
    pause
    exit /b 1
)

REM 创建必要的目录
echo 📁 创建必要的目录...
if not exist "data" mkdir data
if not exist "logs" mkdir logs

REM 构建并启动服务
echo 🔨 构建Docker镜像...
docker-compose build

if errorlevel 1 (
    echo ❌ 构建失败
    pause
    exit /b 1
) else (
    echo ✅ 构建成功
)

echo 🚀 启动服务...
docker-compose up -d

if errorlevel 1 (
    echo ❌ 服务启动失败
    pause
    exit /b 1
) else (
    echo ✅ 服务启动成功
    echo.
    echo 🌐 访问地址: http://localhost:5000
    echo 📊 健康检查: http://localhost:5000/api/health
    echo.
    echo 📋 常用命令:
    echo   查看日志: docker-compose logs -f
    echo   停止服务: docker-compose down
    echo   重启服务: docker-compose restart
    echo.
    echo 🎉 应用已启动，请在浏览器中访问上述地址
)

pause
