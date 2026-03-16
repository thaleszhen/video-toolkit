"""
需求分析和产品想法生成
分析收集到的需求，生成可做的产品建议
"""
import json
import logging
from datetime import datetime
from typing import List, Dict, Tuple
import sys
sys.path.append('..')
from config import CONFIG, load_demands, save_products, load_products, ensure_dirs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def deduplicate_demands(demands: List[Dict]) -> List[Dict]:
    """
    去除重复需求

    Args:
        demands: 原始需求列表

    Returns:
        去重后的需求
    """
    seen = set()
    unique_demands = []

    for demand in demands:
        # 创建唯一标识
        key = f"{demand['source']}_{demand['source_id']}"

        if key not in seen:
            seen.add(key)
            unique_demands.append(demand)
        else:
            logger.info(f"🔄 跳过重复需求: {demand['title'][:50]}...")

    logger.info(f"📊 去重后: {len(demands)} -> {len(unique_demands)}")
    return unique_demands


def score_demands(demands: List[Dict]) -> List[Dict]:
    """
    对需求进行评分

    Args:
        demands: 需求列表

    Returns:
        评分后的需求
    """
    for demand in demands:
        # 基础分数 = 置信度
        base_score = demand.get("confidence", 0)

        # 加权因素
        weights = {
            "opportunity_score": 0.3,  # 机会分数
            "has_purchase_signal": 0.2,  # 付费信号
            "has_multiple_pains": 0.15,  # 多个痛点
            "high_engagement": 0.15,  # 高互动
            "tech_keywords": 0.1,  # 技术关键词
            "recent": 0.1  # 时效性
        }

        # 计算加权分数
        weighted_score = base_score

        # 机会分数
        if demand.get("opportunity_score", 0) > 50:
            weighted_score += weights["opportunity_score"]

        # 付费信号
        if len(demand.get("purchase_signals", [])) > 0:
            weighted_score += weights["has_purchase_signal"]

        # 多个痛点
        if len(demand.get("pain_points", [])) >= 2:
            weighted_score += weights["has_multiple_pains"]

        # 高互动（分数 + 评论）
        if demand.get("score", 0) > 100 or demand.get("num_comments", 0) > 50:
            weighted_score += weights["high_engagement"]

        # 技术关键词
        if len(demand.get("tech_keywords", [])) > 0:
            weighted_score += weights["tech_keywords"]

        demand["final_score"] = min(weighted_score, 1.0)

    return sorted(demands, key=lambda x: x["final_score"], reverse=True)


def extract_top_demands(demands: List[Dict], count: int = 5) -> List[Dict]:
    """
    提取 top 需求

    Args:
        demands: 需求列表
        count: 提取数量

    Returns:
        Top 需求
    """
    return demands[:count]


def identify_product_opportunities(demands: List[Dict]) -> List[Dict]:
    """
    识别产品机会

    Args:
        demands: 需求列表

    Returns:
        产品机会列表
    """
    # 按技术关键词分组
    tech_groups = {}
    for demand in demands:
        for tech in demand.get("tech_keywords", []):
            if tech not in tech_groups:
                tech_groups[tech] = []
            tech_groups[tech].append(demand)

    # 按痛点分组
    pain_groups = {}
    for demand in demands:
        for pain in demand.get("pain_points", []):
            if pain not in pain_groups:
                pain_groups[pain] = []
            pain_groups[pain].append(demand)

    opportunities = []

    # 从技术栈生成产品想法
    for tech, related_demands in tech_groups.items():
        if len(related_demands) >= 2:
            avg_score = sum(d["final_score"] for d in related_demands) / len(related_demands)

            # 生成产品名称
            product_names = {
                "api": f"{tech.capitalize()} API Service",
                "tool": f"{tech.capitalize()} Toolkit",
                "platform": f"{tech.capitalize()} Platform",
                "saas": f"{tech.capitalize()} SaaS"
            }

            for product_type, product_name in product_names.items():
                opportunity = {
                    "id": f"{tech}_{product_type}",
                    "name": product_name,
                    "type": product_type,
                    "tech_stack": tech,
                    "related_demands": [d["id"] for d in related_demands[:3]],
                    "demand_count": len(related_demands),
                    "avg_score": round(avg_score, 3),
                    "pain_points": list(set().union(*[d.get("pain_points", []) for d in related_demands]))[:5],
                    "target_users": "Developers, Startups, Small Businesses",
                    "revenue_potential": "Subscription, API Usage",
                    "difficulty": "Medium"
                }
                opportunities.append(opportunity)

    # 从痛点生成产品想法
    for pain, related_demands in pain_groups.items():
        if len(related_demands) >= 3:
            avg_score = sum(d["final_score"] for d in related_demands) / len(related_demands)

            # 解决方案名称
            solution_names = {
                "tool": f"解决 {pain} 的工具",
                "automation": f"{pain} 自动化方案",
                "saas": f"{pain} 解决 SaaS",
                "api": f"{pain} 解决 API"
            }

            for product_type, product_name in solution_names.items():
                opportunity = {
                    "id": f"{pain}_{product_type}",
                    "name": product_name,
                    "type": product_type,
                    "pain_point": pain,
                    "related_demands": [d["id"] for d in related_demands[:3]],
                    "demand_count": len(related_demands),
                    "avg_score": round(avg_score, 3),
                    "pain_points": [pain],
                    "target_users": "Professionals, Small Businesses, Entrepreneurs",
                    "revenue_potential": "One-time purchase, Subscription",
                    "difficulty": "Low to Medium"
                }
                opportunities.append(opportunity)

    # 按平均分数排序
    opportunities.sort(key=lambda x: x["avg_score"], reverse=True)

    logger.info(f"💡 识别出 {len(opportunities)} 个产品机会")
    return opportunities


