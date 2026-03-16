#!/bin/bash
# 运行 X Radar 爬虫

cd "$(dirname "$0")"

# 检查依赖
if ! python3 -c "import requests" 2>/dev/null; then
    echo "安装依赖..."
    pip3 install -r requirements.txt
fi

# 选择爬虫方式
echo "选择爬虫方式:"
echo "1) 混合爬虫（推荐：无需账号，生成真实模拟数据）"
echo "2) 模拟数据生成（快速测试）"
echo "3) twscrape（需要 Twitter 账号）"
echo "4) 官方 API（需要付费订阅）"
echo
read -p "请选择 [1-4]: " choice

case $choice in
    1)
        echo "启动混合爬虫..."
        python3 x_crawler_hybrid.py
        ;;
    2)
        echo "启动模拟数据生成..."
        python3 generate_mock_data.py
        ;;
    3)
        echo "启动 twscrape 爬虫..."
        python3 x_crawler_twscrape.py
        ;;
    4)
        echo "启动官方 API 爬虫..."
        if [ -z "$X_BEARER_TOKEN" ]; then
            echo "错误：请设置 X_BEARER_TOKEN 环境变量"
            exit 1
        fi
        python3 x_crawler.py
        ;;
    *)
        echo "无效选择，默认使用混合爬虫..."
        python3 x_crawler_hybrid.py
        ;;
esac
