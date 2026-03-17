# video-toolkit 使用教程

## 🎯 快速开始

### 1. 查看可用命令

```bash
# 查看主命令帮助
video-toolkit --help

# 查看版本
video-toolkit --version
```

### 2. 查看可用模块

```bash
# 列出所有模块
video-toolkit module list

# 只看视频模块
video-toolkit module list --category video

# 只看音频模块
video-toolkit module list --category audio

# 查看模块详细信息
video-toolkit module info trim
video-toolkit module info compress
video-toolkit module info watermark
```

### 3. 创建测试视频（用于演示）

由于我们使用 FFmpeg，可以用它创建一个测试视频：

```bash
# 创建一个 10 秒的测试视频
ffmpeg -f lavfi -i testsrc=duration=10:size=1920x1080:rate=30 \
  -f lavfi -i sine=frequency=1000:duration=10 \
  -pix_fmt yuv420p test-video.mp4
```

### 4. 使用预设工作流

#### YouTube 预设（横屏 1080p）

```bash
# 干运行模式（仅验证，不执行）
video-toolkit workflow youtube \
  --input test-video.mp4 \
  --output youtube-output.mp4 \
  --dry-run

# 实际执行
video-toolkit workflow youtube \
  --input test-video.mp4 \
  --output youtube-output.mp4
```

#### TikTok 预设（竖屏 60秒）

```bash
# 干运行模式
video-toolkit workflow tiktok \
  --input test-video.mp4 \
  --output tiktok-output.mp4 \
  --dry-run

# 实际执行
video-toolkit workflow tiktok \
  --input test-video.mp4 \
  --output tiktok-output.mp4
```

### 5. 运行单个模块

#### 裁剪视频时长

```bash
# 裁剪前 5 秒
video-toolkit run \
  --module trim \
  --input test-video.mp4 \
  --output trimmed.mp4 \
  --params '{"duration":5,"start":0}'
```

#### 裁剪画面

```bash
# 裁剪为 720p
video-toolkit run \
  --module crop \
  --input test-video.mp4 \
  --output cropped.mp4 \
  --params '{"width":1280,"height":720,"x":"center","y":"center"}'
```

#### 压缩视频

```bash
# 压缩到 5000k
video-toolkit run \
  --module compress \
  --input test-video.mp4 \
  --output compressed.mp4 \
  --params '{"bitrate":"5000k"}'
```

#### 添加水印

```bash
# 添加右下角水印
video-toolkit run \
  --module watermark \
  --input test-video.mp4 \
  --output watermarked.mp4 \
  --params '{"text":"My Brand","position":"bottom-right","fontSize":24,"color":"white"}'
```

#### 音频标准化

```bash
# 标准化到 -16 LUFS
video-toolkit run \
  --module normalize \
  --input test-video.mp4 \
  --output normalized.mp4 \
  --params '{"target":"-16"}'
```

### 6. 创建自定义工作流

```bash
# 创建工作流模板
video-toolkit create-workflow \
  --name my-custom-workflow \
  --description "我的自定义工作流" \
  --output my-workflow.json

# 编辑 my-workflow.json 文件
# 添加你需要的处理步骤

# 运行自定义工作流
video-toolkit workflow my-custom-workflow \
  --input test-video.mp4 \
  --output custom-output.mp4
```

## 📝 自定义工作流示例

编辑 `my-workflow.json`:

```json
{
  "name": "my-custom-workflow",
  "description": "我的自定义工作流",
  "version": "1.0.0",
  "steps": [
    {
      "module": "trim",
      "name": "裁剪前 30 秒",
      "params": {
        "duration": 30,
        "start": 0
      }
    },
    {
      "module": "watermark",
      "name": "添加品牌水印",
      "params": {
        "text": "My Brand",
        "position": "bottom-right",
        "fontSize": 32,
        "color": "white"
      }
    },
    {
      "module": "compress",
      "name": "压缩输出",
      "params": {
        "bitrate": "6000k",
        "format": "mp4"
      }
    }
  ]
}
```

## 🎬 实际应用场景

### 场景 1: 批量处理 YouTube 视频

```bash
for video in *.mp4; do
  video-toolkit workflow youtube \
    --input "$video" \
    --output "youtube_${video}"
done
```

### 场景 2: 从长视频提取片段

```bash
# 提取 1:00-1:30 的片段
video-toolkit run \
  --module trim \
  --input long-video.mp4 \
  --output clip.mp4 \
  --params '{"duration":30,"start":60}'
```

### 场景 3: 为不同平台创建多个版本

```bash
# 创建 YouTube 版本
video-toolkit workflow youtube \
  --input raw.mp4 \
  --output youtube.mp4

# 创建 TikTok 版本
video-toolkit workflow tiktok \
  --input raw.mp4 \
  --output tiktok.mp4
```

## 🔧 高级技巧

### 查看模块参数详情

```bash
video-toolkit module info compress
```

输出会显示所有参数及其类型、默认值等。

### 验证工作流而不执行

使用 `--dry-run` 参数：

```bash
video-toolkit workflow youtube --input test.mp4 --output out.mp4 --dry-run
```

### 查看详细日志

```bash
video-toolkit workflow youtube \
  --input test.mp4 \
  --output out.mp4 \
  --verbose
```

## ⚠️ 注意事项

1. **FFmpeg 依赖**: 确保系统已安装 FFmpeg
2. **文件路径**: 支持相对路径和绝对路径
3. **参数格式**: JSON 参数需要用单引号包裹
4. **输出覆盖**: 如果输出文件已存在，会被覆盖

## 🐛 故障排除

### 问题: 找不到 video-toolkit 命令

**解决方案**:
```bash
cd /root/.openclaw/workspace-code
npm link
```

### 问题: FFmpeg not found

**解决方案**:
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg
```

### 问题: 模块执行失败

**解决方案**:
1. 检查输入文件是否存在
2. 检查参数是否正确
3. 使用 `module info` 查看参数详情

## 📚 更多信息

查看 README.md 获取完整文档。

---

**祝你使用愉快！** 🎉
