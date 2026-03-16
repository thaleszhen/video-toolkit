#!/usr/bin/env python3
"""
X (Twitter) Data Crawler
爬取当日热门帖子、需求帖子、产品帖子、抱怨帖子及评论区
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import tweepy

# Twitter API 配置（从环境变量读取）
BEARER_TOKEN = os.getenv("X_BEARER_TOKEN", "")
API_KEY = os.getenv("X_API_KEY", "")
API_SECRET = os.getenv("X_API_SECRET", "")
ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN", "")
ACCESS_SECRET = os.getenv("X_ACCESS_SECRET", "")

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), "../data/x_radar.db")

# 关键词分类
KEYWORDS = {
    "need": ["need", "looking for", "want", "need help", "anyone knows", "any recommendations", "建议", "求", "需要"],
    "product": ["launch", "release", "new app", "product", "tool", "app", "software", "发布", "推出", "新产品"],
    "complain": ["hate", "sucks", "broken", "bug", "frustrated", "worst", "垃圾", "坑", "烂", "差评"]
}


class XCrawler:
    def __init__(self):
        """初始化爬虫"""
        self.client = None
        if BEARER_TOKEN:
            self.client = tweepy.Client(bearer_token=BEARER_TOKEN)
        else:
            print("Warning: No X_BEARER_TOKEN found. Set up credentials in environment.")
        self.init_db()

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
                metrics_impressions INTEGER,
                metrics_likes INTEGER,
                metrics_retweets INTEGER,
                metrics_replies INTEGER,
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

    def search_posts(
        self,
        query: str,
        category: str,
        max_results: int = 100,
        hours_back: int = 24
    ) -> List[Dict]:
        """搜索帖子"""
        if not self.client:
            print("Twitter client not initialized")
            return []

        # 构建时间查询
        since_date = datetime.now() - timedelta(hours=hours_back)
        since_str = since_date.strftime("%Y-%m-%dT%H:%M:%SZ")

        tweets = []
        try:
            # 使用 Twitter API v2 搜索
            response = self.client.search_recent_tweets(
                query=query,
                max_results=min(max_results, 100),
                tweet_fields=['author_id', 'created_at', 'public_metrics', 'text'],
                expansions=['author_id'],
                start_time=since_str
            )

            if response.data:
                # 获取作者信息
                authors = {user.id: user for user in response.includes['users']} if 'users' in response.includes else {}

                for tweet in response.data:
                    author = authors.get(tweet.author_id)
                    tweets.append({
                        'id': tweet.id,
                        'author_id': tweet.author_id,
                        'author_username': author.username if author else 'unknown',
                        'text': tweet.text,
                        'created_at': tweet.created_at.isoformat() if tweet.created_at else None,
                        'metrics_impressions': tweet.public_metrics.get('impression_count', 0) if tweet.public_metrics else 0,
                        'metrics_likes': tweet.public_metrics.get('like_count', 0) if tweet.public_metrics else 0,
                        'metrics_retweets': tweet.public_metrics.get('retweet_count', 0) if tweet.public_metrics else 0,
                        'metrics_replies': tweet.public_metrics.get('reply_count', 0) if tweet.public_metrics else 0,
                        'category': category
                    })

        except Exception as e:
            print(f"Error searching posts: {e}")

        return tweets

    def get_trending_posts(self, hours_back: int = 24, max_results: int = 100) -> List[Dict]:
        """获取热门帖子（按浏览和评论数排序）"""
        # 搜索英文和中文的热门内容
        tweets = []
        for query in ["-is:retweet lang:en", "-is:retweet lang:zh"]:
            tweets.extend(self.search_posts(query, "trending", max_results, hours_back))

        # 按浏览量 + 评论量排序
        tweets.sort(key=lambda x: x['metrics_impressions'] + x['metrics_replies'], reverse=True)
        return tweets[:max_results]

    def get_category_posts(self, category: str, hours_back: int = 24, max_results: int = 50) -> List[Dict]:
        """获取分类帖子"""
        keywords = KEYWORDS.get(category, [])
        tweets = []

        for keyword in keywords:
            # 构建查询
            query = f"({keyword}) -is:retweet"
            tweets.extend(self.search_posts(query, category, max_results // len(keywords), hours_back))

        return tweets

    def get_comments(self, post_id: str, max_results: int = 50) -> List[Dict]:
        """获取帖子评论"""
        if not self.client:
            return []

        comments = []
        try:
            response = self.client.get_replies(
                id=post_id,
                max_results=max_results,
                tweet_fields=['author_id', 'created_at', 'text'],
                expansions=['author_id']
            )

            if response.data:
                authors = {user.id: user for user in response.includes['users']} if 'users' in response.includes else {}

                for tweet in response.data:
                    author = authors.get(tweet.author_id)
                    comments.append({
                        'id': tweet.id,
                        'post_id': post_id,
                        'author_id': tweet.author_id,
                        'author_username': author.username if author else 'unknown',
                        'text': tweet.text,
                        'created_at': tweet.created_at.isoformat() if tweet.created_at else None
                    })

        except Exception as e:
            print(f"Error getting comments for post {post_id}: {e}")

        return comments

    def save_posts(self, posts: List[Dict]):
        """保存帖子到数据库"""
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

    def crawl_all(self, hours_back: int = 24):
        """爬取所有数据"""
        print("Starting X radar crawl...")

        # 爬取热门帖子
        print("Fetching trending posts...")
        trending = self.get_trending_posts(hours_back)
        self.save_posts(trending)

        # 为每个热门帖子获取评论（前20个）
        for post in trending[:20]:
            print(f"Fetching comments for post {post['id']}...")
            comments = self.get_comments(post['id'])
            self.save_comments(comments)

        # 爬取需求帖子
        print("Fetching need posts...")
        need_posts = self.get_category_posts("need", hours_back)
        self.save_posts(need_posts)

        # 爬取产品帖子
        print("Fetching product posts...")
        product_posts = self.get_category_posts("product", hours_back)
        self.save_posts(product_posts)

        # 爬取抱怨帖子
        print("Fetching complain posts...")
        complain_posts = self.get_category_posts("complain", hours_back)
        self.save_posts(complain_posts)

        print("Crawl completed!")


def main():
    """主函数"""
    crawler = XCrawler()
    crawler.crawl_all(hours_back=24)


if __name__ == "__main__":
    main()
