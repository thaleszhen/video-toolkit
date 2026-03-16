#!/usr/bin/env python3
"""
生成模拟 Twitter 数据用于演示
"""

import os
import sqlite3
import random
from datetime import datetime, timedelta

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), "../data/x_radar.db")

# 模拟数据源
MOCK_TWEETS = {
    "trending": [
        {"user": "techguru", "text": "AI is revolutionizing how we build products! The new GPT models are game changers. #AI #Tech"},
        {"user": "startup_founder", "text": "Just closed our Series A! $10M to transform healthcare with AI. Excited for the journey ahead! 🚀"},
        {"user": "dev_tools", "text": "New release: Faster builds, better debugging, and zero downtime deployments. Check it out!"},
        {"user": "data_scientist", "text": "Machine learning models are now 40% faster thanks to our new optimization techniques"},
        {"user": "crypto_analyst", "text": "Bitcoin hits new all-time high! The market is showing incredible strength. #Bitcoin #Crypto"},
        {"user": "product_manager", "text": "Launched our new analytics dashboard - users love the real-time insights feature!"},
        {"user": "cloud_architect", "text": "Serverless architecture reduced our costs by 70% and improved scalability dramatically"},
        {"user": "security_expert", "text": "Zero-trust security is no longer optional - it's essential for modern organizations"},
        {"user": "mobile_dev", "text": "Our new app hit 1M downloads in the first week! Users love the intuitive design"},
        {"user": "ai_researcher", "text": "Breakthrough in natural language understanding - models can now reason about complex problems"}
    ],
    "need": [
        {"user": "indie_hacker", "text": "Need a reliable payment gateway for international customers. Any recommendations?"},
        {"user": "startup_ceo", "text": "Looking for a CTO with experience in fintech. Must know Python and AWS"},
        {"user": "product_owner", "text": "Need help with user research for our new app. Tools or services you recommend?"},
        {"user": "freelancer", "text": "Anyone know a good tool for managing multiple client projects and invoicing?"},
        {"user": "dev_lead", "text": "Need recommendations for CI/CD pipeline tools for a mixed stack (React, Node, Python)"},
        {"user": "marketer", "text": "Looking for analytics tools that work well with social media campaigns"},
        {"user": "content_creator", "text": "Need suggestions for video editing software that's not too expensive"},
        {"user": "entrepreneur", "text": "Any good resources for learning about MVP development?"},
        {"user": "designer", "text": "Looking for design system tools that integrate with Figma"},
        {"user": "data_analyst", "text": "Need help choosing between Power BI and Tableau for startup analytics"}
    ],
    "product": [
        {"user": "product_launch", "text": "Introducing AI-Powered Code Assistant - write better code faster with intelligent suggestions"},
        {"user": "saaS_company", "text": "New feature released: Automated testing with our smart test generation engine"},
        {"user": "tech_startup", "text": "Launching our developer-first API platform - 99.99% uptime guaranteed"},
        {"user": "mobile_app", "text": "Our new productivity app is now live on iOS and Android! 📱✨"},
        {"user": "cloud_service", "text": "New database service: Fully managed, auto-scaling, with built-in AI optimization"},
        {"user": "ai_platform", "text": "Launch: No-code AI model builder for business users. Build AI solutions without coding"},
        {"user": "dev_tools_co", "text": "Released our new debugging tool - finds bugs before they reach production"},
        {"user": "security_firm", "text": "New product: AI-powered threat detection that stops attacks in real-time"},
        {"user": "analytics_co", "text": "Our analytics dashboard now includes predictive insights and AI recommendations"},
        {"user": "collaboration_app", "text": "New feature: Real-time collaborative editing for teams"}
    ],
    "complain": [
        {"user": "frustrated_user", "text": "This app keeps crashing every 10 minutes. So annoying! 😤"},
        {"user": "customer_123", "text": "Customer support is terrible. Waited 3 hours and still no response"},
        {"user": "developer_pain", "text": "The API documentation is so outdated. Spent hours figuring it out"},
        {"user": "user_buggy", "text": "Found another critical bug in the latest update. When will it be fixed?"},
        {"user": "disappointed", "text": "Paid for premium features but they don't work as advertised. Feeling scammed"},
        {"user": "tech_issues", "text": "System is down again. This is the third time this week"},
        {"user": "ui_complaint", "text": "The new UI is terrible - everything is harder to find now"},
        {"user": "slow_service", "text": "Page load times are getting worse with each update. Frustrating!"},
        {"user": "feature_missing", "text": "Can't believe they removed the best feature from the last version"},
        {"user": "billing_issue", "text": "Been charged double this month and can't get anyone to fix it"}
    ]
}

