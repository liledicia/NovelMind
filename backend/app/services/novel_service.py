"""
小说查询和数据库操作服务
兼容 SQLite（开发）和 PostgreSQL（生产）
"""
from typing import Optional, Dict, List
from ..config import DATABASE_URL
from ..database.connection import get_db_connection

# PostgreSQL 用 %s，SQLite 用 ?
_P = "%s" if DATABASE_URL else "?"


def normalize_cover_url(cover_url: str, book_id: int) -> str:
    if not cover_url:
        return cover_url
    if 'sinaimg.cn' in cover_url or 'qpic.cn' in cover_url:
        return f'https://i9-static.jjwxc.net/novelimage.php?novelid={book_id}'
    return cover_url


def search_novel_exact(novel_name: str) -> Optional[Dict]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM book WHERE title = {_P}", (novel_name,))
        row = cursor.fetchone()
        return dict(row) if row else None


def search_novel_fuzzy(keyword: str, limit: int = 10) -> List[Dict]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * FROM book WHERE title LIKE {_P} OR author LIKE {_P} LIMIT {_P}",
            (f"%{keyword}%", f"%{keyword}%", limit),
        )
        return [dict(row) for row in cursor.fetchall()]


def get_novel_by_id(book_id: int) -> Optional[Dict]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM book WHERE book_id = {_P}", (book_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_all_novels(exclude_id: Optional[int] = None, limit: Optional[int] = None) -> List[Dict]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if exclude_id is not None:
            query = f"SELECT * FROM book WHERE book_id != {_P}"
            params: list = [exclude_id]
        else:
            query = "SELECT * FROM book"
            params = []

        if limit is not None:
            query += f" LIMIT {_P}"
            params.append(limit)

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def get_candidate_novels(target_novel: Dict) -> List[Dict]:
    """
    推荐候选集预筛选：只返回与目标小说至少共享一个信号
    （同类型 / 同视角 / 同作者 / 任一标签重叠）的小说。

    相似度算法中 score>0 的充要条件就是上述信号至少命中一个，
    因此该预筛选保证零漏召回（no false negatives），同时把候选集
    从全表 5000+ 条缩减到通常几百条，大幅降低 DB 传输与 Python 计算量。

    注：tags 用 LIKE '%tag%' 做超集匹配（可能含少量误召回），
    最终 Python 精算会修正分数，不影响结果正确性。
    """
    book_id = target_novel["book_id"]
    conditions: List[str] = []
    params: list = [book_id]

    for field in ("category", "perspective", "author"):
        val = target_novel.get(field)
        if val:
            conditions.append(f"{field} = {_P}")
            params.append(val)

    tags = (target_novel.get("tags") or "").split()
    for tag in tags:
        tag = tag.strip()
        if tag:
            conditions.append(f"tags LIKE {_P}")
            params.append(f"%{tag}%")

    # 目标小说没有任何可匹配信号 → 无候选
    if len(conditions) == 0:
        return []

    where_clause = " OR ".join(conditions)
    query = f"SELECT * FROM book WHERE book_id != {_P} AND ({where_clause})"

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def insert_novel(novel_data: dict) -> bool:
    try:
        book_id = novel_data.get('book_id')
        cover_url = normalize_cover_url(novel_data.get('cover_url'), book_id)

        values = (
            book_id,
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
            novel_data.get('first_pub_time'),
            novel_data.get('last_update_time'),
            novel_data.get('chapter_count'),
            novel_data.get('review_count'),
            novel_data.get('favorite_count'),
            novel_data.get('nutrient_count'),
            novel_data.get('total_click_count'),
            novel_data.get('score'),
            cover_url,
        )

        with get_db_connection() as conn:
            cursor = conn.cursor()
            if DATABASE_URL:
                # PostgreSQL upsert
                cursor.execute("""
                    INSERT INTO book (
                        book_id, title, author, intro, tags, main_chars, support_chars,
                        other_info, category, perspective, series, status, word_count,
                        publish_status, sign_status, first_pub_time, last_update_time,
                        chapter_count, review_count, favorite_count, nutrient_count,
                        total_click_count, score, cover_url
                    ) VALUES (
                        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
                    )
                    ON CONFLICT (book_id) DO UPDATE SET
                        title = EXCLUDED.title,
                        author = EXCLUDED.author,
                        intro = EXCLUDED.intro,
                        tags = EXCLUDED.tags,
                        main_chars = EXCLUDED.main_chars,
                        support_chars = EXCLUDED.support_chars,
                        other_info = EXCLUDED.other_info,
                        category = EXCLUDED.category,
                        perspective = EXCLUDED.perspective,
                        series = EXCLUDED.series,
                        status = EXCLUDED.status,
                        word_count = EXCLUDED.word_count,
                        publish_status = EXCLUDED.publish_status,
                        sign_status = EXCLUDED.sign_status,
                        first_pub_time = EXCLUDED.first_pub_time,
                        last_update_time = EXCLUDED.last_update_time,
                        chapter_count = EXCLUDED.chapter_count,
                        review_count = EXCLUDED.review_count,
                        favorite_count = EXCLUDED.favorite_count,
                        nutrient_count = EXCLUDED.nutrient_count,
                        total_click_count = EXCLUDED.total_click_count,
                        score = EXCLUDED.score,
                        cover_url = EXCLUDED.cover_url
                """, values)
            else:
                # SQLite upsert
                cursor.execute("""
                    INSERT OR REPLACE INTO book (
                        book_id, title, author, intro, tags, main_chars, support_chars,
                        other_info, category, perspective, series, status, word_count,
                        publish_status, sign_status, first_pub_time, last_update_time,
                        chapter_count, review_count, favorite_count, nutrient_count,
                        total_click_count, score, cover_url
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, values)
        return True

    except Exception as e:
        print(f"插入小说数据失败: {e}")
        return False
