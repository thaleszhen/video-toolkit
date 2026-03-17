# 🚀 快速上传到 GitHub (thaleszhen/video-toolkit)

## ⚡ 最快方式 (5分钟)

### 步骤 1: 创建 Personal Access Token (2分钟)

1. **打开浏览器**，访问：
   ```
   https://github.com/settings/tokens/new
   ```

2. **填写表单**：
   - **Note**: `video-toolkit-upload`
   - **Expiration**: `30 days` (或更长)
   - **Scopes**: 只需要勾选 `repo` (完整仓库权限)

3. **生成 Token**：
   - 点击绿色按钮 `Generate token`
   - **⚠️ 立即复制** token (格式: `ghp_xxxxxxxxxxxx`)
   - 只会显示一次！

### 步骤 2: 运行上传脚本 (1分钟)

在终端中运行（替换 `YOUR_TOKEN_HERE` 为你的 token）：

```bash
cd /root/.openclaw/workspace-code
GITHUB_TOKEN='YOUR_TOKEN_HERE' ./push-to-github.sh
```

例如：
```bash
GITHUB_TOKEN='ghp_ABC123def456GHI789jkl' ./push-to-github.sh
```

### 步骤 3: 完成！

✅ 访问你的仓库：
```
https://github.com/thaleszhen/video-toolkit
```

---

## 📖 详细步骤

### 如果你已有 Token

直接运行：

```bash
cd /root/.openclaw/workspace-code

# 方式 1: 使用环境变量
export GITHUB_TOKEN='your_token_here'
./push-to-github.sh

# 方式 2: 直接传递
GITHUB_TOKEN='your_token_here' ./push-to-github.sh
```

### 如果你想手动推送

```bash
cd /root/.openclaw/workspace-code

# 1. 添加远程仓库 (替换 YOUR_TOKEN)
git remote add origin https://YOUR_TOKEN@github.com/thaleszhen/video-toolkit.git

# 2. 切换到 main 分支
git branch -M main

# 3. 推送
git push -u origin main
```

---

## 🔧 如果推送失败

### 错误 1: Token 权限不足

**解决**：重新创建 token，确保勾选了 `repo` 权限

### 错误 2: 仓库已存在

**解决方案 A**：先在 GitHub 删除旧仓库
```
https://github.com/thaleszhen/video-toolkit/settings
→ 滚动到底部 → Delete this repository
```

**解决方案 B**：强制推送
```bash
git push -u origin main --force
```

### 错误 3: 认证失败

**检查**：
- Token 是否正确复制（没有多余空格）
- Token 是否过期
- 用户名是否正确（thaleszhen）

---

## 📊 推送后的仓库统计

项目包含：
- ✅ 17 个 TypeScript 源文件 (959 行)
- ✅ 19 个测试文件 (845 行)
- ✅ 71 个测试用例
- ✅ 5 个核心模块
- ✅ 2 个预设工作流
- ✅ 完整的文档

---

## 🎯 推送后建议

### 1. 添加仓库描述

访问：`https://github.com/thaleszhen/video-toolkit`

点击 ⚙️ (Settings 旁边的齿轮图标)：
- **Description**: `AI 原生视频处理工具箱 - 模块化、可扩展的视频处理工作流引擎`
- **Website**: 留空或添加项目网站
- **Topics**: 添加标签
  - `video-processing`
  - `ffmpeg`
  - `nodejs`
  - `typescript`
  - `cli`
  - `workflow-engine`

### 2. 启用 GitHub Actions (可选)

创建 `.github/workflows/test.yml`:

```yaml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm install
      - run: npm test
```

### 3. 添加徽章到 README.md

在 README.md 顶部添加：

```markdown
[![GitHub stars](https://img.shields.io/github/stars/thaleszhen/video-toolkit?style=social)](https://github.com/thaleszhen/video-toolkit)
[![GitHub forks](https://img.shields.io/github/forks/thaleszhen/video-toolkit?style=social)](https://github.com/thaleszhen/video-toolkit/fork)
[![GitHub issues](https://img.shields.io/github/issues/thaleszhen/video-toolkit)](https://github.com/thaleszhen/video-toolkit/issues)
[![GitHub license](https://img.shields.io/github/license/thaleszhen/video-toolkit)](https://github.com/thaleszhen/video-toolkit)
```

---

## ✅ 准备好了！

**最快方式（3步）**：

```bash
# 1. 创建 token: https://github.com/settings/tokens/new

# 2. 运行脚本 (替换 YOUR_TOKEN)
cd /root/.openclaw/workspace-code
GITHUB_TOKEN='YOUR_TOKEN' ./push-to-github.sh

# 3. 访问仓库
# https://github.com/thaleszhen/video-toolkit
```

**开始上传吧！** 🚀
