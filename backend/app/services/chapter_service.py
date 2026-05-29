"""
章节试读数据服务（前 N 章免费正文）
兼容 SQLite（开发）和 PostgreSQL（生产）
"""
from typing import Dict, List
from ..config import DATABASE_URL
from ..database.connection import get_db_connection

# PostgreSQL 用 %s，SQLite 用 ?
_P = "%s" if DATABASE_URL else "?"


def get_chapters(book_id: int) -> List[Dict]:
    """取某本小说已存的试读章节，按章节顺序返回。"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * FROM chapter WHERE book_id = {_P} ORDER BY chapter_order",
            (book_id,),
        )
        return [dict(row) for row in cursor.fetchall()]


def has_chapters(book_id: int) -> bool:
    """该书是否已存过试读章节（懒加载判定用）。"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT 1 FROM chapter WHERE book_id = {_P} LIMIT 1", (book_id,)
        )
        return cursor.fetchone() is not None


def get_or_fetch_chapters(book_id: int, n: int = 3) -> List[Dict]:
    """
    懒加载试读章节：库里有就直接返回；没有则实时爬前 n 章免费正文、
    写库后返回。爬取失败返回空列表。
    """
    existing = get_chapters(book_id)
    if existing:
        return existing

    # 延迟导入，避免模块加载期的循环依赖
    from .crawler_service import JinjiangCrawler
    try:
        chapters = JinjiangCrawler().fetch_free_chapters(book_id, n)
    except Exception as e:
        print(f"✗ 爬取试读章节失败 (book_id={book_id}): {e}")
        return []

    if chapters:
        insert_chapters(book_id, chapters)
    return chapters


def insert_chapters(book_id: int, chapters: List[Dict]) -> bool:
    """批量写入/更新试读章节（按 book_id+chapter_id upsert）。"""
    if not chapters:
        return False
    rows = [
        (
            book_id,
            ch.get("chapter_id"),
            ch.get("chapter_order"),
            ch.get("chapter_name"),
            ch.get("chapter_intro"),
            ch.get("content"),
            ch.get("author_say"),
        )
        for ch in chapters
    ]
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if DATABASE_URL:
                cursor.executemany("""
                    INSERT INTO chapter (
                        book_id, chapter_id, chapter_order,
                        chapter_name, chapter_intro, content, author_say
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (book_id, chapter_id) DO UPDATE SET
                        chapter_order = EXCLUDED.chapter_order,
                        chapter_name  = EXCLUDED.chapter_name,
                        chapter_intro = EXCLUDED.chapter_intro,
                        content       = EXCLUDED.content,
                        author_say    = EXCLUDED.author_say
                """, rows)
            else:
                cursor.executemany("""
                    INSERT OR REPLACE INTO chapter (
                        book_id, chapter_id, chapter_order,
                        chapter_name, chapter_intro, content, author_say
                    ) VALUES (?,?,?,?,?,?,?)
                """, rows)
        return True
    except Exception as e:
        print(f"插入章节数据失败 (book_id={book_id}): {e}")
        return False