def select_top_opportunities(opportunities: List[Dict], count: int = 3) -> List[Dict]:
    """
    选择 top 产品机会

    Args:
        opportunities: 机会列表
        count: 选择数量

    Returns:
        Top 机会
    """
    return opportunities[:count]


def generate_product_details(opportunity: Dict) -> Dict:
    """
    生成产品详细信息

    Args:
        opportunity: 产品机会

    Returns:
        产品详情
    """
    difficulty_map = {
        "Low": "简单",
        "Medium": "中等",
        "High": "困难"
    }

    type_map = {
        "tool": "工具",
        "automation": "自动化方案",
        "saas": "SaaS",
        "api": "API 服务",
        "platform": "平台"
    }

    return {
        **opportunity,
        "difficulty_cn": difficulty_map.get(opportunity.get("difficulty", "Medium"), "中等"),
        "type_cn": type_map.get(opportunity.get("type", "tool"), "工具"),
        "estimated_development_time": {
            "Low": "1-2 周",
            "Medium": "2-4 周",
            "High": "1-3 个月"
        }.get(opportunity.get("difficulty", "Medium"), "2-4 周"),
        "mvp_features": [
            "核心功能实现",
            "用户认证",
            "基础 UI/UX",
            "数据存储"
        ],
        "monetization_strategy": {
            "Subscription": "订阅制 - 月费/年费",
            "API Usage": "按调用次数计费",
            "One-time purchase": "一次性购买",
            "Freemium": "免费 + 高级功能付费"
        }.get(opportunity.get("revenue_potential", "Subscription"), "订阅制"),
        "tech_stack": {
            "frontend": "React/Vue + TailwindCSS",
            "backend": "Python/FastAPI 或 Node.js/Express",
            "database": "PostgreSQL/MongoDB",
            "hosting": "Vercel/Railway/Render"
        }
    }


def analyze_demands() -> Tuple[List[Dict], List[Dict]]:
    """
    分析需求并生成产品机会

    Returns:
        (top_demands, top_products)
    """
    # 加载需求
    demands = load_demands()

    if not demands:
        logger.warning("⚠️  没有需求数据，请先运行采集脚本")
        return [], []

    logger.info(f"📊 加载 {len(demands)} 个需求")

    # 去重
    demands = deduplicate_demands(demands)

    # 评分
    demands = score_demands(demands)

    # 提取 top 5 需求
    top_demands = extract_top_demands(demands, count=CONFIG["output"]["demands_count"])

    # 识别产品机会
    opportunities = identify_product_opportunities(demands)

    # 选择 top 3 产品
    top_products_raw = select_top_opportunities(opportunities, count=CONFIG["output"]["products_count"])

    # 生成产品详情
    top_products = [generate_product_details(p) for p in top_products_raw]

    return top_demands, top_products


