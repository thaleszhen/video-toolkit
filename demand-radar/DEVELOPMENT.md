# 开发指南

## 本地开发环境

### 必需工具

- Python 3.10+
- PostgreSQL 15+ (或使用 SQLite 开发)
- Redis 7+ (可选，用于任务队列)
- Docker & Docker Compose (可选)

### 快速开始

1. **克隆项目**
```bash
git clone <repo-url>
cd demand-radar
```

2. **运行配置脚本**
```bash
./setup.sh
```

3. **配置环境变量**
```bash
cd backend
cp .env.example .env
# 编辑 .env 添加你的 API Keys
```

4. **启动服务**
```bash
# 使用 Docker (推荐)
docker-compose up

# 或手动启动
cd backend && python3 -m app.main
```

## 项目结构详解

```
demand-radar/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── main.py           # API 入口
│   │   ├── config.py         # 配置管理
│   │   ├── models/           # 数据模型
│   │   │   └── database.py   # SQLAlchemy 模型
│   │   └── services/         # 业务逻辑 (待添加)
│   ├── requirements.txt      # Python 依赖
│   ├── .env.example          # 环境变量模板
│   └── Dockerfile           # Docker 配置
├── frontend/                  # 前端
│   └── index.html           # 简化版静态页面 (可升级为 Next.js)
├── scrapers/                 # 数据采集脚本
│   ├── hn_scraper.py        # Hacker News 采集器 (✅ 可用)
│   └── reddit_scraper.py   # Reddit 采集器 (待开发)
├── nlp/                      # NLP 处理模块 (待开发)
├── docker-compose.yml       # Docker 编排配置
└── README.md                # 项目说明
```

## API 端点

### 健康检查
```http
GET /health
```

### 获取需求列表
```http
GET /api/demands?limit=50&offset=0
```

### 分析需求
```http
POST /api/demands/analyze
Content-Type: application/json

{
  "text": "我希望有一个能自动整理邮件的工具"
}
```

响应示例:
```json
{
  "is_demand": true,
  "category": "tool",
  "confidence": 0.85,
  "signals": {
    "pain_points": ["希望", "自动整理"],
    "tech_keywords": ["工具"],
    "purchase_signals": []
  }
}
```

## 数据采集器开发

### 添加新平台采集器

1. 在 `scrapers/` 目录创建新文件，如 `platform_scraper.py`
2. 实现以下函数:

```python
import requests
from datetime import datetime

def fetch_posts(limit=100):
    """获取帖子列表"""
    pass

def extract_signals(text):
    """提取需求信号"""
    pass

def process_post(post):
    """处理单个帖子"""
    pass

def main():
    """主函数"""
    posts = fetch_posts()
    for post in posts:
        demand = process_post(post)
        # TODO: 保存到数据库
```

3. 集成到定时任务 (Celery 或 Cron)

## NLP 模型开发

### 当前状态

- **关键词匹配**: 已实现，简单快速
- **LLM 分类**: 计划使用 OpenAI API
- **向量化**: 计划使用 Sentence-Transformers

### 集成 OpenAI

```python
from openai import OpenAI

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def classify_demand(text):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "你是一个需求分类专家。判断文本是否包含用户需求。"
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )
    return response.choices[0].message
```

### 需求去重

使用 Qdrant 向量数据库实现语义去重:

```python
from qdrant_client import QdrantClient

client = QdrantClient(url=settings.QDRANT_URL)

def find_similar_demands(text, limit=5):
    """查找相似需求"""
    # 1. 将文本转换为向量
    embedding = get_embedding(text)

    # 2. 搜索相似向量
    results = client.search(
        collection_name="demands",
        query_vector=embedding,
        limit=limit,
        score_threshold=0.85  # 相似度阈值
    )

    return results
```

## 数据库迁移

使用 Alembic 管理数据库迁移:

```bash
# 创建迁移
alembic revision --autogenerate -m "Add new field"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

## 部署

### Railway

1. 连接 GitHub 仓库
2. 设置环境变量
3. 部署后端 + PostgreSQL

### Render

1. 创建 Web Service (后端)
2. 创建 PostgreSQL
3. 添加环境变量

### VPS / Docker

```bash
# 拉取代码
git clone <repo>
cd demand-radar

# 配置环境
cp backend/.env.example backend/.env
nano backend/.env  # 编辑配置

# 启动
docker-compose up -d
```

## 调试技巧

### 查看日志
```bash
# Docker
docker-compose logs -f backend

# 手动运行
python3 -m app.main  # 直接在终端查看输出
```

### 测试采集器
```bash
cd scrapers
python3 hn_scraper.py
```

### 测试 API
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/demands?limit=10
```

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 下一步

- [ ] 实现完整的需求评分模型
- [ ] 添加 Reddit 采集器
- [ ] 集成 LLM 进行需求分类
- [ ] 实现需求去重和聚类
- [ ] 添加用户认证系统
- [ ] 实现高级筛选和搜索
- [ ] 添加需求趋势分析
- [ ] 创建完整的 Next.js 前端

## 常见问题

### Q: 为什么用 SQLite 而不是 PostgreSQL?
A: SQLite 是默认配置，开发环境更简单。生产环境建议使用 PostgreSQL。

### Q: 如何切换到 PostgreSQL?
A: 修改 `backend/.env` 中的 `DATABASE_URL`:
```
DATABASE_URL=postgresql://user:password@localhost:5432/demand_radar
```

### Q: 采集器可以自动运行吗?
A: 可以使用 Celery + Beat 定时任务，或者系统的 Cron。

### Q: 为什么评分这么低?
A: 当前使用简单的加权公式。后续会引入更复杂的模型。

### Q: 如何提高需求识别准确率?
A:
1. 调整关键词列表
2. 使用 LLM 进行二次验证
3. 收集用户反馈进行微调
