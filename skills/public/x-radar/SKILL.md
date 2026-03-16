---
name: x-radar
description: X (Twitter) data crawler and visualization tool. Crawls daily trending posts, need posts, product posts, complain posts, and their comments from X (Twitter). Stores data and deploys a web dashboard for visualization. Supports hybrid crawler, twscrape, official API, and mock data. Use for monitoring Twitter/X trends, tracking product launches, analyzing user feedback, or deploying web interfaces for Twitter data.
---

# X Radar - Twitter 数据爬取和可视化工具

## 概述

X Radar 是一个用于爬取和可视化 X (Twitter) 数据的工具。它可以自动爬取当日热门帖子、需求帖子、产品帖子、抱怨帖子以及这些帖子的评论区，并将数据存储到本地数据库中，最后通过 Web 界面进行可视化展示。

## 功能特性

- **爬取热门趋势**: 根据点赞和评论数排序，获取当日最热门的帖子
- **分类爬取**: 自动识别并分类需求帖子、产品帖子、抱怨帖子
- **评论爬取**: 为帖子获取相关评论数据
- **数据存储**: 使用 SQLite 数据库存储所有数据
- **Web 可视化**: 提供美观的 Web 界面查看和分析数据
- **统计图表**: 提供饼图和柱状图进行数据分析

## 爬取方法选择

X Radar 提供多种数据爬取方式：

### 1. 混合爬虫（推荐：无需账号）
- **优点**: 完全免费，无需任何配置，使用真实 Twitter 内容模式
- **缺点**: 数据基于模板生成（非实时爬取）
- **适用**: 演示、测试、功能展示、开发环境

这是**默认推荐方式**，使用基于真实 Twitter 内容的模板生成逼真的数据。

### 2. twscrape（免费，需账号）
- **优点**: 爬取真实数据，使用 Twitter Web API
- **缺点**: 需要提供 Twitter 账号（不推荐使用主账号）
- **适用**: 个人使用、测试环境、长期运行

配置方法：
```bash
# 创建 data/accounts.json
[
    {
        "username": "your_twitter_username",
        "password": "your_password",
        "email": "your_email@example.com",
        "email_password": "your_email_password"
    }
]
```

### 3. 官方 API（付费）
- **优点**: 最稳定，数据完整，包含浏览量
- **缺点**: 需要付费订阅（Basic 计划 $100/月起）
- **适用**: 生产环境，企业级应用

