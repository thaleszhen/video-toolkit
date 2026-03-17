# 🚀 GitHub 上传指南

## 方式 1: 使用 GitHub CLI（自动化，推荐）

### 步骤 1: 登录 GitHub CLI

```bash
gh auth login
```

登录选项：
1. **What account do you want to log into?** → 选择 `GitHub.com`
2. **What is your preferred protocol for Git operations?** → 选择 `HTTPS`
3. **Authenticate Git with your GitHub credentials?** → 选择 `Yes`
4. **How would you like to authenticate GitHub CLI?** → 选择 `Login with a web browser`
5. 复制显示的 code，按 Enter 打开浏览器
6. 在浏览器中粘贴 code 并授权

### 步骤 2: 运行自动设置脚本

```bash
cd /root/.openclaw/workspace-code
chmod +x github-setup.sh
./github-setup.sh
```

脚本会自动：
- ✅ 创建 GitHub 仓库
- ✅ 添加远程地址
- ✅ 推送所有代码

---

## 方式 2: 手动设置（完全控制）

### 步骤 1: 在 GitHub 上创建仓库

1. 访问 https://github.com/new
2. 填写信息：
   - **Repository name**: `video-toolkit`
   - **Description**: `AI 原生视频处理工具箱 - 模块化、可扩展的视频处理工作流引擎`
   - **Public/Private**: 选择 Public
   - **不要勾选** "Initialize this repository with a README"
3. 点击 "Create repository"

### 步骤 2: 配置远程仓库

```bash
cd /root/.openclaw/workspace-code

# 添加远程仓库（替换 YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/video-toolkit.git

# 或者使用 SSH（如果配置了 SSH key）
git remote add origin git@github.com:YOUR_USERNAME/video-toolkit.git
```

### 步骤 3: 推送代码

```bash
# 切换到 main 分支
git branch -M main

# 推送代码
git push -u origin main
```

---

## 方式 3: 使用 Personal Access Token

### 步骤 1: 创建 Personal Access Token

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 设置：
   - **Note**: `video-toolkit-upload`
   - **Expiration**: 选择 30 天或更长
   - **Scopes**: 勾选 `repo` (完整仓库访问权限)
4. 点击 "Generate token"
5. **⚠️ 复制 token**（只显示一次）

### 步骤 2: 使用 token 推送

```bash
cd /root/.openclaw/workspace-code

# 添加远程仓库（替换 YOUR_USERNAME 和 YOUR_TOKEN）
git remote add origin https://YOUR_TOKEN@github.com/YOUR_USERNAME/video-toolkit.git

# 推送
git push -u origin main
```

---

## 📋 推送前的检查清单

运行以下命令检查项目状态：

```bash
# 查看当前状态
git status

# 查看提交历史
git log --oneline | head -10

# 查看将要推送的文件
git ls-files | grep -v node_modules | grep -v ".mp4$" | head -20
```

---

## 🔧 推荐的 .gitignore

已配置的 .gitignore 会排除：
- ✅ `node_modules/` - 依赖文件
- ✅ `dist/` - 编译输出
- ✅ `*.log` - 日志文件
- ✅ `test-*.mp4` - 测试视频
- ✅ `*.mp4` - 所有视频文件
- ✅ `.DS_Store` - macOS 文件
- ✅ `temp-*/` - 临时目录

---

## ✅ 验证上传成功

推送后，访问你的仓库页面：

```
https://github.com/YOUR_USERNAME/video-toolkit
```

检查：
- ✅ 所有源代码文件都在
- ✅ README.md 正确显示
- ✅ 仓库描述正确
- ✅ 没有敏感信息（token、密码等）

---

## 📝 可选：添加仓库徽章

在 README.md 顶部添加徽章：

```markdown
[![GitHub stars](https://img.shields.io/github/stars/YOUR_USERNAME/video-toolkit?style=social)](https://github.com/YOUR_USERNAME/video-toolkit)
[![GitHub forks](https://img.shields.io/github/forks/YOUR_USERNAME/video-toolkit?style=social)](https://github.com/YOUR_USERNAME/video-toolkit/fork)
[![GitHub license](https://img.shields.io/github/license/YOUR_USERNAME/video-toolkit)](https://github.com/YOUR_USERNAME/video-toolkit)
```

---

## 🎯 推荐设置

推送后，在 GitHub 仓库设置中：

1. **About** 部分：
   - 添加描述
   - 添加网站链接（如果有）
   - 添加 topics: `video-processing`, `ffmpeg`, `nodejs`, `typescript`, `cli`

2. **Branches**：
   - 设置 `main` 为默认分支
   - 添加分支保护规则（可选）

3. **Actions**（可选）：
   - 启用 GitHub Actions 进行 CI/CD

---

## 🐛 常见问题

### 问题 1: remote origin already exists

```bash
# 删除现有远程
git remote remove origin

# 重新添加
git remote add origin https://github.com/YOUR_USERNAME/video-toolkit.git
```

### 问题 2: Authentication failed

```bash
# 使用 token 方式
git remote set-url origin https://YOUR_TOKEN@github.com/YOUR_USERNAME/video-toolkit.git
```

### 问题 3: Push rejected (non-fast-forward)

```bash
# 强制推送（仅在新仓库时）
git push -u origin main --force

# 或者拉取后合并
git pull origin main --allow-unrelated-histories
git push -u origin main
```

---

**选择最适合你的方式，开始上传吧！** 🚀