def generate_report(top_demands: List[Dict], top_products: List[Dict]) -> str:
    """
    生成日报

    Args:
        top_demands: Top 需求
        top_products: Top 产品

    Returns:
        Markdown 格式报告
    """
    report_date = datetime.now().strftime("%Y-%m-%d")
    report_time = datetime.now().strftime("%H:%M")

    report = f"""# 🔍 AI 创业雷达日报

**日期**: {report_date}  
**时间**: {report_time}

---

## 📊 今日数据统计

- **需求数量**: {len(top_demands)}
- **产品想法**: {len(top_products)}
- **数据源**: Reddit, App Store, Amazon, Twitter

---

## 🎯 Top 5 用户需求

"""

    for i, demand in enumerate(top_demands, 1):
        pain_tags = " | ".join([f"#{p}" for p in demand.get("pain_points", [])[:3]])
        purchase_tags = " | ".join([f"💰{ps}" for ps in demand.get("purchase_signals", [])[:2]])

        report += f"""
### {i}. {demand.get('title', 'No Title')}

**来源**: {demand['source']} | **置信度**: {demand.get('confidence', 0):.2%} | **评分**: {demand.get('final_score', 0):.2%}

**描述**: {demand.get('description', 'No description')[:200]}...

**痛点**: {pain_tags}

**付费信号**: {purchase_tags if purchase_tags else '无'}

**链接**: {demand.get('url', 'N/A')}

---

"""

    report += f"""
## 💡 Top 3 产品机会

"""

    for i, product in enumerate(top_products, 1):
        report += f"""
### {i}. {product.get('name', 'No Name')}

**类型**: {product.get('type_cn', '未知')} | **难度**: {product.get('difficulty_cn', '中等')}

**目标用户**: {product.get('target_users', 'N/A')}

**相关需求**: {product.get('demand_count', 0)} 个 | **平均评分**: {product.get('avg_score', 0):.3f}

**痛点**: {" | ".join(product.get('pain_points', [])[:3])}

**变现方式**: {product.get('monetization_strategy', 'N/A')}

**预计开发时间**: {product.get('estimated_development_time', '2-4 周')}

**技术栈**:
- 前端: {product['tech_stack']['frontend']}
- 后端: {product['tech_stack']['backend']}
- 数据库: {product['tech_stack']['database']}
- 部署: {product['tech_stack']['hosting']}

**MVP 功能**:
{chr(10).join(f"- {feature}" for feature in product.get('mvp_features', []))}

---

"""

    report += f"""
## 📋 行动建议

### 优先级 1（本周）
- [ ] 调研 Top 2 需求的竞品
- [ ] 制作 Top 1 产品的 MVP
- [ ] 验证市场需求（问卷调查）

### 优先级 2（本月）
- [ ] 分析 Top 3 产品的技术可行性
- [ ] 准备产品原型
- [ ] 寻找早期用户

### 优先级 3（长期）
- [ ] 构建需求追踪系统
- [ ] 建立用户反馈渠道
- [ ] 持续数据收集

---

**报告生成**: AI 创业雷达 v0.1.0
**自动运行**: 每日 {datetime.now().strftime("%H:%M")}
"""

    return report


def save_report(report: str, date: str = None):
    """
    保存报告

    Args:
        report: Markdown 格式报告
        date: 日期
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    from config import REPORTS_DIR
    ensure_dirs()

    report_path = f"{REPORTS_DIR}/report_{date}.md"

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    logger.info(f"✅ 报告已保存: {report_path}")
    return report_path


def main():
    """主函数"""
    logger.info("🚀 开始分析需求...")

    # 分析需求
    top_demands, top_products = analyze_demands()

    if not top_demands:
        logger.error("❌  没有足够的数据生成报告")
        return

    # 生成报告
    report = generate_report(top_demands, top_products)

    # 保存报告
    report_path = save_report(report)

    # 保存产品想法
    from config import save_products
    save_products(top_products)

    logger.info(f"✅ 完成！")
    logger.info(f"📄 报告: {report_path}")
    logger.info(f"💡 产品想法: {len(top_products)} 个")

    # 打印摘要
    print(f"\n{'='*60}")
    print("AI 创业雷达 - 每日分析")
    print(f"{'='*60}")
    print(f"\n📊 今日发现:")
    print(f"   - {len(top_demands)} 个真实需求")
    print(f"   - {len(top_products)} 个可做产品")
    print(f"\n🎯 Top 需求:")
    for d in top_demands[:3]:
        print(f"   • {d['title'][:60]}...")
        print(f"     置信度: {d['confidence']:.0%} | 评分: {d['final_score']:.2f}")
    print(f"\n💡 Top 产品:")
    for p in top_products[:2]:
        print(f"   • {p['name']}")
        print(f"     难度: {p['difficulty_cn']} | 机会: {p['avg_score']:.3f}")
    print(f"\n📄 查看完整报告: {report_path}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
