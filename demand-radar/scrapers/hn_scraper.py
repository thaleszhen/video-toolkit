"""
Hacker News API 数据采集
每小时运行一次，获取热门帖子和评论
"""
import requests
import logging
from datetime import datetime
from typing import List, Dict, Any
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HN_API_BASE = "https://hacker-news.firebaseio.com/v0"


class Demand:
    """简化的需求模型（用于独立运行）"""
    def __init__(self, **kwargs):
        self.title = kwargs.get("title", "")
        self.description = kwargs.get("description", "")
        self.category = kwargs.get("category", "")
        self.platform = kwargs.get("platform", "")
        self.source_url = kwargs.get("source_url", "")
        self.source_id = kwargs.get("source_id", "")
        self.author = kwargs.get("author", "")
        self.pain_points = kwargs.get("pain_points", [])
        self.purchase_signals = kwargs.get("purchase_signals", [])
        self.tech_keywords = kwargs.get("tech_keywords", [])
        self.confidence = kwargs.get("confidence", 0.0)
        self.engagement_score = kwargs.get("engagement_score", 0.0)
        self.score = kwargs.get("score", 0.0)
        self.status = kwargs.get("status", "new")
        self.published_at = kwargs.get("published_at", None)
        self.created_at = kwargs.get("created_at", datetime.utcnow())


def get_stories(story_type: str = "new", limit: int = 50) -> List[int]:
    """
    获取故事ID列表
    story_type: top/best/new/ask/show/job
    """
    url = f"{HN_API_BASE}/{story_type}stories.json"
    response = requests.get(url)
    response.raise_for_status()
    story_ids = response.json()[:limit]
    return story_ids


def get_story_detail(story_id: int) -> Dict[str, Any]:
    """获取单个故事的详情"""
    url = f"{HN_API_BASE}/item/{story_id}.json"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def extract_demand_signals(text: str) -> Dict[str, List[str]]:
    """
    从文本中提取需求信号
    """
    pain_keywords = [
        "why", "how", "need", "want", "looking for", "recommend",
        "difficult", "hard", "complex", "frustrating", "pain",
        "为什么", "怎么做", "需要", "想要", "寻找", "推荐", "太难用", "复杂"
    ]

    purchase_keywords = [
        "pay", "subscription", "price", "cost", "buy", "willing to pay",
        "付费", "订阅", "价格", "愿意", "多少钱"
    ]

    tech_keywords = [
        "api", "database", "frontend", "backend", "ml", "ai", "automation",
        "script", "tool", "app", "service", "saas",
        "API", "数据库", "自动化", "脚本", "工具"
    ]

    text_lower = text.lower()

    signals = {
        "pain_points": [],
        "purchase_signals": [],
        "tech_keywords": []
    }

    # 简单的关键词匹配（可以升级为NLP）
    words = text_lower.split()

    for keyword in pain_keywords:
        if keyword.lower() in text_lower:
            signals["pain_points"].append(keyword)

    for keyword in purchase_keywords:
        if keyword.lower() in text_lower:
            signals["purchase_signals"].append(keyword)

    for keyword in tech_keywords:
        if keyword.lower() in text_lower:
            signals["tech_keywords"].append(keyword)

    return signals


def calculate_engagement_score(story: Dict[str, Any]) -> float:
    """计算互动热度分数"""
    score = (story.get("score", 0) * 1.0 +
             story.get("descendants", 0) * 2.0)
    return min(score / 100.0, 1.0)  # 归一化到 0-1


def estimate_demand_confidence(title: str, text: str, signals: Dict[str, List[str]]) -> float:
    """
    估算需求置信度
    简单规则：有痛点 + 明确描述
    """
    combined_text = (title + " " + text).lower()
    confidence = 0.0

    # 有明确问题
    if signals["pain_points"]:
        confidence += 0.3

    # 提及技术/工具
    if signals["tech_keywords"]:
        confidence += 0.2

    # 标题长度适中（不是太短也不是太长）
    if 20 <= len(title) <= 150:
        confidence += 0.2

    # 文本长度充足
    if len(text) > 100:
        confidence += 0.2

    # 有提问标记
    if "?" in combined_text or "how" in combined_text or "怎么" in combined_text:
        confidence += 0.1

    return min(confidence, 1.0)


def process_story(story: Dict[str, Any]) -> Demand:
    """处理单个故事，返回Demand对象"""
    title = story.get("title", "")
    text = story.get("text", "")

    # 提取信号
    signals = extract_demand_signals(title + " " + (text or ""))

    # 计算分数
    engagement_score = calculate_engagement_score(story)
    confidence = estimate_demand_confidence(title, text or "", signals)

    # 简单分类
    category = "unknown"
    if "ask" in str(story.get("type", "")):
        category = "question"
    elif "show" in str(story.get("type", "")):
        category = "showcase"
    elif any(kw in title.lower() for kw in ["tool", "app", "service"]):
        category = "tool"

    demand = Demand(
        title=title[:500],
        description=text or "",
        category=category,
        platform="hn",
        source_url=story.get("url", ""),
        source_id=str(story.get("id")),
        author=story.get("by", ""),
        pain_points=signals["pain_points"],
        purchase_signals=signals["purchase_signals"],
        tech_keywords=signals["tech_keywords"],
        confidence=confidence,
        engagement_score=engagement_score,
        score=engagement_score * confidence,  # 简单的加权
        status="new",
        published_at=datetime.fromtimestamp(story.get("time", 0)),
        created_at=datetime.utcnow()
    )

    return demand


def fetch_and_store():
    """主函数：获取并存储Hacker News数据"""
    logger.info("🚀 开始获取 Hacker News 数据...")

    # 获取新的故事
    story_ids = get_stories(story_type="new", limit=100)
    logger.info(f"📊 找到 {len(story_ids)} 个新故事")

    # TODO: 连接数据库，检查是否已存在
    # from backend.app.config import SessionLocal
    # db = SessionLocal()

    new_demands = []
    skipped = 0

    for story_id in story_ids:
        try:
            story = get_story_detail(story_id)
            if not story:
                continue

            # 只处理有实际内容的故事
            if not story.get("title"):
                continue

            demand = process_story(story)
            new_demands.append(demand)

            logger.info(f"✅ 处理: {demand.title[:60]}... (score: {demand.score:.2f})")

            # 避免请求过快
            time.sleep(0.1)

        except Exception as e:
            logger.error(f"❌ 处理故事 {story_id} 失败: {e}")
            continue

    logger.info(f"📦 完成！获取 {len(new_demands)} 个需求，跳过 {skipped} 个")

    # TODO: 批量保存到数据库
    # db.add_all(new_demands)
    # db.commit()
    # db.close()

    return new_demands


if __name__ == "__main__":
    demands = fetch_and_store()
    print(f"\n=== 采样 5 条需求 ===")
    for d in demands[:5]:
        print(f"\n[{d.category}] {d.title}")
        print(f"   痛点: {d.pain_points}")
        print(f"   技术: {d.tech_keywords}")
        print(f"   置信度: {d.confidence:.2f} | 评分: {d.score:.2f}")
