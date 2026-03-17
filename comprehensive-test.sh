#!/bin/bash

# video-toolkit 综合测试脚本
# 测试各种实际使用场景

echo "🎬 video-toolkit 综合测试"
echo "================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试计数器
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 测试函数
run_test() {
    local test_name="$1"
    local command="$2"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -e "${BLUE}测试 $TOTAL_TESTS: $test_name${NC}"
    echo "命令: $command"
    echo ""

    if eval "$command" > /tmp/test-output.log 2>&1; then
        echo -e "${GREEN}✅ 通过${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${YELLOW}❌ 失败${NC}"
        cat /tmp/test-output.log
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    echo ""
    echo "----------------------------------------"
    echo ""
}

# 准备测试视频
echo "📦 准备测试素材..."
echo ""

# 创建不同尺寸的测试视频
echo "创建测试视频..."
ffmpeg -f lavfi -i testsrc=duration=30:size=1920x1080:rate=30 \
  -f lavfi -i sine=frequency=1000:duration=30 \
  -pix_fmt yuv420p -y test-30s.mp4 2>&1 | grep -E "(frame|time|size)" | tail -3

echo ""
echo "✅ 测试视频准备完成: test-30s.mp4 (30秒)"
echo ""
echo "================================"
echo ""

# 场景 1: 基础裁剪测试
echo "📍 场景 1: 基础裁剪功能"
echo ""

run_test "裁剪前 10 秒" \
  "video-toolkit run --module trim --input test-30s.mp4 --output test-trim-10s.mp4 --params '{\"duration\":10,\"start\":0}'"

run_test "裁剪中间 10 秒 (10-20秒)" \
  "video-toolkit run --module trim --input test-30s.mp4 --output test-trim-mid.mp4 --params '{\"duration\":10,\"start\":10}'"

run_test "裁剪最后 10 秒" \
  "video-toolkit run --module trim --input test-30s.mp4 --output test-trim-end.mp4 --params '{\"duration\":10,\"start\":20}'"

# 场景 2: 不同比特率压缩测试
echo "📍 场景 2: 压缩功能对比"
echo ""

run_test "高比特率压缩 (8000k)" \
  "video-toolkit run --module compress --input test-30s.mp4 --output test-compress-high.mp4 --params '{\"bitrate\":\"8000k\"}'"

run_test "中等比特率压缩 (3000k)" \
  "video-toolkit run --module compress --input test-30s.mp4 --output test-compress-mid.mp4 --params '{\"bitrate\":\"3000k\"}'"

run_test "低比特率压缩 (1000k)" \
  "video-toolkit run --module compress --input test-30s.mp4 --output test-compress-low.mp4 --params '{\"bitrate\":\"1000k\"}'"

# 场景 3: 水印位置测试
echo "📍 场景 3: 水印位置测试"
echo ""

run_test "水印 - 左上角" \
  "video-toolkit run --module watermark --input test-30s.mp4 --output test-watermark-tl.mp4 --params '{\"text\":\"左上角\",\"position\":\"top-left\",\"fontSize\":36,\"color\":\"white\"}'"

run_test "水印 - 右上角" \
  "video-toolkit run --module watermark --input test-30s.mp4 --output test-watermark-tr.mp4 --params '{\"text\":\"右上角\",\"position\":\"top-right\",\"fontSize\":36,\"color\":\"yellow\"}'"

run_test "水印 - 中心" \
  "video-toolkit run --module watermark --input test-30s.mp4 --output test-watermark-center.mp4 --params '{\"text\":\"中心水印\",\"position\":\"center\",\"fontSize\":48,\"color\":\"red\"}'"

run_test "水印 - 左下角" \
  "video-toolkit run --module watermark --input test-30s.mp4 --output test-watermark-bl.mp4 --params '{\"text\":\"左下角\",\"position\":\"bottom-left\",\"fontSize\":36,\"color\":\"cyan\"}'"

run_test "水印 - 右下角" \
  "video-toolkit run --module watermark --input test-30s.mp4 --output test-watermark-br.mp4 --params '{\"text\":\"右下角\",\"position\":\"bottom-right\",\"fontSize\":36,\"color\":\"white\"}'"

# 场景 4: 画面裁剪测试
echo "📍 场景 4: 画面裁剪测试"
echo ""

run_test "裁剪为 720p" \
  "video-toolkit run --module crop --input test-30s.mp4 --output test-crop-720p.mp4 --params '{\"width\":1280,\"height\":720,\"x\":\"center\",\"y\":\"center\"}'"

