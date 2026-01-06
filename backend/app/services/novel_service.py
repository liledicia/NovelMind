"""
小说查询和数据库操作服务
"""
from typing import Optional, Dict, List
from datetime import date
from ..database.connection import get_db_connection


def search_novel_exact(novel_name: str) -> Optional[Dict]:
    """
    在数据库中精确搜索小说（按书名）

    Args:
        novel_name: 小说名称

    Returns:
        dict: 小说完整信息字典（包含book和stats数据），未找到返回None
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 联表查询，获取最新的统计数据
        query = """
            SELECT
                b.*,
                s.review_count, s.favorite_count, s.nutrient_count,
                s.total_click_count, s.score
            FROM book b
            LEFT JOIN (
                SELECT book_id,
                       review_count, favorite_count, nutrient_count,
                       total_click_count, score
                FROM stats
                WHERE id IN (
                    SELECT MAX(id) FROM stats GROUP BY book_id
                )
            ) s ON b.book_id = s.book_id
            WHERE b.title = ?
        """

        cursor.execute(query, (novel_name,))
        row = cursor.fetchone()

        if row:
            return dict(row)
        return None


def search_novel_fuzzy(keyword: str, limit: int = 10) -> List[Dict]:
    """
    模糊搜索小说（支持标题/作者匹配）

    Args:
        keyword: 搜索关键词
        limit: 返回结果数量限制

    Returns:
        List[dict]: 小说列表
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        query = """
            SELECT
                b.*,
                s.review_count, s.favorite_count, s.nutrient_count,
                s.total_click_count, s.score
            FROM book b
            LEFT JOIN (
                SELECT book_id,
                       review_count, favorite_count, nutrient_count,
                       total_click_count, score
                FROM stats
                WHERE id IN (
                    SELECT MAX(id) FROM stats GROUP BY book_id
                )
            ) s ON b.book_id = s.book_id
            WHERE b.title LIKE ? OR b.author LIKE ?
            LIMIT ?
        """

        cursor.execute(query, (f"%{keyword}%", f"%{keyword}%", limit))
        rows = cursor.fetchall()

        return [dict(row) for row in rows]


def get_novel_by_id(book_id: int) -> Optional[Dict]:
    """
    根据book_id获取小说信息

    Args:
        book_id: 小说ID

    Returns:
        dict: 小说完整信息，未找到返回None
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        query = """
            SELECT
                b.*,
                s.review_count, s.favorite_count, s.nutrient_count,
                s.total_click_count, s.score
            FROM book b
            LEFT JOIN (
                SELECT book_id,
                       review_count, favorite_count, nutrient_count,
                       total_click_count, score
                FROM stats
                WHERE id IN (
                    SELECT MAX(id) FROM stats GROUP BY book_id
                )
            ) s ON b.book_id = s.book_id
            WHERE b.book_id = ?
        """

        cursor.execute(query, (book_id,))
        row = cursor.fetchone()

        if row:
            return dict(row)
        return None


def get_all_novels(exclude_id: Optional[int] = None, limit: Optional[int] = None) -> List[Dict]:
    """
    获取所有小说列表（用于推荐计算）

    Args:
        exclude_id: 排除的小说ID（通常是目标小说自己）
        limit: 返回数量限制

    Returns:
        List[dict]: 小说列表
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        if exclude_id:
            query = """
                SELECT
                    b.*,
                    s.review_count, s.favorite_count, s.nutrient_count,
                    s.total_click_count, s.score
                FROM book b
                LEFT JOIN (
                    SELECT book_id,
                           review_count, favorite_count, nutrient_count,
                           total_click_count, score
                    FROM stats
                    WHERE id IN (
                        SELECT MAX(id) FROM stats GROUP BY book_id
                    )
                ) s ON b.book_id = s.book_id
                WHERE b.book_id != ?
            """
            params = [exclude_id]
        else:
            query = """
                SELECT
                    b.*,
                    s.review_count, s.favorite_count, s.nutrient_count,
                    s.total_click_count, s.score
                FROM book b
                LEFT JOIN (
                    SELECT book_id,
                           review_count, favorite_count, nutrient_count,
                           total_click_count, score
                    FROM stats
                    WHERE id IN (
                        SELECT MAX(id) FROM stats GROUP BY book_id
                    )
                ) s ON b.book_id = s.book_id
            """
            params = []

        if limit:
            query += " LIMIT ?"
            params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [dict(row) for row in rows]


def insert_novel(novel_data: dict) -> bool:
    """
    将爬取的小说数据插入数据库

    Args:
        novel_data: 小说数据字典（必须包含book_id字段）

    Returns:
        bool: 插入是否成功
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # 插入book表
            cursor.execute('''
                INSERT OR REPLACE INTO book
                (book_id, title, author, intro, tags, main_chars, support_chars,
                 other_info, category, perspective, series, status, word_count,
                 publish_status, sign_status, last_update_time, chapter_count)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ''', (
                novel_data.get('book_id'),
                novel_data.get('title'),
                novel_data.get('author'),
                novel_data.get('intro'),
                novel_data.get('tags'),
                novel_data.get('main_chars'),
                novel_data.get('support_chars'),
                novel_data.get('other_info'),
                novel_data.get('category'),
                novel_data.get('perspective'),
                novel_data.get('series'),
                novel_data.get('status'),
                novel_data.get('word_count'),
                novel_data.get('publish_status'),
                novel_data.get('sign_status'),
                novel_data.get('last_update_time'),
                novel_data.get('chapter_count')
            ))

            # 插入stats表
            cursor.execute('''
                INSERT INTO stats
                (book_id, date, review_count, favorite_count, nutrient_count,
                 total_click_count, score, chapter_count)
                VALUES (?,?,?,?,?,?,?,?)
            ''', (
                novel_data.get('book_id'),
                date.today().isoformat(),
                novel_data.get('review_count'),
                novel_data.get('favorite_count'),
                novel_data.get('nutrient_count'),
                novel_data.get('total_click_count'),
                novel_data.get('score'),
                novel_data.get('chapter_count')
            ))

            conn.commit()
            return True

    except Exception as e:
        print(f"插入小说数据失败: {e}")
        return False


if __name__ == "__main__":
    # 测试查询功能
    print("测试1: 精确搜索")
    result = search_novel_exact("全职高手")
    if result:
        print(f"找到小说: {result['title']}, 作者: {result['author']}")
    else:
        print("未找到小说")
    print()

    print("测试2: 模糊搜索")
    results = search_novel_fuzzy("高手", limit=5)
    print(f"找到 {len(results)} 本相关小说:")
    for novel in results:
        print(f"  - {novel['title']} by {novel['author']}")
