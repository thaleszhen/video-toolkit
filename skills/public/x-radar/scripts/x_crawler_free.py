#!/usr/bin/env python3
"""
X (Twitter) Data Crawler - Free & No Account Required
使用公开 API 和多种前端实例抓取 Twitter/X 数据（无需账号）
"""

import os
import json
import sqlite3
import requests
from datetime import datetime
from typing import List, Dict
import re
import hashlib

DB_PATH = os.path.join(os.path.dirname(__file__), "../data/x_radar.db")

# 关键词分类
KEYWORDS = {
    "need": ["looking for", "need help", "any recommendations", "anyone knows", "suggest me"],
    "product": ["just launched", "new release", "introducing", "we're excited", "new app"],
    "complain": ["this sucks", "worst experience", "terrible", "so frustrating", "broken"]
}


class XCrawlerFree:
    """免费的 Twitter 爬虫（无需账号）"""

    def __init__(self):
        """初始化爬虫"""
        self.init_db()
        print("=" * 70)
        print("🚀 X RADAR - FREE CRAWLER (NO ACCOUNT REQUIRED)")
        print("=" * 70)

    def init_db(self):
        """初始化数据库"""
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id TEXT PRIMARY KEY,
                author_id TEXT,
                author_username TEXT,
                text TEXT,
                created_at TIMESTAMP,
                metrics_impressions INTEGER DEFAULT 0,
                metrics_likes INTEGER DEFAULT 0,
                metrics_retweets INTEGER DEFAULT 0,
                metrics_replies INTEGER DEFAULT 0,
                category TEXT,
                crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id TEXT PRIMARY KEY,
                post_id TEXT,
                author_id TEXT,
                author_username TEXT,
                text TEXT,
                created_at TIMESTAMP,
                crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts(id)
            )
        ''')

        conn.commit()
        conn.close()

    def _generate_tweet_id(self, text: str, username: str) -> str:
        """生成唯一的推文 ID"""
        content = f"{username}_{text[:100]}_{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def _fetch_from_search_engine(self, query: str, category: str, max_results: int = 30) -> List[Dict]:
        """从搜索引擎获取 Twitter 结果（备用方案）"""
        tweets = []
        try:
            # 使用 DuckDuckGo 搜索 Twitter
            search_url = f"https://api.duckduckgo.com/?q=site:twitter.com%20{query}&format=json"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(search_url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                results = data.get('RelatedTopics', []) + data.get('Results', [])

                for result in results[:max_results]:
                    try:
                        url = result.get('FirstURL', '')
                        text = result.get('Text', '')

                        if 'twitter.com' in url and text:
                            # 提取用户名
                            username_match = re.search(r'twitter\.com/(\w+)', url)
                            username = username_match.group(1) if username_match else 'unknown'

                            # 简化内容
                            clean_text = re.sub(r'\s+', ' ', text).strip()

                            if len(clean_text) > 10:
                                tweets.append({
                                    'id': self._generate_tweet_id(clean_text, username),
                                    'author_id': '',
                                    'author_username': username,
                                    'text': clean_text[:280],  # Twitter 字符限制
                                    'created_at': datetime.now().isoformat(),
                                    'metrics_impressions': 0,
                                    'metrics_likes': 0,
                                    'metrics_retweets': 0,
                                    'metrics_replies': 0,
                                    'category': category
                                })
                    except:
                        continue

        except Exception as e:
            print(f"   ⚠️  Search engine error: {e}")

        return tweets

    def get_trending_tweets(self, hours_back: int = 24, max_results: int = 50) -> List[Dict]:
        """获取热门推文（基于模拟，因为免费 API 限制）"""
        print("\n📊 Fetching trending tweets...")

        # 使用热门关键词模拟趋势
        trending_keywords = [
            "AI artificial intelligence trending",
            "tech innovation startup",
            "machine learning news",
            "software development trending"
        ]

        tweets = []
        for keyword in trending_keywords:
            results = self._fetch_from_search_engine(keyword, "trending", max_results // len(trending_keywords))
            tweets.extend(results)

        # 去重
        seen_ids = set()
        unique_tweets = []
        for tweet in tweets:
            if tweet['id'] not in seen_ids:
                seen_ids.add(tweet['id'])
                unique_tweets.append(tweet)

        print(f"   ✓ Found {len(unique_tweets)} trending tweets")
        return unique_tweets[:max_results]

    def get_category_tweets(self, category: str, hours_back: int = 24, max_results: int = 50) -> List[Dict]:
        """获取分类推文"""
        print(f"\n🔍 Fetching {category} tweets...")

        keywords = KEYWORDS.get(category, [])
        tweets = []

        for keyword in keywords:
            print(f"   Searching for '{keyword}'...")
            results = self._fetch_from_search_engine(keyword, category, max_results // len(keywords))
            tweets.extend(results)

        # 去重
        seen_ids = set()
        unique_tweets = []
        for tweet in tweets:
            if tweet['id'] not in seen_ids:
                seen_ids.add(tweet['id'])
                unique_tweets.append(tweet)

        print(f"   ✓ Found {len(unique_tweets)} {category} tweets")
        return unique_tweets[:max_results]

    def get_comments(self, post_id: str, max_results: int = 20) -> List[Dict]:
        """获取推文评论（免费方案不支持）"""
        return []

    def save_posts(self, posts: List[Dict]):
        """保存推文到数据库"""
        if not posts:
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        for post in posts:
            cursor.execute('''
                INSERT OR REPLACE INTO posts
                (id, author_id, author_username, text, created_at, metrics_impressions,
                 metrics_likes, metrics_retweets, metrics_replies, category)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                post['id'], post['author_id'], post['author_username'], post['text'],
                post['created_at'], post['metrics_impressions'], post['metrics_likes'],
                post['metrics_retweets'], post['metrics_replies'], post['category']
            ))

        conn.commit()
        conn.close()
        print(f"✓ Saved {len(posts)} posts to database")

    def save_comments(self, comments: List[Dict]):
        """保存评论到数据库"""
        pass

    def crawl_all(self, hours_back: int = 24):
        """爬取所有数据"""
        print("\n" + "=" * 70)
        print("📝 STARTING CRAWL")
        print("=" * 70)
        print("\n⚠️  Note: Free crawler uses search engines as data source.")
        print("   For better data quality, consider:")
        print("   • Using twscrape with Twitter accounts")
        print("   • Using official Twitter API (paid)")
        print("   • Generating mock data for testing")
        print("=" * 70)

        # 爬取热门推文
        trending = self.get_trending_tweets(hours_back)
        self.save_posts(trending)

        # 爬取需求推文
        need_posts = self.get_category_tweets("need", hours_back)
        self.save_posts(need_posts)

        # 爬取产品推文
        product_posts = self.get_category_tweets("product", hours_back)
        self.save_posts(product_posts)

        # 爬取抱怨推文
        complain_posts = self.get_category_tweets("complain", hours_back)
        self.save_posts(complain_posts)

        print("\n" + "=" * 70)
        print("✅ CRAWL COMPLETED!")
        print("=" * 70)

        # 统计
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        total_posts = cursor.execute("SELECT COUNT(*) FROM posts").fetchone()[0]

        by_category = {}
        for category in ['trending', 'need', 'product', 'complain']:
            count = cursor.execute(
                "SELECT COUNT(*) FROM posts WHERE category = ?",
                (category,)
            ).fetchone()[0]
            by_category[category] = count

        print(f"\n📊 Statistics:")
        print(f"   Total posts: {total_posts}")
        for cat, count in by_category.items():
            print(f"   {cat}: {count}")
        print("=" * 70)


def main():
    """主函数"""
    crawler = XCrawlerFree()
    crawler.crawl_all(hours_back=24)


if __name__ == "__main__":
    main()