run_test "裁剪为 480p" \
  "video-toolkit run --module crop --input test-30s.mp4 --output test-crop-480p.mp4 --params '{\"width\":854,\"height\":480,\"x\":\"center\",\"y\":\"center\"}'"

run_test "裁剪为正方形 (1:1)" \
  "video-toolkit run --module crop --input test-30s.mp4 --output test-crop-square.mp4 --params '{\"width\":720,\"height\":720,\"x\":\"center\",\"y\":\"center\"}'"

# 场景 5: 音频标准化测试
echo "📍 场景 5: 音频标准化测试"
echo ""

run_test "标准化到 -14 LUFS (TikTok 标准)" \
  "video-toolkit run --module normalize --input test-30s.mp4 --output test-normalize-14.mp4 --params '{\"target\":\"-14\"}'"

run_test "标准化到 -16 LUFS (YouTube 标准)" \
  "video-toolkit run --module normalize --input test-30s.mp4 --output test-normalize-16.mp4 --params '{\"target\":\"-16\"}'"

run_test "标准化到 -24 LUFS (广播标准)" \
  "video-toolkit run --module normalize --input test-30s.mp4 --output test-normalize-24.mp4 --params '{\"target\":\"-24\"}'"

# 场景 6: 组合使用测试
echo "📍 场景 6: 多步骤组合测试"
echo ""

# 步骤 1: 裁剪
run_test "组合测试步骤1: 裁剪 15 秒" \
  "video-toolkit run --module trim --input test-30s.mp4 --output test-step1.mp4 --params '{\"duration\":15}'"

# 步骤 2: 添加水印
run_test "组合测试步骤2: 添加水印" \
  "video-toolkit run --module watermark --input test-step1.mp4 --output test-step2.mp4 --params '{\"text\":\"Processed\",\"position\":\"bottom-right\",\"fontSize\":32}'"

# 步骤 3: 压缩
run_test "组合测试步骤3: 压缩输出" \
  "video-toolkit run --module compress --input test-step2.mp4 --output test-final-combo.mp4 --params '{\"bitrate\":\"2000k\"}'"

# 场景 7: 边界情况测试
echo "📍 场景 7: 边界情况测试"
echo ""

run_test "极短时长裁剪 (1秒)" \
  "video-toolkit run --module trim --input test-30s.mp4 --output test-trim-1s.mp4 --params '{\"duration\":1}'"

run_test "超低比特率 (500k)" \
  "video-toolkit run --module compress --input test-30s.mp4 --output test-compress-500k.mp4 --params '{\"bitrate\":\"500k\"}'"

run_test "超大水印 (72px)" \
  "video-toolkit run --module watermark --input test-30s.mp4 --output test-watermark-large.mp4 --params '{\"text\":\"BIG\",\"position\":\"center\",\"fontSize\":72,\"color\":\"white\"}'"

# 场景 8: 预设工作流测试
echo "📍 场景 8: 预设工作流测试"
echo ""

run_test "YouTube 预设工作流" \
  "video-toolkit workflow youtube --input test-30s.mp4 --output test-youtube-workflow.mp4"

run_test "TikTok 预设工作流" \
  "video-toolkit workflow tiktok --input test-30s.mp4 --output test-tiktok-workflow.mp4"

# 统计结果
echo ""
echo "================================"
echo ""
echo "📊 测试统计"
echo "----------------------------------------"
echo -e "总测试数: ${TOTAL_TESTS}"
echo -e "通过: ${GREEN}${PASSED_TESTS}${NC}"
echo -e "失败: ${YELLOW}${FAILED_TESTS}${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 所有测试通过！${NC}"
else
    echo -e "${YELLOW}⚠️  有 ${FAILED_TESTS} 个测试失败${NC}"
fi

echo ""
echo "📁 生成的测试文件:"
echo "----------------------------------------"
ls -lh test-*.mp4 2>/dev/null | awk '{printf "%-30s %s\n", $9, $5}'

echo ""
echo "📊 文件大小对比:"
echo "----------------------------------------"
echo "原始文件 (30秒):"
ls -lh test-30s.mp4 | awk '{print $5}'
echo ""
echo "压缩对比:"
ls -lh test-compress-*.mp4 2>/dev/null | awk '{printf "  %-30s %s\n", $9, $5}'

echo ""
echo "✅ 测试完成！"
