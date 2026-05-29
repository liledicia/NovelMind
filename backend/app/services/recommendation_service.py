"""
推荐算法服务
"""
import time
import threading
from typing import List, Dict, Optional, Tuple
from ..utils.similarity import calculate_multidimensional_similarity
from ..utils.tag_idf import get_tag_idf, get_default_idf, clear_tag_idf_cache
from .novel_service import get_novel_by_id, get_candidate_novels, insert_novel
from .crawler_service import JinjiangCrawler


# ── 推荐结果 TTL 缓存 ────────────────────────────────────────────
# 小说静态数据变化很慢，缓存 5 分钟可大幅减少重复查询 + 重算
_CACHE_TTL = 300       # 秒
_CACHE_MAX_SIZE = 1000  # 最大缓存条目数，防止无限增长
_rec_cache: Dict[Tuple[int, int], Tuple[float, Dict]] = {}
_cache_lock = threading.Lock()


def _cache_get(key: Tuple[int, int]) -> Optional[Dict]:
    with _cache_lock:
        entry = _rec_cache.get(key)
        if entry is None:
            return None
        expire_ts, value = entry
        if expire_ts < time.time():
            _rec_cache.pop(key, None)
            return None
        return value


def _cache_set(key: Tuple[int, int], value: Dict) -> None:
    with _cache_lock:
        # 超过容量上限：先清掉已过期条目，仍超限则按过期时间淘汰最旧的
        if len(_rec_cache) >= _CACHE_MAX_SIZE:
            now = time.time()
            expired = [k for k, (ts, _) in _rec_cache.items() if ts < now]
            for k in expired:
                _rec_cache.pop(k, None)
            if len(_rec_cache) >= _CACHE_MAX_SIZE:
                oldest = min(_rec_cache, key=lambda k: _rec_cache[k][0])
                _rec_cache.pop(oldest, None)
        _rec_cache[key] = (time.time() + _CACHE_TTL, value)


def invalidate_recommendation_cache() -> None:
    """数据更新后可调用，清空推荐缓存 + 标签 IDF 缓存（新书会改变标签频率）。"""
    with _cache_lock:
        _rec_cache.clear()
    clear_tag_idf_cache()


def fetch_cover_if_missing(novel: Dict) -> Dict:
    """
    检查小说封面，如果缺失则实时爬取

    Args:
        novel: 小说数据字典

    Returns:
        Dict: 更新后的小说数据（如果爬取了封面）
    """
    # 如果已经有封面，直接返回
    if novel.get('cover_url'):
        return novel

    # 如果没有 book_id，无法爬取
    if not novel.get('book_id'):
        return novel

    try:
        # 实时爬取封面
        crawler = JinjiangCrawler()
        novel_url = f"https://www.jjwxc.net/onebook.php?novelid={novel['book_id']}"

        # 只爬取封面信息
        detail = crawler.fetch_novel_detail(novel_url)

        if detail.get('cover_url'):
            # 更新小说数据
            novel['cover_url'] = detail['cover_url']

            # 同时更新数据库
            updated_novel = {**novel, 'cover_url': detail['cover_url']}
            insert_novel(updated_novel)

            print(f"✓ 已为《{novel.get('title')}》爬取封面")
    except Exception as e:
        print(f"✗ 爬取《{novel.get('title')}》封面失败: {e}")

    return novel


def fetch_stats_if_missing(novel: Dict) -> Dict:
    """
    检查小说统计数据，缺失则通过移动端 API 实时补全并写回数据库。

    判定标准：nutrient_count 为 None（营养液数桌面端静态页抓不到，
    历史入库的书几乎都缺），触发一次移动端 API 补全。

    Args:
        novel: 小说数据字典

    Returns:
        Dict: 更新后的小说数据（如果补全了统计）
    """
    # 已有营养液数据，视为统计完整，直接返回
    if novel.get('nutrient_count') is not None:
        return novel

    # 没有 book_id 无法补全
    if not novel.get('book_id'):
        return novel

    try:
        crawler = JinjiangCrawler()
        stats = crawler.fetch_stats_via_mobile_api(novel['book_id'])

        if stats:
            novel.update(stats)
            # 写回数据库，下次直接命中
            insert_novel(novel)
            print(f"✓ 已为《{novel.get('title')}》补全统计数据")
    except Exception as e:
        print(f"✗ 补全《{novel.get('title')}》统计失败: {e}")

    return novel


