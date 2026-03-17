# video-toolkit

🎬 **AI 原生视频处理工具箱** - 模块化、可扩展的视频处理工作流引擎

[![Node.js Version](https://img.shields.io/badge/node-%3E%3D18.0.0-brightgreen)](https://nodejs.org/)
[![TypeScript](https://img.shields.io/badge/typescript-5.3-blue)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## ✨ 特性

- 🎯 **模块化架构** - 基于插件的模块系统，易于扩展
- 🔄 **工作流引擎** - 支持自定义工作流，串联多个处理步骤
- 🎬 **预设模板** - 内置 YouTube、TikTok 等平台优化预设
- 🛠️ **CLI 工具** - 完整的命令行界面，开箱即用
- 📦 **TypeScript** - 完整的类型支持，开发体验优秀
- ✅ **测试覆盖** - 63 个测试用例，核心功能 100% 覆盖

## 📦 安装

```bash
npm install -g video-toolkit
```

## 🚀 快速开始

### 使用预设工作流

最简单的方式是使用内置的预设工作流：

```bash
# 处理 YouTube 视频（1920x1080 横屏）
video-toolkit workflow youtube -i raw.mp4 -o final.mp4

# 处理 TikTok 视频（1080x1920 竖屏）
video-toolkit workflow tiktok -i raw.mp4 -o final.mp4

# 干运行模式（仅验证，不执行）
video-toolkit workflow youtube -i raw.mp4 -o final.mp4 --dry-run
```

### 模块管理

查看所有可用模块：

```bash
# 列出所有模块
video-toolkit module list

# 按类别筛选
video-toolkit module list --category video
video-toolkit module list --category audio

# 查看模块详情
video-toolkit module info trim
video-toolkit module info compress
```

### 运行单个模块

直接运行单个处理模块：

```bash
# 裁剪视频时长
video-toolkit run --module trim \
  --input video.mp4 \
  --params '{"duration": 60, "start": 10}'

# 压缩视频
video-toolkit run --module compress \
  --input video.mp4 \
  --params '{"bitrate": "5000k"}'

# 添加水印
video-toolkit run --module watermark \
  --input video.mp4 \
  --params '{"text": "My Brand", "position": "bottom-right"}'
```

### 创建自定义工作流

创建自己的工作流配置：

```bash
# 创建工作流模板
video-toolkit create-workflow --name my-workflow --output workflow.json

# 编辑 workflow.json，添加处理步骤
# 然后运行：
video-toolkit workflow my-workflow -i input.mp4 -o output.mp4
```

## 📚 核心模块

### 视频模块

| 模块 | 功能 | 关键参数 |
|------|------|---------|
| `trim` | 裁剪视频时长 | `duration`, `start` |
| `crop` | 裁剪画面尺寸 | `width`, `height`, `x`, `y` |
| `compress` | 压缩视频 | `bitrate`, `format` |
| `watermark` | 添加文字水印 | `text`, `position`, `fontSize`, `color` |

### 音频模块

| 模块 | 功能 | 关键参数 |
|------|------|---------|
| `normalize` | 音频标准化 | `target` (LUFS) |

## 🎬 预设工作流

### YouTube 预设

优化为 1080p 横屏视频，适合 YouTube 平台：

- ✂️ 时长：最长 10 分钟
- 📐 分辨率：1920x1080 (16:9)
- 🔊 音频：-16 LUFS 标准化
- 📦 比特率：8000k

```bash
video-toolkit workflow youtube -i raw.mp4 -o final.mp4
```

### TikTok 预设

优化为竖屏短视频，适合 TikTok/抖音：

- ✂️ 时长：最长 60 秒
- 📐 分辨率：1080x1920 (9:16)
- 🔊 音频：-14 LUFS 标准化
- 📦 比特率：5000k

```bash
video-toolkit workflow tiktok -i raw.mp4 -o final.mp4
```

## 🛠️ 开发

### 环境要求

- Node.js >= 18.0.0
- FFmpeg（系统已安装）

### 安装依赖

```bash
npm install
```

### 运行测试

```bash
npm test
```

### 构建

```bash
npm run build
```

### 开发模式

```bash
npm run dev
```

## 📖 工作流配置示例

```json
{
  "name": "my-custom-workflow",
  "description": "自定义工作流示例",
  "version": "1.0.0",
  "steps": [
    {
      "module": "trim",
      "name": "裁剪前 60 秒",
      "params": {
        "duration": 60,
        "start": 0
      }
    },
    {
      "module": "crop",
      "name": "裁剪为 1080p",
      "params": {
        "width": 1920,
        "height": 1080,
        "x": "center",
        "y": "center"
      }
    },
    {
      "module": "normalize",
      "name": "音频标准化",
      "params": {
        "target": "-16"
      }
    },
    {
      "module": "watermark",
      "name": "添加水印",
      "params": {
        "text": "My Brand",
        "position": "bottom-right",
        "fontSize": 24,
        "color": "white"
      }
    },
    {
      "module": "compress",
      "name": "压缩输出",
      "params": {
        "bitrate": "8000k",
        "format": "mp4"
      }
    }
  ]
}
```

## 🏗️ 架构

```
video-toolkit/
├── src/
│   ├── cli/              # CLI 命令
│   ├── engine/           # 工作流引擎
│   │   ├── parser.ts     # 解析器
│   │   ├── validator.ts  # 验证器
│   │   └── executor.ts   # 执行器
│   ├── modules/          # 模块系统
│   │   ├── core/         # 核心模块
│   │   └── interface.ts  # 模块接口
│   ├── utils/            # 工具类
│   └── presets/          # 预设工作流
└── tests/                # 测试文件
```

## 🤝 贡献

欢迎贡献代码！请查看 [贡献指南](CONTRIBUTING.md)。

## 📝 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [FFmpeg](https://ffmpeg.org/) - 强大的多媒体处理库
- [Commander.js](https://github.com/tj/commander.js/) - CLI 框架
- [fluent-ffmpeg](https://github.com/fluent-ffmpeg/node-fluent-ffmpeg) - FFmpeg Node.js 封装

---

**Made with ❤️ by Turing Toast Community**
