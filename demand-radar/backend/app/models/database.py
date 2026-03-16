from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Demand(Base):
    """需求表"""
    __tablename__ = "demands"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    category = Column(String(100))  # 工具/内容/服务/信息差
    subcategory = Column(String(100))

    # 来源信息
    platform = Column(String(50))  # hn/reddit/v2ex
    source_url = Column(String(1000))
    source_id = Column(String(200))
    author = Column(String(200))

    # 信号分析
    pain_points = Column(JSON, default=list)  # 痛点词
    purchase_signals = Column(JSON, default=list)  # 付费信号
    tech_keywords = Column(JSON, default=list)  # 技术关键词
    confidence = Column(Float, default=0.0)  # 需求置信度

    # 热度指标
    score = Column(Float, default=0.0)  # 综合评分
    engagement_score = Column(Float, default=0.0)  # 互动热度
    purchase_signal_score = Column(Float, default=0.0)  # 付费信号
    feasibility_score = Column(Float, default=0.0)  # 技术可行性
    competition_score = Column(Float, default=0.0)  # 竞争度（越低越好）

    # 状态
    status = Column(String(50), default="new")  # new/analyzing/validated/archived
    cluster_id = Column(Integer, ForeignKey("demand_clusters.id"), nullable=True)

    # 时间
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime)  # 原文发布时间

    # 关系
    cluster = relationship("DemandCluster", back_populates="demands")

    __table_args__ = (
        Index("idx_platform_status", "platform", "status"),
        Index("idx_score", "score"),
        Index("idx_created_at", "created_at"),
    )


class DemandCluster(Base):
    """需求聚类（去重后的需求组）"""
    __tablename__ = "demand_clusters"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    summary = Column(Text)
    category = Column(String(100))

    # 聚合指标
    demand_count = Column(Integer, default=0)  # 包含的需求数量
    total_engagement = Column(Float, default=0.0)  # 总互动
    avg_score = Column(Float, default=0.0)  # 平均评分

    # 时间
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    demands = relationship("Demand", back_populates="cluster")


class Platform(Base):
    """平台配置"""
    __tablename__ = "platforms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100))
    api_endpoint = Column(String(500))
    is_active = Column(String(20), default="true")  # 使用字符串兼容SQLite
    last_fetch = Column(DateTime)
    fetch_interval = Column(Integer, default=3600)  # 秒

    # 过滤配置
    keywords = Column(JSON, default=list)  # 目标关键词
    min_score = Column(Integer, default=5)  # 最低热度


class TaskLog(Base):
    """采集任务日志"""
    __tablename__ = "task_logs"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50))
    task_type = Column(String(50))  # fetch/analyze/cluster
    status = Column(String(50))  # success/failed/pending
    items_processed = Column(Integer, default=0)
    items_new = Column(Integer, default=0)
    error_message = Column(Text)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime)