def backfill_missing_stats(recommendations: List[Dict]) -> None:
    """后台补全推荐列表中缺失的统计数据，通过 BackgroundTasks 调用，不阻塞响应。"""
    for rec in recommendations:
        fetch_stats_if_missing(rec)


def get_recommendations(
    target_novel: Dict,
    limit: int = 10,
    weights: Optional[dict] = None
) -> List[Dict]:
    """
    基于目标小说推荐相似作品。

    Args:
        target_novel: 已查询好的目标小说字典（调用方负责查询，避免重复 DB 往返）
        limit: 推荐数量（默认10本）
        weights: 自定义相似度权重配置

    Returns:
        List[dict]: 推荐小说列表，每项含 similarity_score 和 match_reasons
    """
    # 候选集预筛选：只取与目标至少共享一个信号的小说，
    # 而非全表 5000+ 条，DB 传输与 Python 计算量都大幅下降
    candidate_novels = get_candidate_novels(target_novel)

    # 标签 IDF 权重表只加载一次，供本次所有候选共用
    tag_idf = get_tag_idf()
    default_idf = get_default_idf()

    recommendations = []
    for candidate in candidate_novels:
        similarity_score, match_reasons, match_summary = calculate_multidimensional_similarity(
            target_novel,
            candidate,
            weights,
            tag_idf=tag_idf,
            default_idf=default_idf,
        )
        if similarity_score > 0:
            recommendations.append({
                **candidate,
                "similarity_score": round(similarity_score, 2),
                "match_reasons": match_reasons,
                "match_summary": match_summary,
                "url": f"https://www.jjwxc.net/onebook.php?novelid={candidate['book_id']}"
            })

    recommendations.sort(key=lambda x: x["similarity_score"], reverse=True)
    return recommendations[:limit]


def get_recommendation_summary(book_id: int, limit: int = 10) -> Dict:
    """
    获取推荐摘要（包含目标小说和推荐列表）。

    封面补全（fetch_cover_if_missing）已从此函数移出，
    改由调用方通过 BackgroundTasks 异步执行，不阻塞响应。

    结果带 5 分钟 TTL 缓存，相同 (book_id, limit) 的请求直接命中缓存。
    """
    cache_key = (book_id, limit)
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    target_novel = get_novel_by_id(book_id)
    if not target_novel:
        raise ValueError(f"小说ID {book_id} 不存在")

    # 复用已查询的 target_novel，无需在 get_recommendations 内再查一次
    recommendations = get_recommendations(target_novel, limit)

    result = {
        "target_novel": {
            "book_id": target_novel["book_id"],
            "title": target_novel["title"],
            "author": target_novel.get("author"),
            "category": target_novel.get("category"),
            "tags": target_novel.get("tags")
        },
        "recommendations": recommendations
    }

    _cache_set(cache_key, result)
    return result


def backfill_missing_covers(recommendations: List[Dict]) -> None:
    """后台补全推荐列表中缺失的封面，通过 BackgroundTasks 调用，不阻塞响应。"""
    for rec in recommendations:
        fetch_cover_if_missing(rec)


if __name__ == "__main__":
    # 测试推荐功能
    print("测试推荐算法")
    print("=" * 70)

    # 假设数据库中第一本小说的ID
    try:
        from .novel_service import get_all_novels

        novels = get_all_novels(limit=1)
        if novels:
            target = novels[0]
            test_book_id = target['book_id']
            print(f"目标小说: {target['title']} (ID: {test_book_id})")
            print(f"作者: {target.get('author')}")
            print(f"标签: {target.get('tags')}")
            print()

            # 获取推荐（get_recommendations 现在接收小说字典）
            recommendations = get_recommendations(target, limit=5)

            print(f"为你推荐 {len(recommendations)} 本相似小说:")
            print()

            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec['title']} by {rec.get('author')}")
                print(f"   相似度: {rec['similarity_score']}%")
                print(f"   匹配原因: {', '.join(rec['match_reasons'])}")
                print(f"   标签: {rec.get('tags', 'N/A')}")
                print()
        else:
            print("数据库中没有小说数据")

    except Exception as e:
        print(f"测试失败: {e}")
