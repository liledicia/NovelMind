"""
推荐算法服务
"""
from typing import List, Dict, Optional
from ..utils.similarity import calculate_multidimensional_similarity
from .novel_service import get_novel_by_id, get_all_novels, insert_novel
from .crawler_service import JinjiangCrawler


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


def get_recommendations(
    book_id: int,
    limit: int = 10,
    weights: Optional[dict] = None
) -> List[Dict]:
    """
    基于指定小说ID推荐相似作品

    Args:
        book_id: 目标小说ID
        limit: 推荐数量（默认10本）
        weights: 自定义相似度权重配置

    Returns:
        List[dict]: 推荐小说列表，每个小说包含:
            - 所有小说字段
            - similarity_score: 相似度分数 (0-100)
            - match_reasons: 匹配原因列表

    Raises:
        ValueError: 目标小说不存在
    """
    # 1. 获取目标小说
    target_novel = get_novel_by_id(book_id)

    if not target_novel:
        raise ValueError(f"小说ID {book_id} 不存在")

    # 2. 获取所有候选小说（排除目标小说自己）
    candidate_novels = get_all_novels(exclude_id=book_id)

    # 3. 计算每本小说的相似度
    recommendations = []

    for candidate in candidate_novels:
        similarity_score, match_reasons = calculate_multidimensional_similarity(
            target_novel,
            candidate,
            weights
        )

        # 只推荐有一定相似度的小说（相似度>0）
        if similarity_score > 0:
            recommendations.append({
                **candidate,  # 包含所有小说字段
                "similarity_score": round(similarity_score, 2),
                "match_reasons": match_reasons,
                "url": f"https://www.jjwxc.net/onebook.php?novelid={candidate['book_id']}"
            })

    # 4. 按相似度降序排序
    recommendations.sort(key=lambda x: x["similarity_score"], reverse=True)

    # 5. 返回Top-K推荐
    top_recommendations = recommendations[:limit]

    # 6. 检查并爬取缺失的封面
    for i, rec in enumerate(top_recommendations):
        top_recommendations[i] = fetch_cover_if_missing(rec)

    return top_recommendations


def get_recommendation_summary(book_id: int, limit: int = 10) -> Dict:
    """
    获取推荐摘要（包含目标小说和推荐列表）

    Args:
        book_id: 目标小说ID
        limit: 推荐数量

    Returns:
        dict: {
            "target_novel": {...},  # 目标小说信息
            "recommendations": [...]  # 推荐列表
        }
    """
    target_novel = get_novel_by_id(book_id)

    if not target_novel:
        raise ValueError(f"小说ID {book_id} 不存在")

    recommendations = get_recommendations(book_id, limit)

    return {
        "target_novel": {
            "book_id": target_novel["book_id"],
            "title": target_novel["title"],
            "author": target_novel.get("author"),
            "category": target_novel.get("category"),
            "tags": target_novel.get("tags")
        },
        "recommendations": recommendations
    }


if __name__ == "__main__":
    # 测试推荐功能
    print("测试推荐算法")
    print("=" * 70)

    # 假设数据库中第一本小说的ID
    try:
        from .novel_service import get_all_novels

        novels = get_all_novels(limit=1)
        if novels:
            test_book_id = novels[0]['book_id']
            print(f"目标小说: {novels[0]['title']} (ID: {test_book_id})")
            print(f"作者: {novels[0].get('author')}")
            print(f"标签: {novels[0].get('tags')}")
            print()

            # 获取推荐
            recommendations = get_recommendations(test_book_id, limit=5)

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
