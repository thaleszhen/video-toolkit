#!/bin/bash

# GitHub 快速上传脚本

cat << 'EOF'

╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🚀 GitHub 上传准备完成！                              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

EOF

echo "📦 项目状态:"
echo "----------------------------------------"
cd /root/.openclaw/workspace-code
git log --oneline -1
echo ""

echo "📊 代码统计:"
echo "----------------------------------------"
echo "源文件: $(find src -name '*.ts' | wc -l) 个"
echo "测试文件: $(find tests -name '*.ts' | wc -l) 个"
echo "提交数: $(git log --oneline | wc -l) 次"
echo ""

echo "🎯 上传到 GitHub 有两种方式:"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "方式 1: 使用 GitHub CLI（推荐，自动化）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "步骤 1: 登录 GitHub CLI"
echo "  $ gh auth login"
echo ""
echo "  选项："
echo "  - What account? → GitHub.com"
echo "  - Protocol? → HTTPS"
echo "  - Authenticate? → Yes"
echo "  - How? → Login with a web browser"
echo "  - 复制 code，按 Enter"
echo "  - 在浏览器中授权"
echo ""
echo "步骤 2: 运行自动设置"
echo "  $ ./github-setup.sh"
echo ""
echo "✅ 完成！仓库将自动创建并推送"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "方式 2: 手动创建（完全控制）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "步骤 1: 在 GitHub 创建仓库"
echo "  访问: https://github.com/new"
echo "  仓库名: video-toolkit"
echo "  描述: AI 原生视频处理工具箱"
echo "  可见性: Public"
echo "  ❌ 不要初始化 README/gitignore/license"
echo ""
echo "步骤 2: 添加远程仓库"
echo "  $ git remote add origin https://github.com/YOUR_USERNAME/video-toolkit.git"
echo ""
echo "步骤 3: 推送代码"
echo "  $ git branch -M main"
echo "  $ git push -u origin main"
echo ""
echo "✅ 完成！"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📖 详细文档:"
echo "  cat GITHUB-GUIDE.md"
echo ""
echo "🌐 推荐设置:"
echo "  1. 添加仓库描述和 topics"
echo "  2. 启用 GitHub Actions (可选)"
echo "  3. 添加徽章到 README.md"
echo ""
echo "🚀 准备好了吗？开始上传吧！"
echo ""
