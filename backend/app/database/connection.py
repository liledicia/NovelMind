"""
数据库连接管理
- 生产环境（DATABASE_URL 已设置）：PostgreSQL via psycopg2 连接池
- 本地开发（无 DATABASE_URL）：SQLite 回退
"""
import os
from contextlib import contextmanager
from typing import Generator

from ..config import DATABASE_URL, SQLITE_PATH

# ── PostgreSQL 连接池（仅生产环境）─────────────────────────────
_pg_pool = None

def _get_pg_pool():
    global _pg_pool
    if _pg_pool is None:
        import psycopg2.pool
        _pg_pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=DATABASE_URL,
        )
    return _pg_pool


# ── 统一上下文管理器 ───────────────────────────────────────────
@contextmanager
def get_db_connection() -> Generator:
    if DATABASE_URL:
        yield from _pg_connection()
    else:
        yield from _sqlite_connection()


@contextmanager
def _pg_connection():
    import psycopg2.extras
    pool = _get_pg_pool()
    conn = pool.getconn()
    try:
        yield _PgConnWrapper(conn)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.putconn(conn)


@contextmanager
def _sqlite_connection():
    import sqlite3
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


class _PgConnWrapper:
    """薄包装层：让 PostgreSQL 连接的游标行为像 sqlite3.Row（返回 dict）。"""

    def __init__(self, conn):
        self._conn = conn

    def cursor(self):
        import psycopg2.extras
        return self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()


# ── 数据库初始化 ───────────────────────────────────────────────
_CREATE_TABLE_PG = """
CREATE TABLE IF NOT EXISTS book (
    book_id             BIGINT PRIMARY KEY,
    title               TEXT,
    author              TEXT,
    intro               TEXT,
    tags                TEXT,
    main_chars          TEXT,
    support_chars       TEXT,
    other_info          TEXT,
    category            TEXT,
    perspective         TEXT,
    series              TEXT,
    status              TEXT,
    word_count          INTEGER,
    publish_status      TEXT,
    sign_status         TEXT,
    first_pub_time      TEXT,
    last_update_time    TEXT,
    chapter_count       INTEGER,
    review_count        INTEGER,
    favorite_count      INTEGER,
    nutrient_count      INTEGER,
    total_click_count   INTEGER,
    score               BIGINT,
    cover_url           TEXT
);
"""

_CREATE_TABLE_SQLITE = """
CREATE TABLE IF NOT EXISTS book (
    book_id             INTEGER PRIMARY KEY,
    title               TEXT,
    author              TEXT,
    intro               TEXT,
    tags                TEXT,
    main_chars          TEXT,
    support_chars       TEXT,
    other_info          TEXT,
    category            TEXT,
    perspective         TEXT,
    series              TEXT,
    status              TEXT,
    word_count          INTEGER,
    publish_status      TEXT,
    sign_status         TEXT,
    first_pub_time      TEXT,
    last_update_time    TEXT,
    chapter_count       INTEGER,
    review_count        INTEGER,
    favorite_count      INTEGER,
    nutrient_count      INTEGER,
    total_click_count   INTEGER,
    score               INTEGER,
    cover_url           TEXT
);
"""

_INDEXES = [
    ("idx_book_title",  "CREATE INDEX IF NOT EXISTS idx_book_title  ON book(title)"),
    ("idx_book_tags",   "CREATE INDEX IF NOT EXISTS idx_book_tags   ON book(tags)"),
    ("idx_book_author", "CREATE INDEX IF NOT EXISTS idx_book_author ON book(author)"),
]


def init_db_indexes():
    """启动时建表（如不存在）并创建索引。"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            ddl = _CREATE_TABLE_PG if DATABASE_URL else _CREATE_TABLE_SQLITE
            cursor.execute(ddl)
            for _, sql in _INDEXES:
                cursor.execute(sql)
        except Exception as e:
            print(f"数据库初始化失败: {e}")
