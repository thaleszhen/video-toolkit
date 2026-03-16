"""
Reddit 数据采集
从 Reddit 挖掘用户需求和创业机会
"""
import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict
import sys
sys.path.append('..')
from config import CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REDDIT_API_BASE = "https://www.reddit.com"
USER_AGENT = "AIStartupRadar/0.1"


def get_subreddit_posts(subreddit: str, limit: int = 50) -> List[Dict]:
    """
    获取 subreddit 的新帖子

    Args:
        subreddit: subreddit 名称
        limit: 获取数量

    Returns:
        帖子列表
    """
    url = f"{REDDIT_API_BASE}/r/{subreddit}/new.json"
    headers = {"User-Agent": USER_AGENT}

    try:
        response = requests.get(url, headers=headers, params={"limit": limit}, timeout=30)
        response.raise_for_status()
        data = response.json()

        posts = []
        for post in data["data"]["children"]:
            post_data = post["data"]
            posts.append({
                "id": post_data["id"],
                "title": post_data["title"],
                "selftext": post_data.get("selftext", ""),
                "author": post_data["author"],
                "subreddit": post_data["subreddit"],
                "score": post_data["score"],
                "num_comments": post_data["num_comments"],
                "created_utc": post_data["created_utc"],
                "url": post_data["url"],
                "is_self": post_data["is_self"]
            })

        logger.info(f"✅ 从 r/{subreddit} 获取 {len(posts)} 条帖子")
        return posts

    except Exception as e:
        logger.error(f"❌ 获取 r/{subreddit} 失败: {e}")
        return []


def extract_demand_signals(post: Dict) -> Dict:
    """
    从帖子中提取需求信号

    Returns:
        信号字典
    """
    title = post["title"].lower()
    text = post.get("selftext", "").lower()
    combined = f"{title} {text}"

    signals = {
        "pain_points": [],
        "purchase_signals": [],
        "tech_keywords": [],
        "opportunity_score": 0
    }

    # 痛点关键词
    pain_keywords = [
        "frustrating", "painful", "hate", "struggling", "difficult",
        "为什么", "太难用", "痛苦", "困扰", "麻烦", "复杂",
        "annoying", "problem", "issue", "can't", "unable to",
        "没办法", "解决不了", "烦", "累"
    ]

    # 付费信号
    purchase_keywords = [
        "willing to pay", "looking for", "need", "buy", "subscribe",
        "愿意付费", "寻找", "需要购买", "订阅", "多少钱",
        "budget", "pricing", "pay for", "付费"
    ]

    # 技术关键词
    tech_keywords = [
        "api", "saas", "app", "tool", "software", "automation",
        "ai", "ml", "chatgpt", "gpt", "python", "javascript",
        "web", "mobile", "ios", "android", "extension",
        "插件", "脚本", "工具", "自动化"
    ]

    # 提取信号
    for keyword in pain_keywords:
        if keyword in combined:
            signals["pain_points"].append(keyword)

    for keyword in purchase_keywords:
        if keyword in combined:
            signals["purchase_signals"].append(keyword)

    for keyword in tech_keywords:
        if keyword in combined:
            signals["tech_keywords"] = signals.get("tech_keywords", [])
            signals["tech_keywords"].append(keyword)

    # 计算机会分数
    score = post["score"]
    comments = post["num_comments"]
    signals["opportunity_score"] = (score * 0.6) + (comments * 0.4)

    return signals


def analyze_post(post: Dict) -> Dict:
    """
    分析帖子，判断是否为需求

    Returns:
        分析结果
    """
    signals = extract_demand_signals(post)

    # 判断是否为需求
    is_demand = len(signals["pain_points"]) > 0 or len(signals["purchase_signals"]) > 0

    # 置信度
    confidence = 0
    if is_demand:
        confidence = 0.5
        if len(signals["pain_points"]) >= 2:
            confidence += 0.2
        if len(signals["purchase_signals"]) >= 1:
            confidence += 0.2
        if len(signals["tech_keywords"]) >= 1:
            confidence += 0.1

    return {
        "source": "reddit",
        "source_id": post["id"],
        "title": post["title"],
        "description": post.get("selftext", "")[:500],
        "url": post["url"],
        "author": post["author"],
        "subreddit": post["subreddit"],
        "is_demand": is_demand,
        "confidence": min(confidence, 1.0),
        "opportunity_score": signals["opportunity_score"],
        "pain_points": signals["pain_points"][:5],  # 最多 5 个
        "purchase_signals": signals["purchase_signals"][:3],
        "tech_keywords": signals["tech_keywords"][:5],
        "score": post["score"],
        "num_comments": post["num_comments"],
        "created_at": datetime.fromtimestamp(post["created_utc"]).isoformat()
    }


def fetch_reddit_demands() -> List[Dict]:
    """
    从 Reddit 获取需求

    Returns:
        需求列表
    """
    config = CONFIG["sources"]["reddit"]
    if not config["enabled"]:
        logger.info("⚠️  Reddit 数据源未启用")
        return []

    logger.info("🚀 开始从 Reddit 获取数据...")

    all_demands = []
    seen_ids = set()

    for subreddit in config["subreddits"]:
        posts = get_subreddit_posts(subreddit, limit=50)

        for post in posts:
            # 去重
            if post["id"] in seen_ids:
                continue
            seen_ids.add(post["id"])

            # 分析帖子
            analysis = analyze_post(post)

            # 只保留真正的需求
            if analysis["is_demand"] and analysis["confidence"] >= 0.7:
                all_demands.append(analysis)

        logger.info(f"📊 从 r/{subreddit} 发现 {len([d for d in all_demands if d['subreddit'] == subreddit])} 个需求")

    # 按机会分数排序
    all_demands.sort(key=lambda x: x["opportunity_score"], reverse=True)

    logger.info(f"✅ 总共发现 {len(all_demands)} 个需求")
    return all_demands


if __name__ == "__main__":
    demands = fetch_reddit_demands()

    # 保存结果
    from config import save_demands, ensure_dirs
    ensure_dirs()

    if demands:
        save_demands(demands)
        print(f"\n✅ 已保存 {len(demands)} 个需求到 data/demands_*.json")

        # 打印前 5 个
        print("\n🔍 Top 5 需求:")
        for i, d in enumerate(demands[:5], 1):
            print(f"\n{i}. {d['title']}")
            print(f"   来源: r/{d['subreddit']}")
            print(f"   置信度: {d['confidence']:.2f} | 机会分数: {d['opportunity_score']:.1f}")
            print(f"   痛点: {', '.join(d['pain_points'][:3])}")
    else:
        print("⚠️  未发现任何需求")
