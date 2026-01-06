"""
配置文件
"""
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.parent.parent

# 数据库路径
DB_PATH = os.path.join(BASE_DIR, "jinjiang_novels.db")

# API配置
API_HOST = "0.0.0.0"
API_PORT = 8000

# CORS配置
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000"
]

# 推荐算法权重配置
RECOMMENDATION_WEIGHTS = {
    "tags": 0.5,  # 标签相似度权重
    "category": 0.15,  # 类型匹配权重
    "perspective": 0.15,  # 视角匹配权重
    "status": 0.1,  # 状态匹配权重
    "author": 0.1  # 同作者权重
}

# 爬虫配置
CRAWLER_DELAY_MIN = 2.0  # 最小延迟（秒）
CRAWLER_DELAY_MAX = 3.0  # 最大延迟（秒）
CRAWLER_TIMEOUT = 15  # 请求超时（秒）