MOCK_COMMENTS = [
    {"user": "supportive_user", "text": "Great insight! Thanks for sharing."},
    {"user": "expert_comment", "text": "I've been working on something similar. Happy to discuss!"},
    {"user": "question_mark", "text": "This is interesting. What stack are you using?"},
    {"user": "helpful_reply", "text": "I had this issue too. Here's what worked for me..."},
    {"user": "enthusiastic", "text": "Love this! Going to try it out right now!"},
    {"user": "constructive", "text": "Have you considered adding feature X? Would make it even better"},
    {"user": "agree", "text": "Totally agree with this. Spot on!"},
    {"user": "sharing", "text": "Sharing this with my team - very useful"},
    {"user": "curious", "text": "How's the performance compared to alternatives?"},
    {"user": "suggestion", "text": "Maybe add a tutorial section for new users?"}
]


def init_db():
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


def generate_mock_data():
    """生成模拟数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 清空旧数据
    cursor.execute("DELETE FROM posts")
    cursor.execute("DELETE FROM comments")

    # 生成帖子数据
    tweet_id = 1000000

    for category, tweets in MOCK_TWEETS.items():
        for tweet_data in tweets:
            # 生成随机时间（最近24小时）
            hours_ago = random.randint(0, 24)
            created_at = datetime.now() - timedelta(hours=hours_ago)

            # 生成随机指标
            likes = random.randint(10, 10000)
            retweets = random.randint(5, 2000)
            replies = random.randint(2, 500)
            impressions = likes * random.randint(3, 10)

            cursor.execute('''
                INSERT INTO posts
                (id, author_id, author_username, text, created_at,
                 metrics_impressions, metrics_likes, metrics_retweets,
                 metrics_replies, category)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(tweet_id),
                str(tweet_id + 10000000),
                tweet_data['user'],
                tweet_data['text'],
                created_at.isoformat(),
                impressions,
                likes,
                retweets,
                replies,
                category
            ))

            # 为部分帖子生成评论
            if random.random() > 0.3:  # 70% 的帖子有评论
                num_comments = random.randint(1, 5)
                for i in range(num_comments):
                    comment_data = random.choice(MOCK_COMMENTS)
                    comment_hours = random.randint(0, hours_ago)
                    comment_time = datetime.now() - timedelta(hours=comment_hours)

                    cursor.execute('''
                        INSERT INTO comments
                        (id, post_id, author_id, author_username, text, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        str(tweet_id * 1000 + i),  # 唯一评论 ID
                        str(tweet_id),
                        str(tweet_id * 100 + i),
                        comment_data['user'],
                        comment_data['text'],
                        comment_time.isoformat()
                    ))

            tweet_id += 1

    conn.commit()
    conn.close()

    # 统计
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    total_posts = cursor.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
    total_comments = cursor.execute("SELECT COUNT(*) FROM comments").fetchone()[0]

    print("=" * 50)
    print("✅ 模拟数据生成成功！")
    print("=" * 50)
    print(f"📊 总帖子数: {total_posts}")
    print(f"💬 总评论数: {total_comments}")
    print("=" * 50)

    # 按分类统计
    for category in ['trending', 'need', 'product', 'complain']:
        count = cursor.execute(
            "SELECT COUNT(*) FROM posts WHERE category = ?",
            (category,)
        ).fetchone()[0]
        print(f"  {category}: {count} 帖子")

    print("=" * 50)
    print("🌐 访问 Web 界面查看数据:")
    print("   http://localhost:8080")
    print("=" * 50)


def main():
    """主函数"""
    init_db()
    generate_mock_data()


if __name__ == "__main__":
    main()
