"""
App Store 评论采集
从 App Store 挖掘用户需求和痛点
"""
import requests
import logging
from datetime import datetime
from typing import List, Dict
import sys
sys.path.append('..')
from config import CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# App Store API (第三方免费 API)
APP_STORE_API_BASE = "https://itunes.apple.com/search"


def search_apps(category: str, limit: int = 20) -> List[Dict]:
    """
    搜索应用

    Args:
        category: 应用分类
        limit: 返回数量

    Returns:
        应用列表
    """
    keywords_map = {
        "productivity": "productivity",
        "business": "business",
        "finance": "finance"
    }

    keyword = keywords_map.get(category, category)

    params = {
        "term": keyword,
        "media": "software",
        "limit": limit
    }

    try:
        response = requests.get(APP_STORE_API_BASE, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        apps = []
        for app in data.get("results", []):
            apps.append({
                "id": app["trackId"],
                "name": app["trackName"],
                "description": app.get("description", "")[:300],
                "seller": app["sellerName"],
                "rating": app.get("averageUserRating", 0),
                "review_count": app.get("userRatingCount", 0),
                "price": app.get("price", 0),
                "category": app.get("primaryGenreName", "Unknown")
            })

        logger.info(f"✅ 从 App Store 获取 {len(apps)} 个 {category} 应用")
        return apps

    except Exception as e:
        logger.error(f"❌ 搜索 App Store 失败: {e}")
        return []


def get_app_reviews(app_id: str, limit: int = 50) -> List[Dict]:
    """
    获取应用评论

    Args:
        app_id: 应用 ID
        limit: 评论数量

    Returns:
        评论列表
    """
    # 使用 RSS 获取评论（免费方式）
    rss_url = f"https://itunes.apple.com/us/rss/customerreviews/id={app_id}/sortBy=mostRecent/json"

    try:
        response = requests.get(rss_url, timeout=30)
        response.raise_for_status()
        data = response.json()

        reviews = []
        for entry in data.get("feed", {}).get("entry", []):
            if "author" not in entry:
                continue

            review = entry.get("content", {}).get("label", "")

            # 提取评分
            rating = 0
            rating_elem = entry.get("im:rating")
            if rating_elem:
                rating = int(rating_elem.get("attributes", {}).get("im:rating", "0"))

            # 提取标题
            title = entry.get("title", {}).get("label", "")

            # 提取作者
            author = entry.get("author", {}).get("name", {}).get("label", "Unknown")

            # 提取日期
            updated = entry.get("updated", {}).get("label", "")
            created_at = datetime.fromisoformat(updated.replace("Z", "+00:00")).isoformat() if updated else datetime.now().isoformat()

            reviews.append({
                "id": entry.get("id", {}).get("label", ""),
                "app_id": app_id,
                "title": title,
                "content": review,
                "rating": rating,
                "author": author,
                "created_at": created_at
            })

        logger.info(f"✅ 获取 {len(reviews)} 条评论")
        return reviews[:limit]

    except Exception as e:
        logger.error(f"❌ 获取评论失败: {e}")
        return []


def extract_pain_points(review: Dict) -> List[str]:
    """
    从评论中提取痛点

    Returns:
        痛点列表
    """
    content = (review["title"] + " " + review["content"]).lower()

    pain_keywords = [
        ("bug", "bug", "崩溃", "crash", "error", "doesn't work"),
        ("慢", "slow", "慢", "卡顿", "lag", "卡"),
        ("贵", "expensive", "太贵", "price", "cost", "pricing"),
        ("难用", "difficult", "complicated", "confusing", "难", "复杂"),
        ("广告", "ads", "ad", "广告", "太多广告"),
        ("功能", "feature", "功能缺失", "missing", "缺少"),
        ("客服", "support", "customer service", "客服", "支持"),
        ("同步", "sync", "同步", "data loss", "数据丢失")
    ]

    pain_points = []
    for category, keywords in pain_keywords:
        for keyword in keywords:
            if keyword in content:
                pain_points.append(f"{category}: {keyword}")

    return list(set(pain_points))


def analyze_review(review: Dict, app_name: str) -> Dict:
    """
    分析评论，判断是否为需求

    Returns:
        分析结果
    """
    pain_points = extract_pain_points(review)

    # 判断是否为负面评论（有痛点）
    is_negative = len(pain_points) > 0 or review["rating"] <= 2

    # 判断是否为功能请求
    content = (review["title"] + " " + review["content"]).lower()
    feature_request_keywords = ["wish", "hope", "need", "希望", "需要", "建议", "suggestion"]
    is_feature_request = any(kw in content for kw in feature_request_keywords)

    # 计算置信度
    confidence = 0
    if is_negative:
        confidence += 0.4
    if is_feature_request:
        confidence += 0.3
    if review["rating"] <= 2:
        confidence += 0.3

    return {
        "source": "app_store",
        "source_id": review["id"],
        "title": f"{app_name} - {review['title']}",
        "description": review["content"],
        "url": f"https://apps.apple.com/us/app/id{review['app_id']}",
        "author": review["author"],
        "app_name": app_name,
        "rating": review["rating"],
        "is_demand": is_negative or is_feature_request,
        "confidence": min(confidence, 1.0),
        "pain_points": pain_points[:5],
        "created_at": review["created_at"]
    }


def fetch_app_store_demands() -> List[Dict]:
    """
    从 App Store 获取需求

    Returns:
        需求列表
    """
    config = CONFIG["sources"]["app_store"]
    if not config["enabled"]:
        logger.info("⚠️  App Store 数据源未启用")
        return []

    logger.info("🚀 开始从 App Store 获取数据...")

    all_demands = []
    seen_ids = set()

    # 搜索应用
    apps = search_apps("productivity", limit=10)

    for app in apps:
        if app["id"] in seen_ids:
            continue
        seen_ids.add(app["id"])

        # 获取评论
        reviews = get_app_reviews(app["id"], limit=20)

        for review in reviews:
            if review["id"] in seen_ids:
                continue
            seen_ids.add(review["id"])

            # 分析评论
            analysis = analyze_review(review, app["name"])

            # 只保留真正的需求
            if analysis["is_demand"] and analysis["confidence"] >= 0.6:
                all_demands.append(analysis)

        logger.info(f"📊 从 {app['name']} 发现 {len([d for d in all_demands if d.get('app_name') == app['name']])} 个需求")

    logger.info(f"✅ 总共发现 {len(all_demands)} 个需求")
    return all_demands


if __name__ == "__main__":
    demands = fetch_app_store_demands()

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
            print(f"   应用: {d.get('app_name', 'Unknown')}")
            print(f"   评分: {d.get('rating', 0)}/5")
            print(f"   置信度: {d['confidence']:.2f}")
            print(f"   痛点: {', '.join(d['pain_points'][:3])}")
    else:
        print("⚠️  未发现任何需求")
