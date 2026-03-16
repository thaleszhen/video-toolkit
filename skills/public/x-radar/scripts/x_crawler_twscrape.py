#!/usr/bin/env python3
"""
X (Twitter) Data Crawler using twscrape
使用免费的 Twitter Web API 爬取 Twitter/X 数据
"""

import os
import json
import sqlite3
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict
import twscrape

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), "../data/x_radar.db")

# 关键词分类（优化后的搜索词）
KEYWORDS = {
    "need": [
        "looking for", "need help", "any recommendations", "anyone knows",
        "suggest me", "best tool for", "how do I"
    ],
    "product": [
        "just launched", "new release", "introducing", "we're excited to announce",
        "new app", "beta launch", "product launch", "finally released"
    ],
    "complain": [
        "this sucks", "worst experience", "terrible", "so frustrating",
        "why does this", "this is broken", "never working"
    ]
}


class XCrawlerTwscrape:
    def __init__(self):
        """初始化爬虫"""
        self.client = None
        self.accounts = []
        self.init_db()
        self.load_accounts()

        if self.accounts:
            self.client = twscrape.API()
            print(f"✓ Loaded {len(self.accounts)} Twitter account(s)")

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

    def load_accounts(self):
        """加载账号配置"""
        accounts_file = os.path.join(os.path.dirname(__file__), "../data/accounts.json")

        if os.path.exists(accounts_file):
            try:
                with open(accounts_file, 'r') as f:
                    self.accounts = json.load(f)
            except Exception as e:
                print(f"✗ Error loading accounts: {e}")

        if not self.accounts:
            self._show_setup_instructions()

    def _show_setup_instructions(self):
        """显示设置说明"""
        print("=" * 70)
        print("❌ NO TWITTER ACCOUNTS CONFIGURED")
        print("=" * 70)
        print("\nTo use twscrape crawler, you need to add Twitter accounts:")
        print("\n1. Create data/accounts.json with this format:")
        print("""
[
    {
        "username": "your_twitter_username",
        "password": "your_password",
        "email": "your_email@example.com",
        "email_password": "your_email_password"
    }
]
        """)
        print("\n2. Best practices:")
        print("   • Use aged accounts (created > 6 months ago)")
        print("   • Don't use your main personal account")
        print("   • Add multiple accounts to distribute load")
        print("   • Keep accounts active (post tweets occasionally)")
        print("\n3. Alternative: Use mock data for testing")
        print("   Run: python3 generate_mock_data.py")
        print("\n" + "=" * 70)

    async def _init_accounts(self):
        """初始化账号到 twscrape"""
        for i, acc in enumerate(self.accounts, 1):
            try:
                await self.client.add_account(
                    acc['username'],
                    acc['password'],
                    acc.get('email'),
                    acc.get('email_password')
                )
                print(f"  ✓ Added account {i}: @{acc['username']}")
            except Exception as e:
                print(f"  ✗ Failed to add account {i}: {e}")

    async def search_tweets(
        self,
        query: str,
        category: str,
        max_results: int = 100
    ) -> List[Dict]:
        """搜索推文"""
        if not self.client:
            return []

        tweets = []
        try:
            print(f"   Searching for '{query}'...")

            # 构建搜索查询
            search_query = f"{query} lang:en OR lang:zh -is:retweet"

            count = 0
            async for tweet in self.client.search(search_query, limit=max_results):
                tweets.append({
                    'id': str(tweet.id),
                    'author_id': str(tweet.user.id),
                    'author_username': tweet.user.username,
                    'text': tweet.rawContent or '',
                    'created_at': tweet.date.isoformat() if tweet.date else None,
                    'metrics_impressions': 0,
                    'metrics_likes': tweet.likeCount or 0,
                    'metrics_retweets': tweet.retweetCount or 0,
                    'metrics_replies': tweet.replyCount or 0,
                    'category': category
                })
                count += 1

            print(f"   ✓ Found {count} tweets for '{query}'")

        except Exception as e:
            print(f"   ✗ Error searching '{query}': {e}")

        return tweets

    async def get_trending_tweets(self, hours_back: int = 24, max_results: int = 100) -> List[Dict]:
        """获取热门推文"""
        if not self.client:
            return []

        tweets = []

        # 搜索多个热门话题
        trending_queries = [
            "AI", "artificial intelligence", "machine learning",
            "startup", "tech", "innovation", "software"
        ]

        for query in trending_queries:
            results = await self.search_tweets(query, "trending", max_results // len(trending_queries))
            tweets.extend(results)

        # 按点赞数 + 回复数排序
        tweets.sort(key=lambda x: x['metrics_likes'] + x['metrics_replies'], reverse=True)
        return tweets[:max_results]

    async def get_category_tweets(self, category: str, hours_back: int = 24, max_results: int = 100) -> List[Dict]:
        """获取分类推文"""
        if not self.client:
            return []

        keywords = KEYWORDS.get(category, [])
        tweets = []

        for keyword in keywords:
            tweets.extend(await self.search_tweets(keyword, category, max_results // len(keywords)))

        # 按点赞数排序
        tweets.sort(key=lambda x: x['metrics_likes'], reverse=True)
        return tweets

    async def get_comments(self, post_id: str, max_results: int = 50) -> List[Dict]:
        """获取推文评论"""
        if not self.client:
            return []

        comments = []
        try:
            print(f"   Fetching comments for tweet {post_id}...")

            # 搜索对该推文的回复
            query = f"to:@{post_id.split('_')[0]}" if '_' in post_id else f"reply to tweet"
            count = 0

            async for tweet in self.client.search(query, limit=max_results):
                comments.append({
                    'id': str(tweet.id),
                    'post_id': post_id,
                    'author_id': str(tweet.user.id),
                    'author_username': tweet.user.username,
                    'text': tweet.rawContent or '',
                    'created_at': tweet.date.isoformat() if tweet.date else None
                })
                count += 1

            print(f"   ✓ Found {count} comments")

        except Exception as e:
            print(f"   ✗ Error fetching comments: {e}")

        return comments

    def save_posts(self, posts: List[Dict]):
        """保存推文到数据库"""
        if not posts:
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        for post in posts:
            cursor.execute('''
                INSERT OR REPLACE INTO posts
                (id, author_id, author_username, text, created_at,
                 metrics_impressions, metrics_likes, metrics_retweets, metrics_replies, category)
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
        if not comments:
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        for comment in comments:
            cursor.execute('''
                INSERT OR REPLACE INTO comments
                (id, post_id, author_id, author_username, text, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                comment['id'], comment['post_id'], comment['author_id'],
                comment['author_username'], comment['text'], comment['created_at']
            ))

        conn.commit()
        conn.close()
        print(f"✓ Saved {len(comments)} comments to database")

    async def crawl_all(self, hours_back: int = 24):
        """爬取所有数据"""
        print("\n" + "=" * 60)
        print("🚀 STARTING TWITTER CRAWL WITH TWSCRAPE")
        print("=" * 60)

        if not self.accounts:
            print("\n❌ No accounts configured. Exiting.")
            return

        # 初始化账号
        print("\n📝 Initializing accounts...")
        await self._init_accounts()

        # 爬取热门推文
        print("\n📊 Fetching trending tweets...")
        trending = await self.get_trending_tweets(hours_back)
        self.save_posts(trending)

        # 为热门推文获取评论
        print("\n💬 Fetching comments for top tweets...")
        for post in trending[:20]:
            comments = await self.get_comments(post['id'])
            self.save_comments(comments)

        # 爬取需求推文
        print("\n🔍 Fetching need tweets...")
        need_posts = await self.get_category_tweets("need", hours_back)
        self.save_posts(need_posts)

        # 爬取产品推文
        print("\n🚀 Fetching product tweets...")
        product_posts = await self.get_category_tweets("product", hours_back)
        self.save_posts(product_posts)

        # 爬取抱怨推文
        print("\n😤 Fetching complain tweets...")
        complain_posts = await self.get_category_tweets("complain", hours_back)
        self.save_posts(complain_posts)

        print("\n" + "=" * 60)
        print("✅ CRAWL COMPLETED SUCCESSFULLY!")
        print("=" * 60)


async def main():
    """主函数"""
    crawler = XCrawlerTwscrape()
    await crawler.crawl_all(hours_back=24)


if __name__ == "__main__":
    asyncio.run(main())
