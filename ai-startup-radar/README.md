# 🔍 AI 创业雷达

每天自动从多个平台挖掘用户需求和创业机会，输出 Top 5 需求和 Top 3 产品想法。

## 🎯 功能特点

- **多平台采集**：Reddit、App Store、Amazon、Twitter
- **智能分析**：自动识别痛点、付费信号、技术关键词
- **需求评分**：综合置信度、互动度、机会评分
- **产品建议**：基于需求自动生成可做的产品想法
- **日报生成**：每天输出 Markdown 格式分析报告

## 📁 项目结构

```
ai-startup-radar/
├── config.py              # 配置文件
├── scripts/               # 脚本目录
│   ├── reddit_scraper.py       # Reddit 采集器
│   ├── app_store_scraper.py    # App Store 采集器
│   ├── analyze.py             # 需求分析和产品生成
│   └── daily_task.py          # 每日定时任务
├── data/                  # 数据存储
│   ├── demands_2026-03-15.json
│   └── products_2026-03-15.json
├── reports/               # 报告输出
│   └── report_2026-03-15.md
└── README.md              # 项目说明
```

## 🚀 快速开始

### 1. 安装依赖

```bash
cd ai-startup-radar
pip install requests python-dotenv
```

### 2. 配置数据源

编辑 `config.py`，启用/禁用数据源：

```python
CONFIG = {
    "sources": {
        "reddit": {
            "enabled": True,  # 启用 Reddit
            "subreddits": ["startups", "SaaS", "entrepreneur"]
        },
        "app_store": {
            "enabled": False,  # 需要 API key 才能启用
            "apps": ["productivity", "business"]
        }
        # ...
    }
}
```

### 3. 运行单个采集器

```bash
# 采集 Reddit 数据
python scripts/reddit_scraper.py

# 采集 App Store 数据
python scripts/app_store_scraper.py
```

### 4. 运行完整流程

```bash
# 运行每日任务（采集 + 分析 + 报告）
python scripts/daily_task.py

# 或单独运行分析
python scripts/analyze.py
```

### 5. 查看报告

报告会保存在 `reports/report_YYYY-MM-DD.md`

```bash
cat reports/report_$(date +%Y-%m-%d).md
```

## 📊 数据源说明

### Reddit ✅（已启用）

- **Subreddits**: startups, SaaS, entrepreneur, smallbusiness, ProductHunt
- **获取内容**: 帖子标题、文本、分数、评论数
- **分析维度**: 痛点、付费信号、技术关键词
- **API**: 免费，无需认证

### App Store ⚠️（实验性）

- **应用分类**: productivity, business, finance
- **获取内容**: 应用信息、评论
- **分析维度**: 负面评价、功能请求
- **API**: iTunes Search API（免费但有限制）

### Amazon ❌（待开发）

- **商品分类**: software, electronics
- **获取内容**: 商品评论
- **分析维度**: 投诉、需求建议
- **API**: 需要爬虫方案

### Twitter ❌（待开发）

- **关键词**: need, looking for, wish there was, frustrated with
- **获取内容**: 推文、转发、点赞
- **分析维度**: 实时需求、痛点
- **API**: Twitter API v2（需要认证）

## 🎯 每日输出

### Top 5 真实需求

每个需求包含：

- **标题**：需求描述
- **来源**：数据平台
- **置信度**：需求真实性评分（0-1）
- **机会分数**：综合评分（热度 + 付费信号）
- **痛点**：用户痛点标签
- **付费信号**：购买意愿标识
- **技术关键词**：相关技术栈

### Top 3 产品想法

每个产品包含：

- **产品名称**：建议的产品名称
- **类型**：工具/SaaS/自动化/API
- **目标用户**：目标用户群体
- **变现方式**：订阅/按次/免费+付费
- **难度评估**：开发难度（简单/中等/困难）
- **预计开发时间**：MVP 开发时间估算
- **技术栈**：推荐技术栈
- **MVP 功能**：最小可行产品功能

## ⚙️ 配置选项

### 输出配置

```python
"output": {
    "demands_count": 5,      # 每天输出的需求数量
    "products_count": 3,      # 每天输出的产品想法数量
    "report_dir": "reports",   # 报告保存目录
    "data_dir": "data"        # 数据保存目录
}
```

### AI 分析配置

```python
"ai_analysis": {
    "enabled": True,
    "min_confidence": 0.7,        # 最低置信度阈值
    "check_duplicates": True,        # 检测重复需求
    "identify_opportunities": True   # 识别产品机会
}
```

## 🕒 定时任务设置

### 使用 Cron（Linux/Mac）

```bash
# 每天早上 8:00 运行
0 8 * * * /path/to/ai-startup-radar/scripts/daily_task.py

# 或每小时运行（测试用）
0 * * * * /path/to/ai-startup-radar/scripts/daily_task.py
```

### 使用 Windows 任务计划程序

```batch
schtasks /create /tn "AI Startup Radar" /tr "python3 C:\path\to\daily_task.py" /sc daily /st 08:00
```

## 🔧 扩展开发

### 添加新的数据源

1. 在 `scripts/` 创建新的采集器
2. 实现相同接口：`fetch_*_demands()` 返回需求列表
3. 在 `config.py` 添加配置
4. 在 `daily_task.py` 注册新采集器

### 改进需求分析

修改 `scripts/analyze.py` 中的：

- `score_demands()`: 调整评分算法
- `identify_product_opportunities()`: 改进产品识别逻辑
- `generate_product_details()`: 丰富产品详情

### 添加通知渠道

修改 `scripts/daily_task.py` 中的 `send_notification()`：

- Email: 使用 `smtplib`
- Slack: 发送 Webhook
- Telegram: 使用 Bot API
- Discord: 发送 Webhook

## 📈 后续计划

- [ ] 集成真实 AI API（OpenAI/Claude）
- [ ] 添加 Amazon 评论采集
- [ ] 添加 Twitter 实时采集
- [ ] 实现需求去重和聚类
- [ ] 添加用户反馈收集
- [ ] 构建可视化 Dashboard
- [ ] 多语言支持（英文报告）
- [ ] 需求趋势分析（周/月）

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 License

MIT License

---

**Made with ❤️ by AI Startup Radar Team**
