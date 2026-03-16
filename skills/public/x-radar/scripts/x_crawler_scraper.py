#!/usr/bin/env python3
"""
X (Twitter) Data Crawler using twscrape
使用免费的 Web API 爬取 Twitter/X 数据
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import asyncio
import twscrape

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), "../data/x_radar.db")

# 关键词分类
KEYWORDS = {
    "need": ["need", "looking for", "want", "need help", "anyone knows", "any recommendations", "建议", "求", "需要"],
    "product": ["launch", "release", "new app", "product", "tool", "app", "software", "发布", "推出", "新产品"],
    "complain": ["hate", "sucks", "broken", "bug", "frustrated", "worst", "垃圾", "坑", "烂", "差评"]
}


class XCrawlerScraper:
    def __init__(self):
        """初始化爬虫"""
        self.client = None
        self.init_db()

        # 尝试加载已有的账号，或使用默认
        accounts_file = os.path.join(os.path.dirname(__file__), "../data/accounts.json")
        self.accounts = self.load_accounts(accounts_file)

        # 初始化 twscrape 客户端
        if self.accounts:
            self.client = twscrape.API()
            asyncio.run(self._init_accounts())

    def load_accounts(self, accounts_file: str) -> List[Dict]:
        """加载账号配置"""
        if os.path.exists(accounts_file):
            with open(accounts_file, 'r') as f:
                return json.load(f)
        return []

    async def _init_accounts(self):
        """初始化账号"""
        for acc in self.accounts:
            try:
                await self.client.add_account(acc['username'], acc['password'],
                                            acc.get('email'), acc.get('email_password'))
            except Exception as e:
                print(f"Failed to add account {acc['username']}: {e}")

    def init_db(self):
        """初始化数据库"""
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 帖子表
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

        # 评论文表
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

    async def search_tweets(
        self,
        query: str,
        category: str,
        max_results: int = 100,
        hours_back: int = 24
    ) -> List[Dict]:
        """搜索推文"""
        if not self.client:
            print("Twitter client not initialized. Add accounts first.")
            return []

        tweets = []
        try:
            # 添加时间过滤
            time_query = f"lang:en OR lang:zh -is:retweet {query}"

            count = 0
            async for tweet in self.client.search(time_query, limit=max_results):
                tweets.append({
                    'id': str(tweet.id),
                    'author_id': str(tweet.user.id),
                    'author_username': tweet.user.username,
                    'text': tweet.rawContent,
                    'created_at': tweet.date.isoformat() if tweet.date else None,
                    'metrics_impressions': 0,  # Web API 不提供浏览量
                    'metrics_likes': tweet.likeCount or 0,
                    'metrics_retweets': tweet.retweetCount or 0,
                    'metrics_replies': tweet.replyCount or 0,
                    'category': category
                })
                count += 1
                if count >= max_results:
                    break

        except Exception as e:
            print(f"Error searching tweets: {e}")

        return tweets

    async def get_trending_tweets(self, hours_back: int = 24, max_results: int = 100) -> List[Dict]:
        """获取热门推文（按点赞和回复数排序）"""
        # 搜索热门话题
        tweets = []
        # 搜索过滤
        queries = ["", "AI", "tech", "startup"]

        for query in queries:
            tweets.extend(await self.search_tweets(query, "trending", max_results // len(queries), hours_back))

        # 按点赞数 + 回复数排序
        tweets.sort(key=lambda x: x['metrics_likes'] + x['metrics_replies'], reverse=True)
        return tweets[:max_results]

    async def get_category_tweets(self, category: str, hours_back: int = 24, max_results: int = 50) -> List[Dict]:
        """获取分类推文"""
        keywords = KEYWORDS.get(category, [])
        tweets = []

        for keyword in keywords:
            tweets.extend(await self.search_tweets(keyword, category, max_results // len(keywords), hours_back))

        return tweets

    async def get_comments(self, post_id: str, max_results: int = 50) -> List[Dict]:
        """获取推文评论"""
        if not self.client:
            return []

        comments = []
        try:
            count = 0
            async for tweet in self.client.search(f"to:{post_id}", limit=max_results):
                comments.append({
                    'id': str(tweet.id),
                    'post_id': post_id,
                    'author_id': str(tweet.user.id),
                    'author_username': tweet.user.username,
                    'text': tweet.rawContent,
                    'created_at': tweet.date.isoformat() if tweet.date else None
                })
                count += 1
                if count >= max_results:
                    break

        except Exception as e:
            print(f"Error getting comments for post {post_id}: {e}")

        return comments

    def save_posts(self, posts: List[Dict]):
        """保存推文到数据库"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        for post in posts:
            cursor.execute('''
                INSERT OR REPLACE INTO posts
                (id, author_id, author_username, text, created_at, metrics_impressions,
                 metrics_likes, metrics_retweets, metrics_replies, category)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                post['id'],
                post['author_id'],
                post['author_username'],
                post['text'],
                post['created_at'],
                post['metrics_impressions'],
                post['metrics_likes'],
                post['metrics_retweets'],
                post['metrics_replies'],
                post['category']
            ))

        conn.commit()
        conn.close()
        print(f"Saved {len(posts)} posts to database")

    def save_comments(self, comments: List[Dict]):
        """保存评论到数据库"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        for comment in comments:
            cursor.execute('''
                INSERT OR REPLACE INTO comments
                (id, post_id, author_id, author_username, text, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                comment['id'],
                comment['post_id'],
                comment['author_id'],
                comment['author_username'],
                comment['text'],
                comment['created_at']
            ))

        conn.commit()
        conn.close()
        print(f"Saved {len(comments)} comments to database")

    async def crawl_all(self, hours_back: int = 24):
        """爬取所有数据"""
        print("Starting X radar crawl with scraper...")

        # 爬取热门推文
        print("Fetching trending posts...")
        trending = await self.get_trending_tweets(hours_back)
        self.save_posts(trending)

        # 为每个热门推文获取评论（前20个）
        for post in trending[:20]:
            print(f"Fetching comments for post {post['id']}...")
            comments = await self.get_comments(post['id'])
            self.save_comments(comments)

        # 爬取需求推文
        print("Fetching need posts...")
        need_posts = await self.get_category_tweets("need", hours_back)
        self.save_posts(need_posts)

        # 爬取产品推文
        print("Fetching product posts...")
        product_posts = await self.get_category_tweets("product", hours_back)
        self.save_posts(product_posts)

        # 爬取抱怨推文
        print("Fetching complain posts...")
        complain_posts = await self.get_category_tweets("complain", hours_back)
        self.save_posts(complain_posts)

        print("Crawl completed!")


async def main():
    """主函数"""
    crawler = XCrawlerScraper()

    if not crawler.accounts:
        print("=" * 60)
        print("No Twitter accounts found!")
        print("=" * 60)
        print("\nTo use this crawler, you need to add Twitter accounts.")
        print("Create accounts.json in the data directory with this format:")
        print("""
[
    {
        "username": "your_twitter_username",
        "password": "your_password",
        "email": "email@example.com",
        "email_password": "email_password"
    }
]
        """)
        print("\nTips:")
        print("- Use aged accounts (older accounts work better)")
        print("- Add multiple accounts to distribute load")
        print("- Keep accounts private and secure")
        print("=" * 60)
        return

    await crawler.crawl_all(hours_back=24)


if __name__ == "__main__":
    asyncio.run(main())
