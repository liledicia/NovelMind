#!/usr/bin/env python3
"""
数据迁移脚本：SQLite → PostgreSQL

用法：
    export DATABASE_URL=postgresql://user:password@host:5432/dbname
    python scripts/migrate_sqlite_to_postgres.py [sqlite_path]

sqlite_path 默认为项目根目录的 jinjiang_novels.db
"""

import os
import sys
import sqlite3
import psycopg2
import psycopg2.extras
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
DEFAULT_SQLITE = BASE_DIR / "jinjiang_novels.db"

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    print("❌ 请先设置 DATABASE_URL 环境变量")
    sys.exit(1)

sqlite_path = sys.argv[1] if len(sys.argv) > 1 else str(DEFAULT_SQLITE)
if not Path(sqlite_path).exists():
    print(f"❌ SQLite 文件不存在: {sqlite_path}")
    sys.exit(1)

print(f"📖 读取 SQLite: {sqlite_path}")
sqlite_conn = sqlite3.connect(sqlite_path)
sqlite_conn.row_factory = sqlite3.Row

print(f"🔌 连接 PostgreSQL...")
pg_conn = psycopg2.connect(DATABASE_URL)
pg_cur = pg_conn.cursor()

# 建表
pg_cur.execute("""
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
)
""")

# 迁移数据
rows = sqlite_conn.execute("SELECT * FROM book").fetchall()
print(f"📦 共 {len(rows)} 条记录，开始迁移...")

cols = [
    "book_id","title","author","intro","tags","main_chars","support_chars",
    "other_info","category","perspective","series","status","word_count",
    "publish_status","sign_status","first_pub_time","last_update_time",
    "chapter_count","review_count","favorite_count","nutrient_count",
    "total_click_count","score","cover_url"
]
placeholders = ",".join(["%s"] * len(cols))
col_str = ",".join(cols)
update_str = ",".join(f"{c}=EXCLUDED.{c}" for c in cols if c != "book_id")

upsert_sql = f"""
INSERT INTO book ({col_str}) VALUES ({placeholders})
ON CONFLICT (book_id) DO UPDATE SET {update_str}
"""

success = 0
errors = 0
for row in rows:
    try:
        row_dict = dict(row)
        values = tuple(row_dict.get(c) for c in cols)
        pg_cur.execute(upsert_sql, values)
        success += 1
    except Exception as e:
        errors += 1
        print(f"  ⚠ book_id={row['book_id']} 失败: {e}")
        pg_conn.rollback()

pg_conn.commit()

# 创建索引
for idx_sql in [
    "CREATE INDEX IF NOT EXISTS idx_book_title  ON book(title)",
    "CREATE INDEX IF NOT EXISTS idx_book_tags   ON book(tags)",
    "CREATE INDEX IF NOT EXISTS idx_book_author ON book(author)",
]:
    pg_cur.execute(idx_sql)
pg_conn.commit()

pg_cur.close()
pg_conn.close()
sqlite_conn.close()

print(f"\n✅ 迁移完成：成功 {success} 条，失败 {errors} 条")
