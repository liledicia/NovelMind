"""
标签 IDF（逆文档频率）计算与缓存。

作用：让推荐打分时按标签的「稀有度」加权——
- 「正剧 / 轻松 / 甜文」这类几乎人人都有的高频标签 → IDF 低 → 权重小
- 「破镜重圆 / 复仇虐渣」这类稀有强信号标签 → IDF 高 → 权重大

从全库标签一次性统计文档频率（DF），结果缓存在内存；
新书入库后调用 clear_tag_idf_cache() 失效重算（已接入 invalidate_recommendation_cache）。
"""
import math
import threading
from typing import Dict, Optional

from ..database.connection import get_db_connection

_idf_cache: Optional[Dict[str, float]] = None
_default_idf: float = 1.0          # 未登录标签（如实时爬取的新书带了库里没有的标签）的兜底权重
_lock = threading.Lock()


def _compute_tag_idf() -> Dict[str, float]:
    """扫描全库 tags 字段，计算每个标签的平滑 IDF。"""
    global _default_idf
    doc_freq: Dict[str, int] = {}
    total_docs = 0

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tags FROM book")
        for row in cursor.fetchall():
            tags = (dict(row).get("tags") or "").split()
            if not tags:
                continue
            total_docs += 1
            for tag in set(tags):
                doc_freq[tag] = doc_freq.get(tag, 0) + 1

    if total_docs == 0:
        return {}

    # 平滑 IDF：log((N+1)/(df+1)) + 1，保证恒为正、且 df 越大值越小
    idf = {
        tag: math.log((total_docs + 1) / (df + 1)) + 1.0
        for tag, df in doc_freq.items()
    }
    # 兜底权重设为中位数附近：用一个只出现过一次的稀有标签的 IDF 作为新标签默认值的上界，
    # 这里取「出现在约 5% 文档」的标签对应 IDF，避免未知标签被过度放大或压没
    _default_idf = math.log((total_docs + 1) / (0.05 * total_docs + 1)) + 1.0
    return idf


def get_tag_idf() -> Dict[str, float]:
    """返回 {标签: IDF}，首次调用时从库里计算并缓存。"""
    global _idf_cache
    if _idf_cache is None:
        with _lock:
            if _idf_cache is None:
                _idf_cache = _compute_tag_idf()
    return _idf_cache


def get_default_idf() -> float:
    """未登录标签的兜底 IDF（需先调用过 get_tag_idf 完成统计）。"""
    return _default_idf


def clear_tag_idf_cache() -> None:
    """数据更新后调用，下次 get_tag_idf 会重新统计。"""
    global _idf_cache
    with _lock:
        _idf_cache = None
