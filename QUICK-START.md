# 🚀 快速开始 - 5分钟上手

## ✅ 第一步：验证安装

```bash
# 进入项目目录
cd /root/.openclaw/workspace-code

# 查看版本（验证安装）
video-toolkit --version
# 输出: 1.0.0

# 查看帮助
video-toolkit --help
```

## 🎬 第二步：准备测试视频

```bash
# 方法1: 使用已有的测试视频
ls -lh test-video.mp4

# 方法2: 创建新的测试视频
./create-test-video.sh
```

## 🎯 第三步：尝试基本功能

### 1. 查看所有模块
```bash
video-toolkit module list
```

### 2. 查看模块详情
```bash
video-toolkit module info trim
video-toolkit module info compress
video-toolkit module info watermark
```

### 3. 裁剪视频（最简单）
```bash
# 裁剪为 5 秒
video-toolkit run --module trim \
  --input test-video.mp4 \
  --output my-trimmed.mp4 \
  --params '{"duration":5}'
```

### 4. 添加水印
```bash
# 添加右下角水印
video-toolkit run --module watermark \
  --input test-video.mp4 \
  --output my-watermarked.mp4 \
  --params '{"text":"My Brand","position":"bottom-right"}'
```

### 5. 压缩视频
```bash
# 压缩到 2000k
video-toolkit run --module compress \
  --input test-video.mp4 \
  --output my-compressed.mp4 \
  --params '{"bitrate":"2000k"}'
```

## 🎨 第四步：使用预设工作流

### YouTube 工作流（横屏 1080p）
```bash
# 干运行（仅验证）
video-toolkit workflow youtube \
  --input test-video.mp4 \
  --output youtube-output.mp4 \
  --dry-run

# 实际执行
video-toolkit workflow youtube \
  --input test-video.mp4 \
  --output youtube-output.mp4
```

### TikTok 工作流（竖屏 60秒）
```bash
# 干运行
video-toolkit workflow tiktok \
  --input test-video.mp4 \
  --output tiktok-output.mp4 \
  --dry-run

# 实际执行
video-toolkit workflow tiktok \
  --input test-video.mp4 \
  --output tiktok-output.mp4
```

## 📚 完整示例

### 示例1: 批量处理
```bash
# 处理所有 mp4 文件
for video in *.mp4; do
  video-toolkit workflow youtube \
    --input "$video" \
    --output "youtube_$video"
done
```

### 示例2: 创建自定义工作流
```bash
# 创建工作流模板
video-toolkit create-workflow \
  --name my-workflow \
  --output my-workflow.json

# 编辑 my-workflow.json（添加你的步骤）

# 运行自定义工作流
video-toolkit workflow my-workflow \
  --input test-video.mp4 \
  --output custom-output.mp4
```

## 🎓 进阶技巧

### 查看模块参数
```bash
# 查看所有参数和默认值
video-toolkit module info trim
video-toolkit module info crop
```

### 组合使用模块
```bash
# 1. 先裁剪
video-toolkit run --module trim \
  --input video.mp4 \
  --output step1.mp4 \
  --params '{"duration":30}'

# 2. 再添加水印
video-toolkit run --module watermark \
  --input step1.mp4 \
  --output step2.mp4 \
  --params '{"text":"My Brand"}'

# 3. 最后压缩
video-toolkit run --module compress \
  --input step2.mp4 \
  --output final.mp4 \
  --params '{"bitrate":"5000k"}'
```

## 📖 更多资源

- **完整教程**: `cat TUTORIAL.md`
- **演示结果**: `cat DEMO-RESULTS.md`
- **项目文档**: `cat README.md`
- **运行演示**: `./demo.sh`

## ⚡ 快速命令参考

```bash
# 查看版本
video-toolkit --version

# 列出模块
video-toolkit module list

# 模块详情
video-toolkit module info <module-name>

# 运行模块
video-toolkit run --module <name> --input <file> --params '<json>'

# 运行工作流
video-toolkit workflow <name> --input <file> --output <file>

# 创建工作流
video-toolkit create-workflow --name <name>
```

## 🎉 开始你的创作！

现在你已经掌握了基本用法，可以：

1. ✅ 处理你自己的视频文件
2. ✅ 创建自定义工作流
3. ✅ 批量处理视频
4. ✅ 为不同平台优化视频

**祝你使用愉快！** 🚀

---

**需要帮助？**
- 查看 README.md 获取完整文档
- 运行 `video-toolkit --help` 查看命令帮助
- 运行 `video-toolkit <command> --help` 查看子命令帮助
