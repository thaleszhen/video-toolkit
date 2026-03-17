#!/bin/bash

# video-toolkit 快速安装脚本

echo "🚀 开始安装 video-toolkit..."

# 1. 构建项目
echo "📦 构建项目..."
npm run build

# 2. 全局链接
echo "🔗 创建全局链接..."
npm link

# 3. 验证安装
echo "✅ 验证安装..."
video-toolkit --version

echo ""
echo "🎉 安装完成！"
echo ""
echo "现在可以使用以下命令："
echo "  video-toolkit --help"
echo "  video-toolkit module list"
echo "  video-toolkit workflow youtube --help"
