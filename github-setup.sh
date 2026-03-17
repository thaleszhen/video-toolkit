#!/bin/bash

# GitHub 仓库设置脚本

echo "🚀 GitHub 仓库设置指南"
echo "================================"
echo ""

# 检查 gh 是否已登录
if gh auth status &> /dev/null; then
    echo "✅ GitHub CLI 已登录"
    echo ""

    # 获取用户名
    USERNAME=$(gh api user -q '.login')
    echo "👤 当前用户: $USERNAME"
    echo ""

    # 创建仓库
    echo "📦 创建 GitHub 仓库..."
    REPO_NAME="video-toolkit"

    # 检查仓库是否已存在
    if gh repo view "$USERNAME/$REPO_NAME" &> /dev/null; then
        echo "⚠️  仓库 $REPO_NAME 已存在"
        echo ""
        echo "将推送到现有仓库..."
    else
        echo "创建新仓库: $REPO_NAME"
        gh repo create "$REPO_NAME" \
            --public \
            --description "AI 原生视频处理工具箱 - 模块化、可扩展的视频处理工作流引擎" \
            --source=. \
            --remote=origin
        echo "✅ 仓库创建成功"
    fi

    # 添加远程仓库
    if ! git remote | grep -q "origin"; then
        git remote add origin "https://github.com/$USERNAME/$REPO_NAME.git"
    fi

    echo ""
    echo "📤 推送代码到 GitHub..."

    # 切换到主分支
    git branch -M main

    # 推送
    git push -u origin main

    echo ""
    echo "✅ 推送完成！"
    echo ""
    echo "🔗 仓库地址: https://github.com/$USERNAME/$REPO_NAME"

else
    echo "❌ GitHub CLI 未登录"
    echo ""
    echo "请先登录 GitHub CLI："
    echo ""
    echo "  gh auth login"
    echo ""
    echo "登录选项："
    echo "  1. 选择 GitHub.com"
    echo "  2. 选择 HTTPS 协议"
    echo "  3. 使用浏览器登录（推荐）或粘贴 token"
    echo ""
    echo "登录后重新运行此脚本："
    echo "  ./github-setup.sh"
fi
