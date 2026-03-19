# Video Toolkit 使用说明（中文）

本文档说明如何在本地仓库中运行并使用本项目。

## 1. 项目可以做什么

- 使用预设工作流处理视频（`youtube`、`tiktok`）
- 运行单个处理模块（`trim`、`crop`、`compress`、`watermark`、`normalize`）
- 输入支持本地视频路径和 YouTube 链接
- 生成自定义工作流 JSON 模板

## 2. 运行环境

- Node.js `>= 18`
- npm
- 已安装依赖（`npm ci` 或 `npm install`）

说明：
- 项目内置 `@ffmpeg-installer/ffmpeg` 和 `@ffprobe-installer/ffprobe`。
- 如果 FFmpeg 自动检测失败，可手动设置环境变量：
  - `FFMPEG_PATH`
  - `FFPROBE_PATH`

## 3. 初始化步骤

在项目根目录执行：

```bash
cd d:\git_hub\video-toolkit
npm ci
npm run build
node dist/cli/index.js --help
```

## 4. 命令形式说明

本文都使用本地命令形式：

```bash
node dist/cli/index.js <command>
```

如果你已全局安装，也可改为：

```bash
video-toolkit <command>
```

## 5. 快速开始

### 5.1 本地视频 + 预设工作流

```bash
node dist/cli/index.js workflow youtube --input .\input.mp4 --output .\youtube-out.mp4
```

### 5.2 YouTube 链接 + 预设工作流（一条命令）

```bash
node dist/cli/index.js workflow youtube --input "https://youtu.be/u2ah9tWTkmk" --output .\youtube-out.mp4
```

### 5.3 本地视频 + 单模块

```bash
node dist/cli/index.js run --module trim --input .\input.mp4 --output .\trim-out.mp4 --params duration=5,start=0
```

### 5.4 YouTube 链接 + 单模块（一条命令）

```bash
node dist/cli/index.js run --module trim --input "https://youtu.be/u2ah9tWTkmk" --output .\trim-out.mp4 --params duration=5,start=0
```

## 6. 命令说明

### 6.1 `workflow`（工作流）

```bash
node dist/cli/index.js workflow <name> --input <文件或URL> --output <输出文件>
```

参数说明：
- `<name>`：`youtube` 或 `tiktok`
- `--dry-run`：只校验流程，不实际执行

示例：

```bash
node dist/cli/index.js workflow tiktok --input .\input.mp4 --output .\tiktok-out.mp4 --dry-run
```

### 6.2 `run`（单模块执行）

```bash
node dist/cli/index.js run --module <模块名> --input <文件或URL> --output <输出文件> --params <参数>
```

`--params` 支持两种格式：

- JSON：
```bash
--params "{\"duration\":5,\"start\":0}"
```
- 键值对（PowerShell 推荐）：
```bash
--params duration=5,start=0
```

### 6.3 `module`（模块信息）

```bash
node dist/cli/index.js module list
node dist/cli/index.js module list --category video
node dist/cli/index.js module info trim
```

### 6.4 `create-workflow`（创建模板）

```bash
node dist/cli/index.js create-workflow --name my-workflow --output .\my-workflow.json
```

## 7. 内置模块说明

### 7.1 `trim`（裁剪时长）
- 必填：`duration`
- 可选：`start`（默认 `0`）

```bash
node dist/cli/index.js run --module trim --input .\input.mp4 --output .\trim.mp4 --params duration=10,start=2
```

### 7.2 `crop`（裁剪画面）
- 必填：`width`、`height`
- 可选：`x`、`y`（默认 `center`）

```bash
node dist/cli/index.js run --module crop --input .\input.mp4 --output .\crop.mp4 --params width=1920,height=1080,x=center,y=center
```

### 7.3 `compress`（压缩视频）
- 必填：`bitrate`

```bash
node dist/cli/index.js run --module compress --input .\input.mp4 --output .\compress.mp4 --params bitrate=5000k
```

### 7.4 `watermark`（添加水印）
- 必填：`text`
- 可选：`position`、`fontSize`、`color`

```bash
node dist/cli/index.js run --module watermark --input .\input.mp4 --output .\watermark.mp4 --params text=MyBrand,position=bottom-right,fontSize=24,color=white
```

### 7.5 `normalize`（音频标准化）
- 必填：`target`（LUFS）

```bash
node dist/cli/index.js run --module normalize --input .\input.mp4 --output .\normalize.mp4 --params target=-16
```

## 8. 输入输出行为

- 本地文件输入：
  - 文件必须存在，否则会报错。
- YouTube 链接输入：
  - 程序会先自动下载到临时目录，再继续处理。
  - 临时下载文件在命令结束后自动清理。
- 输出文件：
  - 按 `--output` 指定路径写出。
  - `run` 命令在未指定 `--output` 时会使用默认命名。

## 9. 常见问题

### `spawn EPERM`
- 常见于权限或沙箱限制，导致 FFmpeg/下载器子进程无法启动。
- 请在有足够权限的本地终端执行。

### 命令找不到
- 直接用本地命令形式：
  - `node dist/cli/index.js ...`

### 找不到输出文件
- 用绝对路径检查：
```powershell
Get-Item .\out.mp4
```

