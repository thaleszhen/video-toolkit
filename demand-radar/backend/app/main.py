from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Demand Radar API starting up...")
    yield
    # Shutdown
    logger.info("👋 Demand Radar API shutting down...")


app = FastAPI(
    title="Demand Radar API",
    description="从社交媒体挖掘用户需求",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "name": "Demand Radar API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/api/demands")
async def get_demands(limit: int = 50, offset: int = 0):
    """获取需求列表"""
    # TODO: 从数据库查询
    return {
        "demands": [],
        "total": 0,
        "limit": limit,
        "offset": offset
    }


@app.post("/api/demands/analyze")
async def analyze_demand(text: str):
    """分析文本是否包含需求信号"""
    # TODO: 调用NLP模型
    return {
        "is_demand": False,
        "category": None,
        "confidence": 0.0,
        "signals": []
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
