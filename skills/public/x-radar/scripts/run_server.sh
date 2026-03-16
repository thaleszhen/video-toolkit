#!/bin/bash
# 运行 X Radar Web 服务

cd "$(dirname "$0")"

# 检查依赖
if ! python3 -c "import flask" 2>/dev/null; then
    echo "安装依赖..."
    pip3 install -r requirements.txt
fi

# 启动 Web 服务
echo "启动 X Radar Web 服务..."
echo "访问地址: http://localhost:5000"
python3 web_app.py
