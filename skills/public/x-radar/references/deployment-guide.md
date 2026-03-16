# X Radar 部署指南

## 快速部署步骤

### 1. 获取 Twitter API 凭证

1. 访问 [Twitter Developer Portal](https://developer.twitter.com/)
2. 创建一个开发者账号（需要 Twitter 账号）
3. 创建一个新的 App
4. 在 App 设置中生成 Bearer Token
5. 复制 Bearer Token

### 2. 配置环境变量

```bash
# 在 ~/.bashrc 或 ~/.zshrc 中添加
export X_BEARER_TOKEN="your_bearer_token_here"

# 重新加载配置
source ~/.bashrc  # 或 source ~/.zshrc
```

### 3. 首次运行

```bash
# 进入 skill 目录
cd /root/.openclaw/workspace-code/skills/public/x-radar/scripts

# 安装依赖
pip3 install -r requirements.txt

# 运行爬虫（测试）
python3 x_crawler.py

# 启动 Web 服务（测试）
python3 web_app.py
```

### 4. 访问测试

打开浏览器访问：http://localhost:5000

### 5. 配置定时任务

```bash
# 编辑 crontab
crontab -e

# 添加以下内容（每天凌晨 2 点爬取）
0 2 * * * cd /root/.openclaw/workspace-code/skills/public/x-radar/scripts && ./run_crawler.sh >> /var/log/x-radar.log 2>&1

# 添加 Web 服务自启动（使用 systemd，见下文）
```

## 使用 Systemd 管理服务

### 创建服务文件

```bash
sudo nano /etc/systemd/system/x-radar-web.service
```

内容：

```ini
[Unit]
Description=X Radar Web Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/.openclaw/workspace-code/skills/public/x-radar/scripts
Environment="X_BEARER_TOKEN=your_bearer_token_here"
ExecStart=/usr/bin/python3 /root/.openclaw/workspace-code/skills/public/x-radar/scripts/web_app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 启动服务

```bash
# 重载 systemd 配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start x-radar-web

# 设置开机自启
sudo systemctl enable x-radar-web

# 查看服务状态
sudo systemctl status x-radar-web
```

## 数据库管理

### 查看数据

```bash
# 使用 sqlite3 命令行工具
cd /root/.openclaw/workspace-code/skills/public/x-radar/scripts/../data
sqlite3 x_radar.db

# 在 sqlite3 中
.tables
.schema posts
SELECT COUNT(*) FROM posts;
SELECT * FROM posts LIMIT 5;
.quit
```

### 备份数据库

```bash
# 创建备份目录
mkdir -p /backups/x-radar

# 备份数据库
cp /root/.openclaw/workspace-code/skills/public/x-radar/data/x_radar.db /backups/x-radar/x_radar_$(date +%Y%m%d).db
```

### 清理旧数据

```bash
# 清理 30 天前的数据
sqlite3 /root/.openclaw/workspace-code/skills/public/x-radar/data/x_radar.db "DELETE FROM posts WHERE crawled_at < datetime('now', '-30 days');"
sqlite3 /root/.openclaw/workspace-code/skills/public/x-radar/data/x_radar.db "DELETE FROM comments WHERE crawled_at < datetime('now', '-30 days');"
```

## 公网访问配置

### 使用 ngrok（临时测试）

```bash
# 安装 ngrok
# https://ngrok.com/

# 启动隧道
ngrok http 5000
```

### 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 性能优化建议

1. **数据库索引**: 为常用查询字段添加索引
2. **缓存**: 为 API 响应添加缓存
3. **分页**: 对于大量数据实现分页加载
4. **异步**: 使用异步爬虫提高爬取效率

## 监控和日志

### 查看日志

```bash
# 查看爬虫日志
tail -f /var/log/x-radar.log

# 查看 systemd 服务日志
sudo journalctl -u x-radar-web -f
```

### 监控指标

- 爬取成功率
- API 调用次数
- 数据库大小
- 响应时间
