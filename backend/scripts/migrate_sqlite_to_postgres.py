#!/usr/bin/env python3
"""
数据迁移脚本：SQLite → PostgreSQL（高速批量版）

用法：
    export DATABASE_URL=postgresql://user:password@host:5432/dbname
    python scripts/migrate_sqlite_to_postgres.py [sqlite_path]
"""

import os
import sys
import sqlite3
import psycopg2
from psycopg2.extras import execute_values
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
DEFAULT_SQLITE = BASE_DIR / "jinjiang_novels.db"

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    print("❌ 请先设置 DATABASE_URL 环境变量", flush=True)
    sys.exit(1)

sqlite_path = sys.argv[1] if len(sys.argv) > 1 else str(DEFAULT_SQLITE)
if not Path(sqlite_path).exists():
    print(f"❌ SQLite 文件不存在: {sqlite_path}", flush=True)
    sys.exit(1)

print(f"📖 读取 SQLite: {sqlite_path}", flush=True)
sqlite_conn = sqlite3.connect(sqlite_path)
sqlite_conn.row_factory = sqlite3.Row

print(f"🔌 连接 PostgreSQL...", flush=True)
pg_conn = psycopg2.connect(DATABASE_URL, connect_timeout=15)
pg_cur = pg_conn.cursor()

# Step 1: 建表
print(f"🛠  创建 book 表...", flush=True)
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
pg_conn.commit()

# Step 2: 读所有数据
rows = sqlite_conn.execute("SELECT * FROM book").fetchall()
total = len(rows)
print(f"📦 共 {total} 条记录，开始批量插入...", flush=True)

cols = [
    "book_id","title","author","intro","tags","main_chars","support_chars",
    "other_info","category","perspective","series","status","word_count",
    "publish_status","sign_status","first_pub_time","last_update_time",
    "chapter_count","review_count","favorite_count","nutrient_count",
    "total_click_count","score","cover_url"
]
col_str = ",".join(cols)
update_str = ",".join(f"{c}=EXCLUDED.{c}" for c in cols if c != "book_id")

# 构造数据元组列表
data = []
for row in rows:
    row_dict = dict(row)
    data.append(tuple(row_dict.get(c) for c in cols))

# Step 3: 批量 upsert（每批 1000 条，一次网络往返）
upsert_sql = f"""
INSERT INTO book ({col_str}) VALUES %s
ON CONFLICT (book_id) DO UPDATE SET {update_str}
"""

BATCH = 1000
success = 0
errors = 0

for start in range(0, total, BATCH):
    chunk = data[start:start + BATCH]
    try:
        execute_values(pg_cur, upsert_sql, chunk, page_size=BATCH)
        pg_conn.commit()
        success += len(chunk)
        print(f"  → 进度 {min(start + BATCH, total)}/{total}", flush=True)
    except Exception as e:
        errors += len(chunk)
        print(f"  ⚠ 批次 {start}-{start+len(chunk)} 失败: {e}", flush=True)
        pg_conn.rollback()

# Step 4: 创建索引
print(f"🔍 创建索引...", flush=True)
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

print(f"\n✅ 迁移完成：成功 {success} 条，失败 {errors} 条", flush=True)
