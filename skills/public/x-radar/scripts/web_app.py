#!/usr/bin/env python3
"""
X Radar Web Application
可视化展示爬取的 X 数据
"""

import os
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify
import plotly.graph_objs as go
import plotly.utils

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), "../data/x_radar.db")

app = Flask(__name__, template_folder='../assets/templates')


def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def format_number(num):
    """格式化数字"""
    if num >= 1000000:
        return f"{num / 1000000:.1f}M"
    elif num >= 1000:
        return f"{num / 1000:.1f}K"
    return str(num)


@app.route('/')
def index():
    """首页"""
    conn = get_db_connection()

    # 统计数据
    stats = {
        'total_posts': conn.execute('SELECT COUNT(*) FROM posts').fetchone()[0],
        'total_comments': conn.execute('SELECT COUNT(*) FROM comments').fetchone()[0],
        'trending': conn.execute('SELECT COUNT(*) FROM posts WHERE category = "trending"').fetchone()[0],
        'need': conn.execute('SELECT COUNT(*) FROM posts WHERE category = "need"').fetchone()[0],
        'product': conn.execute('SELECT COUNT(*) FROM posts WHERE category = "product"').fetchone()[0],
        'complain': conn.execute('SELECT COUNT(*) FROM posts WHERE category = "complain"').fetchone()[0],
    }

    # 最近爬取时间
    last_crawl = conn.execute('SELECT MAX(crawled_at) FROM posts').fetchone()[0]
    if last_crawl:
        last_crawl = datetime.fromisoformat(last_crawl).strftime("%Y-%m-%d %H:%M:%S")

    conn.close()

    return render_template('index.html', stats=stats, last_crawl=last_crawl)


@app.route('/api/stats')
def api_stats():
    """获取统计数据 API"""
    conn = get_db_connection()

    stats = {
        'total_posts': conn.execute('SELECT COUNT(*) FROM posts').fetchone()[0],
        'total_comments': conn.execute('SELECT COUNT(*) FROM comments').fetchone()[0],
        'by_category': {}
    }

    for category in ['trending', 'need', 'product', 'complain']:
        stats['by_category'][category] = conn.execute(
            'SELECT COUNT(*) FROM posts WHERE category = ?', (category,)
        ).fetchone()[0]

    conn.close()
    return jsonify(stats)


@app.route('/posts/<category>')
def posts(category):
    """帖子列表页面"""
    conn = get_db_connection()

    posts = conn.execute('''
        SELECT * FROM posts
        WHERE category = ?
        ORDER BY metrics_impressions + metrics_replies DESC
        LIMIT 100
    ''', (category,)).fetchall()

    conn.close()

    # 转换为字典并格式化
    posts_list = []
    for post in posts:
        post_dict = dict(post)
        post_dict['created_at'] = datetime.fromisoformat(post['created_at']).strftime("%Y-%m-%d %H:%M")
        posts_list.append(post_dict)

    category_names = {
        'trending': '热门趋势',
        'need': '需求帖子',
        'product': '产品帖子',
        'complain': '抱怨帖子'
    }

    return render_template('posts.html',
                          posts=posts_list,
                          category=category,
                          category_name=category_names.get(category, category))


@app.route('/api/posts/<category>')
def api_posts(category):
    """获取帖子列表 API"""
    conn = get_db_connection()

    posts = conn.execute('''
        SELECT * FROM posts
        WHERE category = ?
        ORDER BY metrics_impressions + metrics_replies DESC
        LIMIT 100
    ''', (category,)).fetchall()

    conn.close()

    # 转换为字典
    posts_list = []
    for post in posts:
        post_dict = dict(post)
        posts_list.append(post_dict)

    return jsonify(posts_list)


@app.route('/post/<post_id>')
def post_detail(post_id):
    """帖子详情页面"""
    conn = get_db_connection()

    # 获取帖子
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()

    if not post:
        conn.close()
        return "Post not found", 404

    # 获取评论
    comments = conn.execute('''
        SELECT * FROM comments
        WHERE post_id = ?
        ORDER BY created_at DESC
    ''', (post_id,)).fetchall()

    conn.close()

    post_dict = dict(post)
    post_dict['created_at'] = datetime.fromisoformat(post['created_at']).strftime("%Y-%m-%d %H:%M")

    comments_list = []
    for comment in comments:
        comment_dict = dict(comment)
        comment_dict['created_at'] = datetime.fromisoformat(comment['created_at']).strftime("%Y-%m-%d %H:%M")
        comments_list.append(comment_dict)

    return render_template('post_detail.html', post=post_dict, comments=comments_list)


@app.route('/api/post/<post_id>/comments')
def api_post_comments(post_id):
    """获取帖子评论 API"""
    conn = get_db_connection()

    comments = conn.execute('''
        SELECT * FROM comments
        WHERE post_id = ?
        ORDER BY created_at DESC
    ''', (post_id,)).fetchall()

    conn.close()

    comments_list = []
    for comment in comments:
        comment_dict = dict(comment)
        comments_list.append(comment_dict)

    return jsonify(comments_list)


@app.route('/charts')
def charts():
    """图表页面"""
    conn = get_db_connection()

    # 各类帖子数量
    category_counts = {}
    for category in ['trending', 'need', 'product', 'complain']:
        category_counts[category] = conn.execute(
            'SELECT COUNT(*) FROM posts WHERE category = ?', (category,)
        ).fetchone()[0]

    # 热门帖子的浏览量分布
    top_posts = conn.execute('''
        SELECT text, metrics_impressions, metrics_likes, metrics_replies
        FROM posts
        WHERE category = 'trending'
        ORDER BY metrics_impressions DESC
        LIMIT 20
    ''').fetchall()

    conn.close()

    # 创建饼图
    pie_chart = go.Figure(data=[go.Pie(
        labels=list(category_counts.keys()),
        values=list(category_counts.values()),
        hole=0.3
    )])
    pie_chart.update_layout(title="帖子分类分布")

    # 创建柱状图
    bar_chart = go.Figure(data=[go.Bar(
        x=[p['text'][:30] + '...' for p in top_posts],
        y=[p['metrics_impressions'] for p in top_posts],
        name='浏览量'
    )])
    bar_chart.update_layout(
        title="热门帖子浏览量 Top 20",
        xaxis_tickangle=-45
    )

    return render_template('charts.html',
                          pie_chart=pie_chart.to_html(full_html=False),
                          bar_chart=bar_chart.to_html(full_html=False))


if __name__ == '__main__':
    # 确保数据目录存在
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # 启动服务
    app.run(host='0.0.0.0', port=8080, debug=True)
