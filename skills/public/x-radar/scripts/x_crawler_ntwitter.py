#!/usr/bin/env python3
"""
X (Twitter) Data Crawler using Nitter (Deprecated)
通过 Nitter 实例抓取 Twitter/X 数据（无需账号）

注意：Nitter 实例大多已不可用，建议使用 twscrape 或 mock data
"""

import os
import sqlite3
import requests
from datetime import datetime
from typing import List, Dict
from bs4 import BeautifulSoup

DB_PATH = os.path.join(os.path.dirname(__file__), "../data/x_radar.db")


class XCrawlerNitter:
    """Nitter 爬虫（已弃用）"""

    def __init__(self):
        """初始化爬虫"""
        print("=" * 60)
        print("⚠️  NITTER CRAWLER IS DEPRECATED")
        print("=" * 60)
        print("Most Nitter instances are no longer functional.")
        print("Please use one of these alternatives:")
        print("  1. twscrape (free with Twitter accounts)")
        print("  2. Official Twitter API (paid)")
        print("  3. Mock data for demonstration")
        print("=" * 60)
        print("\nRun 'python3 generate_mock_data.py' for demo data.")
        print("Or add accounts to data/accounts.json and run twscrape crawler.\n")

    def crawl_all(self, hours_back: int = 24):
        """爬取所有数据"""
        print("Nitter crawler is deprecated. No data will be fetched.")


def main():
    """主函数"""
    crawler = XCrawlerNitter()


if __name__ == "__main__":
    main()
