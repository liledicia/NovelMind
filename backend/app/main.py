"""
FastAPI 主程序入口
NovelMind 晋江小说推荐系统后端
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .api.routes import novels

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用实例
app = FastAPI(
    title="NovelMind API",
    description="晋江小说推荐系统 - 基于智能算法的小说推荐服务",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI 文档地址
    redoc_url="/redoc"  # ReDoc 文档地址
)

# 配置CORS中间件（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite 默认端口
        "http://localhost:3000",  # 备用前端端口
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)

# 注册路由
app.include_router(novels.router)

# 根路径
@app.get("/")
async def root():
    """API根路径"""
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


# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    logger.info("=" * 60)
    logger.info("NovelMind API 启动成功!")
    logger.info("API 文档: http://localhost:8000/docs")
    logger.info("=" * 60)


# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    logger.info("NovelMind API 已关闭")


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
