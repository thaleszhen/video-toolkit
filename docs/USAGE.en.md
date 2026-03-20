# Video Toolkit Usage Guide (English)

This guide explains how to run and use the project from your local repository.

## 1. What You Can Do

- Process videos with preset workflows (`youtube`, `tiktok`)
- Run a custom workflow JSON via `--config`
- Batch-process a directory via `--input-dir` / `--output-dir`
- Run a single module (`trim`, `crop`, `compress`, `watermark`, `normalize`)
- Use a local video path or a YouTube URL as input
- Create a custom workflow JSON template, optionally from a preset

## 2. Requirements

- Node.js `>= 18`
- npm
- Dependencies installed (`npm ci` or `npm install`)

Note:
- The project uses `@ffmpeg-installer/ffmpeg` and `@ffprobe-installer/ffprobe`.
- If FFmpeg detection fails on your machine, set:
  - `FFMPEG_PATH`
  - `FFPROBE_PATH`

## 3. Setup

From project root:

```bash
cd d:\git_hub\video-toolkit
npm ci
npm run build
node dist/cli/index.js --help
```

## 4. Command Form

In this guide, commands use:

```bash
node dist/cli/index.js <command>
```

If you install globally, you can replace it with:

```bash
video-toolkit <command>
```

## 5. Quick Start

### 5.1 Run preset workflow with a local file

```bash
node dist/cli/index.js workflow youtube --input .\input.mp4 --output .\youtube-out.mp4
```

### 5.2 Run preset workflow with a YouTube URL (one command)

```bash
node dist/cli/index.js workflow youtube --input "https://youtu.be/u2ah9tWTkmk" --output .\youtube-out.mp4
```

### 5.3 Run a custom workflow file

```bash
node dist/cli/index.js workflow --config .\my-workflow.json --input .\input.mp4 --output .\custom-out.mp4
```

### 5.4 Batch-process a directory

```bash
node dist/cli/index.js workflow youtube --input-dir .\incoming --output-dir .\out
```

### 5.5 Run one module with a local file

```bash
node dist/cli/index.js run --module trim --input .\input.mp4 --output .\trim-out.mp4 --params duration=5,start=0
```

### 5.6 Run one module with a YouTube URL (one command)

```bash
node dist/cli/index.js run --module trim --input "https://youtu.be/u2ah9tWTkmk" --output .\trim-out.mp4 --params duration=5,start=0
```

## 6. Command Reference

### 6.1 Workflow

```bash
node dist/cli/index.js workflow <name> --input <file-or-url> --output <file>
```

Options:
- `<name>`: `youtube` or `tiktok`
- `--config <file>`: run a custom workflow JSON file
- `--input-dir <dir>`: process every supported video in a directory
- `--output-dir <dir>`: output directory for batch processing
- `--dry-run`: validate workflow without executing

Example:

```bash
node dist/cli/index.js workflow tiktok --input .\input.mp4 --output .\tiktok-out.mp4 --dry-run
```

```bash
node dist/cli/index.js workflow --config .\my-workflow.json --input-dir .\incoming --output-dir .\out --dry-run
```

### 6.2 Run single module

```bash
node dist/cli/index.js run --module <module-name> --input <file-or-url> --output <file> --params <params>
```

Parameter formats:

- JSON:
```bash
--params "{\"duration\":5,\"start\":0}"
```
- Key-value (recommended on PowerShell):
```bash
--params duration=5,start=0
```

### 6.3 Module inspection

```bash
node dist/cli/index.js module list
node dist/cli/index.js module list --category video
node dist/cli/index.js module info trim
```

### 6.4 Create custom workflow template

```bash
node dist/cli/index.js create-workflow --name my-workflow --output .\my-workflow.json
node dist/cli/index.js create-workflow --name branded-youtube --from-preset youtube --output .\branded-youtube.json
```

## 7. Built-in Modules

### 7.1 trim
- Required: `duration`
- Optional: `start` (default `0`)

```bash
node dist/cli/index.js run --module trim --input .\input.mp4 --output .\trim.mp4 --params duration=10,start=2
```

### 7.2 crop
- Required: `width`, `height`
- Optional: `x`, `y` (default `center`)

```bash
node dist/cli/index.js run --module crop --input .\input.mp4 --output .\crop.mp4 --params width=1920,height=1080,x=center,y=center
```

### 7.3 compress
- Required: `bitrate`

```bash
node dist/cli/index.js run --module compress --input .\input.mp4 --output .\compress.mp4 --params bitrate=5000k
```

### 7.4 watermark
- Required: `text`
- Optional: `position`, `fontSize`, `color`

```bash
node dist/cli/index.js run --module watermark --input .\input.mp4 --output .\watermark.mp4 --params text=MyBrand,position=bottom-right,fontSize=24,color=white
```

### 7.5 normalize
- Required: `target` (LUFS)

```bash
node dist/cli/index.js run --module normalize --input .\input.mp4 --output .\normalize.mp4 --params target=-16
```

## 8. Input and Output Behavior

- Local file input:
  - Must exist, otherwise command fails.
- Directory input:
  - Only supported video files in the top-level directory are processed.
- YouTube URL input:
  - Automatically downloaded to a temporary folder.
  - Temporary source files are auto-cleaned after execution.
- Output file:
  - Written to your specified `--output` path.
  - If `--output` is omitted in `run`, a default module-based filename is used.

## 9. Troubleshooting

### `spawn EPERM`
- Usually environment/sandbox permission issue for subprocess execution (FFmpeg/downloader).
- Run in a normal local terminal with sufficient permissions.

### Command not found
- Use full local command:
  - `node dist/cli/index.js ...`

### Cannot find output file
- Check absolute path:
```powershell
Get-Item .\out.mp4
```
