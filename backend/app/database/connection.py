"""
数据库连接管理模块
"""
import sqlite3
import os
from contextlib import contextmanager
from typing import Generator


# 数据库文件路径（相对于backend/app目录）
DB_PATH = os.path.join(os.path.dirname(__file__), '../../../jinjiang_novels.db')


@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """
    数据库连接上下文管理器

    使用示例：
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM book")
            results = cursor.fetchall()

    Yields:
        sqlite3.Connection: SQLite数据库连接对象
    """
    conn = sqlite3.connect(DB_PATH)
    # 设置row_factory以字典方式访问查询结果
    conn.row_factory = sqlite3.Row

    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def init_db_indexes():
    """
    初始化数据库索引以优化查询性能
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 创建索引（如果不存在）
        try:
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_book_title
                ON book(title)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_book_tags
                ON book(tags)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_book_author
                ON book(author)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_stats_book_id
                ON stats(book_id)
            """)
            print("数据库索引初始化成功")
        except Exception as e:
            print(f"索引创建失败（可能已存在）: {e}")


def test_connection():
    """测试数据库连接"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM book")
            result = cursor.fetchone()
            print(f"数据库连接成功！当前共有 {result['count']} 本小说")
            return True
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return False


if __name__ == "__main__":
    # 测试数据库连接
    test_connection()
    # 初始化索引
    init_db_indexes()
