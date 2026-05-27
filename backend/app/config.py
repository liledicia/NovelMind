"""
配置文件 — 所有敏感值从环境变量读取
"""
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.parent.parent

# ── 数据库 ──────────────────────────────────────────────────────
# 生产环境设置 DATABASE_URL（PostgreSQL），本地开发回退到 SQLite
DATABASE_URL = os.environ.get("DATABASE_URL")

# 本地 SQLite 回退路径（仅开发用）
SQLITE_PATH = os.path.join(BASE_DIR, "jinjiang_novels.db")

# ── API ──────────────────────────────────────────────────────────
API_HOST = "0.0.0.0"
API_PORT = int(os.environ.get("PORT", 8000))

# ── CORS ─────────────────────────────────────────────────────────
# 生产环境通过 FRONTEND_URL 环境变量指定前端域名
_frontend_url = os.environ.get("FRONTEND_URL", "")
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]
if _frontend_url:
    CORS_ORIGINS.append(_frontend_url)

# ── 推荐算法权重 ─────────────────────────────────────────────────
RECOMMENDATION_WEIGHTS = {
    "tags": 0.55,
    "category": 0.18,
    "perspective": 0.17,
    "author": 0.10,
}

# ── 爬虫 ─────────────────────────────────────────────────────────
CRAWLER_DELAY_MIN = 2.0
CRAWLER_DELAY_MAX = 3.0
CRAWLER_TIMEOUT = 15
