"""
AI 创业雷达 - 每日需求挖掘 Agent
从多个平台挖掘真实需求和可做产品
"""
import json
import os
from datetime import datetime
from typing import List, Dict

# 配置
CONFIG = {
    # 数据源配置
    "sources": {
        "reddit": {
            "enabled": True,
            "subreddits": ["startups", "SaaS", "entrepreneur", "smallbusiness", "ProductHunt"],
            "min_score": 10,
            "max_age_hours": 24
        },
        "app_store": {
            "enabled": False,  # 需要 API key
            "apps": ["productivity", "business", "finance"],
            "min_rating": 3.5
        },
        "amazon": {
            "enabled": False,  # 需要爬虫
            "categories": ["software", "electronics"],
            "min_stars": 3
        },
        "twitter": {
            "enabled": False,  # 需要 API key
            "keywords": ["need", "looking for", "wish there was", "frustrated with"],
            "min_likes": 10
        }
    },

    # 输出配置
    "output": {
        "demands_count": 5,  # 每天输出的需求数量
        "products_count": 3,  # 每天输出的产品想法数量
        "report_dir": "reports",
        "data_dir": "data"
    },

    # AI 分析配置
    "ai_analysis": {
        "enabled": True,
        "min_confidence": 0.7,  # 最低置信度
        "check_duplicates": True,  # 检查重复需求
        "identify_opportunities": True  # 识别机会
    }
}

# 数据存储路径
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")
TODAY = datetime.now().strftime("%Y-%m-%d")

def ensure_dirs():
    """确保目录存在"""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)

def load_demands(date: str = None) -> List[Dict]:
    """加载历史需求"""
    if date is None:
        date = TODAY
    file_path = os.path.join(DATA_DIR, f"demands_{date}.json")
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_demands(demands: List[Dict], date: str = None):
    """保存需求"""
    if date is None:
        date = TODAY
    file_path = os.path.join(DATA_DIR, f"demands_{date}.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(demands, f, ensure_ascii=False, indent=2)

def load_products(date: str = None) -> List[Dict]:
    """加载历史产品想法"""
    if date is None:
        date = TODAY
    file_path = os.path.join(DATA_DIR, f"products_{date}.json")
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_products(products: List[Dict], date: str = None):
    """保存产品想法"""
    if date is None:
        date = TODAY
    file_path = os.path.join(DATA_DIR, f"products_{date}.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

def get_all_dates() -> List[str]:
    """获取所有数据日期"""
    dates = []
    for file in os.listdir(DATA_DIR):
        if file.startswith("demands_") and file.endswith(".json"):
            date = file.replace("demands_", "").replace(".json", "")
            dates.append(date)
    return sorted(dates, reverse=True)
