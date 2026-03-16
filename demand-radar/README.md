# Demand Radar - 需求挖掘平台

从社交媒体和社区挖掘用户需求，帮助个人开发者发现可变现的机会。

## 项目结构

```
demand-radar/
├── backend/          # FastAPI 后端
├── frontend/        # Next.js 前端
├── scrapers/        # 数据采集脚本
├── nlp/            # NLP 处理模块
└── docker-compose.yml
```

## 快速启动

### 方式一：使用脚本一键配置（推荐）

```bash
cd demand-radar
./setup.sh
```

### 方式二：Docker 一键启动

```bash
cd demand-radar
docker-compose up
```

然后访问:
- 前端: http://localhost:3000
- API: http://localhost:8000
- API 文档: http://localhost:8000/docs

### 方式三：手动启动

#### 1. 启动后端
```bash
cd backend
pip3 install -r requirements.txt
cp .env.example .env  # 编辑 .env 添加 API Keys
python3 -m app.main
```

#### 2. 查看前端
```bash
# 直接在浏览器打开
open frontend/index.html
# 或使用简单 HTTP 服务器
cd frontend && python3 -m http.server 3000
```

#### 3. 运行采集器（测试）
```bash
cd scrapers
python3 hn_scraper.py  # Hacker News
```

## 数据源

- ✅ Hacker News API
- 🚧 Reddit API (需要配置)
- 🚧 V2EX (爬虫，注意反爬)
- 🚧 知乎 (爬虫)

## 技术栈

- 后端: FastAPI + SQLAlchemy + Qdrant
- 前端: Next.js + TailwindCSS
- NLP: OpenAI API / Sentence-Transformers
- 部署: Railway / Render / Docker

## 开发路线

- [x] 项目骨架
- [ ] Hacker News 采集
- [ ] 基础需求分类
- [ ] 需求去重
- [ ] 简单评分模型
- [ ] Web Dashboard
- [ ] 用户认证
- [ ] 更多数据源
