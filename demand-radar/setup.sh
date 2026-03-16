#!/bin/bash

# Demand Radar 快速启动脚本

echo "🚀 Demand Radar - 需求挖掘平台"
echo "=============================="
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3，请先安装 Python 3.10+"
    exit 1
fi

# 检查 Node (可选，用于完整前端)
if ! command -v npm &> /dev/null; then
    echo "⚠️  未找到 npm，将使用简化版 HTML 前端"
fi

echo "📦 安装后端依赖..."
cd backend
pip3 install -r requirements.txt

# 复制环境配置
if [ ! -f .env ]; then
    echo "📝 创建环境配置文件..."
    cp .env.example .env
    echo "⚠️  请编辑 backend/.env 文件，添加你的 API Keys"
fi

echo ""
echo "✅ 安装完成！"
echo ""
echo "🎯 快速开始："
echo ""
echo "1. 启动后端 API:"
echo "   cd backend && python3 -m app.main"
echo ""
echo "2. 在浏览器打开前端:"
echo "   file://$(pwd)/../frontend/index.html"
echo ""
echo "3. 运行 Hacker News 采集器:"
echo "   cd ../scrapers && python3 hn_scraper.py"
echo ""
echo "🐳 使用 Docker 一键启动:"
echo "   docker-compose up"
echo ""
echo "📚 更多信息请查看 README.md"
