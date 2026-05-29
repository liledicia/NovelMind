"""
批量补全全库小说统计数据（收藏/书评/营养液/点击/积分）。

背景：桌面端静态页抓不到营养液/点击数，全库历史入库的书统计几乎全空。
本脚本遍历所有缺统计的书，调晋江移动端 JSON API 补全并写回数据库，
让推荐排序的「热度加权」立刻有数据可用。

特性：
- 断点续跑：只处理 nutrient_count IS NULL 的书，中断后重跑自动跳过已完成的
- 限速：每本之间 sleep 1~2s（由 crawler.fetch_stats_via_mobile_api 内部控制）防封
- 数据库自适应：有 DATABASE_URL → PostgreSQL（线上），否则 SQLite（本地）

用法：
    # 本地 SQLite
    cd backend && ../.venv/bin/python -m scripts.backfill_stats

    # 线上 PostgreSQL（对着 Railway 的库跑）
    cd backend && DATABASE_URL="postgresql://..." python -m scripts.backfill_stats

    # 只跑前 N 本（试跑）
    cd backend && ../.venv/bin/python -m scripts.backfill_stats --limit 20
"""
import argparse
import os
import sys
import time

# 让脚本能 import app.*（把 backend/ 加入路径）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.crawler_service import JinjiangCrawler  # noqa: E402
from app.services.novel_service import get_novel_by_id, insert_novel  # noqa: E402
from app.database.connection import get_db_connection  # noqa: E402


def _fetch_pending_ids(limit=None):
    """取出所有仍缺统计（nutrient_count 为空）的 book_id。"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        sql = "SELECT book_id FROM book WHERE nutrient_count IS NULL ORDER BY book_id"
        if limit:
            sql += f" LIMIT {int(limit)}"
        cursor.execute(sql)
        rows = cursor.fetchall()
    # 兼容 sqlite3.Row 和 RealDictRow
    return [dict(r)["book_id"] for r in rows]


def main():
    parser = argparse.ArgumentParser(description="批量补全小说统计数据")
    parser.add_argument("--limit", type=int, default=None, help="最多处理多少本（试跑用）")
    args = parser.parse_args()

    db = "PostgreSQL（线上）" if os.environ.get("DATABASE_URL") else "SQLite（本地）"
    print(f"数据库: {db}")

    pending = _fetch_pending_ids(args.limit)
    total = len(pending)
    print(f"待补全: {total} 本\n")
    if total == 0:
        print("全部已补全，无需处理。")
        return

    crawler = JinjiangCrawler()
    ok = fail = skip = 0
    start = time.time()

    for i, book_id in enumerate(pending, 1):
        novel = get_novel_by_id(book_id)
        if not novel:
            skip += 1
            continue
        try:
            stats = crawler.fetch_stats_via_mobile_api(book_id)  # 内含 1~2s 限速
            if stats:
                novel.update(stats)
                insert_novel(novel)
                ok += 1
                tag = "✓"
            else:
                fail += 1
                tag = "✗ 无数据"
        except KeyboardInterrupt:
            print("\n已中断（进度已写库，可重跑续传）。")
            break
        except Exception as e:
            fail += 1
            tag = f"✗ {e}"

        title = (novel.get("title") or "")[:18]
        elapsed = time.time() - start
        rate = i / elapsed if elapsed > 0 else 0
        eta = (total - i) / rate if rate > 0 else 0
        print(f"[{i}/{total}] {tag}  {title}  "
              f"(成功{ok}/失败{fail}/跳过{skip}, 预计剩余 {eta/60:.1f} 分钟)")

    print(f"\n完成：成功 {ok}，失败 {fail}，跳过 {skip}，"
          f"耗时 {(time.time()-start)/60:.1f} 分钟。")


if __name__ == "__main__":
    main()
