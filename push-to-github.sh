#!/bin/bash

# 使用 Personal Access Token 推送到 GitHub

USERNAME="thaleszhen"
REPO_NAME="video-toolkit"

echo "🚀 准备推送 video-toolkit 到 GitHub"
echo "========================================"
echo ""
echo "目标仓库: https://github.com/$USERNAME/$REPO_NAME"
echo ""

# 检查是否提供了 token
if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ 未设置 GITHUB_TOKEN 环境变量"
    echo ""
    echo "📝 创建 Personal Access Token 步骤:"
    echo "----------------------------------------"
    echo "1. 访问: https://github.com/settings/tokens/new"
    echo "2. 设置选项:"
    echo "   - Note: video-toolkit-upload"
    echo "   - Expiration: 30 days (或更长)"
    echo "   - Scopes: 勾选 'repo' (完整仓库权限)"
    echo "3. 点击 'Generate token'"
    echo "4. 复制生成的 token (ghp_xxxxxxxxx)"
    echo ""
    echo "5. 设置环境变量并运行:"
    echo "   export GITHUB_TOKEN='your_token_here'"
    echo "   ./push-to-github.sh"
    echo ""
    echo "或者直接运行:"
    echo "   GITHUB_TOKEN='your_token_here' ./push-to-github.sh"
    exit 1
fi

echo "✅ Token 已设置"
echo ""

# 配置 git 用户信息（如果需要）
if [ -z "$(git config user.name)" ]; then
    git config user.name "thaleszhen"
    git config user.email "thaleszhen@users.noreply.github.com"
    echo "✅ Git 用户信息已配置"
fi

# 检查远程仓库
if git remote | grep -q "origin"; then
    echo "⚠️  远程仓库 'origin' 已存在，更新地址..."
    git remote set-url origin "https://$GITHUB_TOKEN@github.com/$USERNAME/$REPO_NAME.git"
else
    echo "📦 添加远程仓库..."
    git remote add origin "https://$GITHUB_TOKEN@github.com/$USERNAME/$REPO_NAME.git"
fi

echo "✅ 远程仓库已配置"
echo ""

# 切换到 main 分支
echo "🔄 切换到 main 分支..."
git branch -M main

# 推送代码
echo "📤 推送代码到 GitHub..."
echo ""

if git push -u origin main; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "✅ 推送成功！"
    echo ""
    echo "🌐 仓库地址: https://github.com/$USERNAME/$REPO_NAME"
    echo ""
    echo "📊 仓库信息:"
    echo "  - 提交数: $(git log --oneline | wc -l)"
    echo "  - 源文件: $(find src -name '*.ts' | wc -l) 个"
    echo "  - 测试文件: $(find tests -name '*.ts' | wc -l) 个"
    echo ""
    echo "🎯 接下来可以:"
    echo "  1. 访问仓库查看代码"
    echo "  2. 添加仓库描述和 topics"
    echo "  3. 启用 GitHub Actions"
    echo "  4. 添加徽章到 README.md"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
else
    echo ""
    echo "❌ 推送失败"
    echo ""
    echo "可能的原因:"
    echo "  1. Token 权限不足 (需要 'repo' 权限)"
    echo "  2. 仓库已存在且有不同的提交历史"
    echo "  3. 网络连接问题"
    echo ""
    echo "💡 解决方案:"
    echo "  - 检查 token 是否正确"
    echo "  - 如果仓库已存在，先删除或使用 --force 推送"
    echo "  - 检查网络连接"
fi
