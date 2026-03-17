#!/bin/bash

# 创建测试视频脚本

echo "🎬 创建测试视频..."

# 创建 10 秒的测试视频（彩色条纹 + 音频）
ffmpeg -f lavfi -i testsrc=duration=10:size=1920x1080:rate=30 \
  -f lavfi -i sine=frequency=1000:duration=10 \
  -pix_fmt yuv420p \
  -y \
  test-video.mp4 2>&1 | tail -5

if [ -f test-video.mp4 ]; then
  echo ""
  echo "✅ 测试视频创建成功: test-video.mp4"
  echo ""
  echo "📊 视频信息:"
  ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 test-video.mp4 2>&1
  echo ""
  echo "🎯 现在可以运行："
  echo ""
  echo "  # 测试 YouTube 工作流"
  echo "  video-toolkit workflow youtube -i test-video.mp4 -o youtube-output.mp4"
  echo ""
  echo "  # 测试 TikTok 工作流"
  echo "  video-toolkit workflow tiktok -i test-video.mp4 -o tiktok-output.mp4"
  echo ""
  echo "  # 测试单个模块"
  echo "  video-toolkit run --module trim -i test-video.mp4 -o trimmed.mp4 --params '{\"duration\":5}'"
  echo ""
else
  echo "❌ 创建失败"
fi
