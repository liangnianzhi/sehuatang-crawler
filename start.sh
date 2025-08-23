#!/bin/bash

# 色花堂磁力链接爬虫工具启动脚本

echo "=========================================="
echo "色花堂磁力链接爬虫工具"
echo "=========================================="

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p data logs

# 构建并启动服务
echo "🔨 构建Docker镜像..."
docker-compose build

if [ $? -eq 0 ]; then
    echo "✅ 构建成功"
else
    echo "❌ 构建失败"
    exit 1
fi

echo "🚀 启动服务..."
docker-compose up -d

if [ $? -eq 0 ]; then
    echo "✅ 服务启动成功"
    echo ""
    echo "🌐 访问地址: http://localhost:5000"
    echo "📊 健康检查: http://localhost:5000/api/health"
    echo ""
    echo "📋 常用命令:"
    echo "  查看日志: docker-compose logs -f"
    echo "  停止服务: docker-compose down"
    echo "  重启服务: docker-compose restart"
    echo ""
    echo "🎉 应用已启动，请在浏览器中访问上述地址"
else
    echo "❌ 服务启动失败"
    exit 1
fi