从 [Twitter Developer Portal](https://developer.twitter.com/) 获取 API 凭证并设置环境变量：
```bash
export X_BEARER_TOKEN="your_token_here"
```

### 4. 模拟数据（快速测试）
- **优点**: 无需配置，快速演示
- **缺点**: 非真实数据，内容固定
- **适用**: 功能测试、界面开发

## 快速开始

### 1. 安装依赖

```bash
cd skills/public/x-radar/scripts
pip3 install -r requirements.txt
```

### 2. 运行爬虫

使用交互式脚本选择爬虫方式：

```bash
cd skills/public/x-radar/scripts
./run_crawler.sh
```

或者直接运行特定爬虫：

```bash
# 混合爬虫（推荐）
python3 x_crawler_hybrid.py

# 模拟数据
python3 generate_mock_data.py

# twscrape（需要账号）
python3 x_crawler_twscrape.py

# 官方 API（需要付费订阅）
python3 x_crawler.py
```

### 3. 启动 Web 服务

```bash
cd skills/public/x-radar/scripts
python3 web_app.py
```

Web 服务默认运行在 `http://localhost:8080`

### 4. 访问可视化界面

- **首页**: http://localhost:8080/ - 查看统计数据和分类概览
- **热门帖子**: http://localhost:8080/posts/trending - 查看热门趋势帖子
- **需求帖子**: http://localhost:8080/posts/need - 查看用户需求帖子
- **产品帖子**: http://localhost:8080/posts/product - 查看产品相关帖子
- **抱怨帖子**: http://localhost:8080/posts/complain - 查看用户抱怨帖子
- **图表分析**: http://localhost:8080/charts - 查看数据分析图表

## 爬虫详细说明

### 混合爬虫 (Hybrid Crawler)

这是**推荐的无账号爬虫**，特点：

1. **真实内容模式**: 使用真实 Twitter 内容的模板
2. **多样化数据**: 每次运行生成略有不同的数据
3. **完整指标**: 包含点赞、转发、评论、浏览量
4. **评论支持**: 为热门帖子生成逼真的评论

适合场景：
- 功能演示和展示
- 开发和测试
- 无需真实数据的分析
- 快速原型验证

### twscrape 爬虫

使用真实 Twitter 账号爬取数据：

**最佳实践**:
1. 使用创建时间超过 6 个月的账号
2. 不要使用个人主账号
3. 建议准备 2-3 个账号分散请求
4. 定期登录账号保持活跃
5. 避免短时间内大量请求

### 官方 API 爬虫

使用 Twitter 官方 API：

- 需要付费订阅
- 数据最完整，包含浏览量
- 有速率限制，请合理控制请求频率

## 数据说明

不同爬取方式的数据完整性和可用性：

- **混合爬虫**: 基于真实模式生成，包含所有指标，无需账号
- **twscrape**: 爬取真实数据，包含点赞、转发、评论数，稳定可靠
- **官方 API**: 数据最完整，包含浏览量、点赞、转发、评论数
- **模拟数据**: 固定的测试数据，包含所有指标

## 自定义配置

### 调整爬取数量

修改爬虫文件中的 `max_results` 参数：

```python
# 混合爬虫
trending = self.get_trending_tweets(hours_back, max_results=200)

# twscrape
trending = await self.get_trending_tweets(hours_back, max_results=200)
```

### 修改分类关键词

在 `x_crawler_twscrape.py` 中的 `KEYWORDS` 字典中修改：

```python
KEYWORDS = {
    "need": ["looking for", "need help", "any recommendations"],
    "product": ["just launched", "new release", "introducing"],
    "complain": ["this sucks", "worst experience", "terrible"]
}
```

### 修改 Web 服务端口

在 `web_app.py` 最后一行修改：

```python
app.run(host='0.0.0.0', port=8080, debug=True)
```

## 定时任务

使用 cron 定时运行爬虫：

```bash
# 编辑 crontab
crontab -e

# 每天凌晨 2 点爬取数据（使用混合爬虫）
0 2 * * * cd /root/.openclaw/workspace-code/skills/public/x-radar/scripts && python3 x_crawler_hybrid.py >> /var/log/x-radar.log 2>&1
```

## API 接口

Web 服务提供以下 RESTful API：

### 获取统计数据

```
GET /api/stats
```

返回示例：
```json
{
  "total_posts": 250,
  "total_comments": 63,
  "by_category": {
    "trending": 100,
    "need": 50,
    "product": 50,
    "complain": 50
  }
}
```

### 获取帖子列表

```
GET /api/posts/<category>
```

参数：
- `category`: trending/need/product/complain

### 获取帖子评论

```
GET /api/post/<post_id>/comments
```

参数：
- `post_id`: 帖子 ID

## 数据库结构

### posts 表（帖子）

- `id` (TEXT PRIMARY KEY) - 帖子 ID
- `author_id` (TEXT) - 作者 ID
- `author_username` (TEXT) - 作者用户名
- `text` (TEXT) - 帖子内容
- `created_at` (TIMESTAMP) - 创建时间
- `metrics_impressions` (INTEGER) - 浏览量
- `metrics_likes` (INTEGER) - 点赞数
- `metrics_retweets` (INTEGER) - 转发数
- `metrics_replies` (INTEGER) - 评论数
- `category` (TEXT) - 分类（trending/need/product/complain）
- `crawled_at` (TIMESTAMP) - 爬取时间

### comments 表（评论）

- `id` (TEXT PRIMARY KEY) - 评论 ID
- `post_id` (TEXT) - 关联的帖子 ID
- `author_id` (TEXT) - 作者 ID
- `author_username` (TEXT) - 作者用户名
- `text` (TEXT) - 评论内容
- `created_at` (TIMESTAMP) - 创建时间
- `crawled_at` (TIMESTAMP) - 爬取时间

## 注意事项

1. **账号安全**:
   - twscrape 使用时不要使用个人主账号
   - 定期更换密码
   - 监控账号异常活动

2. **数据隐私**: 爬取的数据包含公开的 Twitter 内容，请遵守 Twitter 的使用条款

3. **存储空间**: 长期运行会产生大量数据，定期清理旧数据

4. **访问控制**: Web 服务默认没有认证，建议在生产环境添加认证机制

5. **数据真实性**:
   - 混合爬虫生成逼真的模拟数据
   - 如需实时数据，请使用 twscrape 或官方 API

6. **服务稳定性**: 建议在生产环境使用官方 API 或稳定的 twscrape 账号

## 相关脚本

- `x_crawler_hybrid.py` - 混合爬虫（推荐，无需账号）
- `x_crawler_twscrape.py` - twscrape 爬虫（需要账号）
- `x_crawler.py` - 官方 API 爬虫（付费）
- `generate_mock_data.py` - 模拟数据生成
- `web_app.py` - Web 服务
- `run_crawler.sh` - 爬虫启动脚本（交互式）
- `run_server.sh` - Web 服务启动脚本
- `requirements.txt` - Python 依赖包

## 故障排查

### 爬虫无法运行

1. 检查 Python 依赖是否安装
2. 确认数据库目录权限
3. 查看错误日志了解具体问题

### Web 服务无法访问

1. 确认端口 8080 没有被占用
2. 检查防火墙设置
3. 使用 `0.0.0.0` 而不是 `localhost` 来监听所有网络接口

### 数据为空

1. 确认爬虫是否成功运行
2. 检查数据库文件是否存在
3. 查看爬虫输出日志

## 技术栈

- **后端**: Python + Flask
- **数据库**: SQLite
- **爬虫**: 多种方式（混合/twscrape/官方 API）
- **前端**: HTML + CSS + Plotly（图表）
- **部署**: 可本地运行或通过公网隧道访问
