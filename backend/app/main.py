"""
FastAPI 主程序入口
NovelMind 晋江小说推荐系统后端
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .api.routes import novels
from .database.connection import init_db_indexes
from .config import CORS_ORIGINS

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 60)
    logger.info("NovelMind API 启动成功!")
    logger.info("API 文档: http://localhost:8000/docs")
    init_db_indexes()
    logger.info("=" * 60)
    yield
    logger.info("NovelMind API 已关闭")


# 创建FastAPI应用实例
app = FastAPI(
    title="NovelMind API",
    description="晋江小说推荐系统 - 基于智能算法的小说推荐服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# 配置CORS中间件（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(novels.router)


@app.get("/")
async def root():
    return {
        "service": "NovelMind API",
        "version": "1.0.0",
        "description": "晋江小说推荐系统",
        "docs": "/docs",
        "endpoints": {
            "search": "/api/novels/search?q={novel_name}",
            "recommendations": "/api/recommendations/{book_id}",
            "health": "/api/health"
        }
    }


if __name__ == "__main__":
    import uvicorn

    # 运行开发服务器
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式：代码修改自动重载
        log_level="info"
    )
