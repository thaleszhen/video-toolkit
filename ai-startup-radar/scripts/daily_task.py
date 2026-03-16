#!/usr/bin/env python3
"""
AI 创业雷达 - 定时任务脚本
每天自动运行数据采集和分析
"""
import subprocess
import logging
import os
from datetime import datetime
import sys
sys.path.append('..')
from config import CONFIG, DATA_DIR, REPORTS_DIR

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_scraper(scraper_name: str, script_path: str) -> bool:
    """
    运行采集脚本

    Args:
        scraper_name: 采集器名称
        script_path: 脚本路径

    Returns:
        是否成功
    """
    logger.info(f"🚀 运行 {scraper_name}...")

    try:
        result = subprocess.run(
            ["python3", script_path],
            capture_output=True,
            text=True,
            timeout=300  # 5 分钟超时
        )

        if result.returncode == 0:
            logger.info(f"✅ {scraper_name} 完成")
            return True
        else:
            logger.error(f"❌ {scraper_name} 失败")
            logger.error(result.stderr)
            return False

    except subprocess.TimeoutExpired:
        logger.error(f"⏰ {scraper_name} 超时")
        return False
    except Exception as e:
        logger.error(f"❌ {scraper_name} 异常: {e}")
        return False


def run_all_scrapers() -> Dict[str, bool]:
    """
    运行所有采集脚本

    Returns:
        运行结果字典
    """
    results = {}

    scripts_dir = os.path.join(os.path.dirname(__file__), "scripts")

    # 检查数据源是否启用
    if CONFIG["sources"]["reddit"]["enabled"]:
        results["reddit"] = run_scraper(
            "Reddit 采集器",
            os.path.join(scripts_dir, "reddit_scraper.py")
        )
    else:
        logger.info("⏭️  跳过 Reddit（未启用）")

    if CONFIG["sources"]["app_store"]["enabled"]:
        results["app_store"] = run_scraper(
            "App Store 采集器",
            os.path.join(scripts_dir, "app_store_scraper.py")
        )
    else:
        logger.info("⏭️  跳过 App Store（未启用）")

    # 其他采集器可以在这里添加

    return results


def run_analyzer() -> bool:
    """
    运行分析脚本

    Returns:
        是否成功
    """
    logger.info(f"🔍 运行需求分析...")

    try:
        result = subprocess.run(
            ["python3", "scripts/analyze.py"],
            capture_output=True,
            text=True,
            timeout=180  # 3 分钟超时
        )

        if result.returncode == 0:
            logger.info(f"✅ 分析完成")
            logger.info(result.stdout)
            return True
        else:
            logger.error(f"❌ 分析失败")
            logger.error(result.stderr)
            return False

    except subprocess.TimeoutExpired:
        logger.error(f"⏰ 分析超时")
        return False
    except Exception as e:
        logger.error(f"❌ 分析异常: {e}")
        return False


def generate_summary(results: Dict[str, bool]) -> str:
    """
    生成运行摘要

    Args:
        results: 运行结果

    Returns:
        摘要文本
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    summary = f"""
{'='*60}
    🤖 AI 创业雷达 - 运行摘要
    {'='*60}
    时间: {timestamp}

    📊 采集结果:
"""

    for scraper, success in results.items():
        status = "✅ 成功" if success else "❌ 失败"
        summary += f"   {scraper}: {status}\n"

    summary += f"\n🔍 分析: ✅ 完成\n"
    summary += f"\n📄 报告位置: {REPORTS_DIR}/report_*.md\n"
    summary += f"📦 数据位置: {DATA_DIR}/*.json\n"
    summary += f"{'='*60}\n"

    return summary


def send_notification(summary: str):
    """
    发送通知（可扩展）

    Args:
        summary: 摘要文本
    """
    # TODO: 可以添加以下通知方式：
    # - Email
    # - Slack/Telegram/Discord webhook
    # - Pushover/Pushbullet

    logger.info("📬 通知功能可扩展")
    logger.info(summary)


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("🚀 AI 创业雷达 - 每日任务启动")
    logger.info("=" * 60)

    # 1. 运行采集器
    logger.info("\n📥 步骤 1: 数据采集")
    scraper_results = run_all_scrapers()

    # 2. 运行分析
    logger.info("\n📊 步骤 2: 需求分析")
    analysis_success = run_analyzer()

    # 3. 生成摘要
    logger.info("\n📋 步骤 3: 生成摘要")
    if analysis_success:
        summary = generate_summary(scraper_results)
        logger.info(summary)

        # 4. 发送通知
        logger.info("\n📬 步骤 4: 发送通知")
        send_notification(summary)

    logger.info("\n" + "=" * 60)
    logger.info("✅ AI 创业雷达 - 每日任务完成")
    logger.info("=" * 60)

    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\n⚠️  用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ 未预期的错误: {e}")
        sys.exit(1)
