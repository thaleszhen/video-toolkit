#!/bin/bash

# video-toolkit 功能演示脚本

echo "🎬 video-toolkit 功能演示"
echo "============================"
echo ""

echo "1️⃣  查看版本"
echo "----------------------------------------"
video-toolkit --version
echo ""

echo "2️⃣  查看帮助"
echo "----------------------------------------"
video-toolkit --help
echo ""

echo "3️⃣  列出所有模块"
echo "----------------------------------------"
video-toolkit module list
echo ""

echo "4️⃣  查看视频类模块"
echo "----------------------------------------"
video-toolkit module list --category video
echo ""

echo "5️⃣  查看 trim 模块详情"
echo "----------------------------------------"
video-toolkit module info trim
echo ""

echo "6️⃣  查看 compress 模块详情"
echo "----------------------------------------"
video-toolkit module info compress
echo ""

echo "7️⃣  验证 YouTube 工作流（干运行）"
echo "----------------------------------------"
echo "命令: video-toolkit workflow youtube --dry-run"
video-toolkit workflow youtube --dry-run
echo ""

echo "8️⃣  验证 TikTok 工作流（干运行）"
echo "----------------------------------------"
echo "命令: video-toolkit workflow tiktok --dry-run"
video-toolkit workflow tiktok --dry-run
echo ""

echo "✅ 演示完成！"
echo ""
echo "📖 接下来你可以："
echo "  1. 准备一个测试视频文件"
echo "  2. 运行: video-toolkit workflow youtube -i your-video.mp4 -o output.mp4"
echo "  3. 查看教程: cat TUTORIAL.md"
echo ""
