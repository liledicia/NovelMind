#!/usr/bin/env python3
"""探索性分析：评估 intro 文案文本质量，判断是否值得上 TF-IDF。"""
import sqlite3
import re
from collections import Counter
from pathlib import Path
import jieba

BASE = Path(__file__).parent.parent.parent
conn = sqlite3.connect(BASE / "jinjiang_novels.db")
conn.row_factory = sqlite3.Row
rows = conn.execute("SELECT book_id, title, intro, tags FROM book").fetchall()
conn.close()

intros = [(r["title"], (r["intro"] or "").strip()) for r in rows]
total = len(intros)

# ── 1. 文本长度分布 & 无效文案占比 ──────────────────────────
empties = ["", "无", "暂无", "无。", "略", "暂无简介", "简介迟些", "-"]
lengths = [len(t) for _, t in intros]
useless = sum(1 for _, t in intros if t in empties or len(t) < 10)

buckets = {"0-20": 0, "20-50": 0, "50-100": 0, "100-200": 0, "200+": 0}
for L in lengths:
    if L < 20: buckets["0-20"] += 1
    elif L < 50: buckets["20-50"] += 1
    elif L < 100: buckets["50-100"] += 1
    elif L < 200: buckets["100-200"] += 1
    else: buckets["200+"] += 1

print("=" * 60)
print(f"总书数: {total}")
print(f"文案<10字 或 占位符(无/暂无等): {useless} 本 ({100*useless/total:.1f}%)")
print(f"文案长度: 最短 {min(lengths)}, 最长 {max(lengths)}, 平均 {sum(lengths)/total:.0f}")
print(f"\n长度分布:")
for k, v in buckets.items():
    bar = "█" * int(50 * v / total)
    print(f"  {k:>8} 字: {v:>5} ({100*v/total:>4.1f}%) {bar}")

# ── 2. 分词 + 关键词频率（去停用词）─────────────────────────
stop = set("的 了 是 在 我 你 他 她 它 们 和 与 也 都 就 不 这 那 有 一个 一 之 而 又 着 过 被 把 让 给 向 从 到 为 以 及 或 但 却 并 很 最 更 还 没 要 会 能 可 可以 因为 所以 如果 虽然 但是 一种 一样 自己 什么 怎么 这样 那样 起来 出来 这个 那个 ， 。 、 ！ ？ ； ： （ ） 《 》 “ ” ‘ ’ … — \n \r \t".split())

word_freq = Counter()
doc_freq = Counter()  # 出现该词的文档数（用于看区分度）
for _, t in intros:
    if len(t) < 10:
        continue
    words = [w for w in jieba.cut(t) if len(w) >= 2 and not re.match(r'^[\d\W]+$', w) and w not in stop]
    word_freq.update(words)
    for w in set(words):
        doc_freq[w] += 1

print(f"\n词汇表大小（去停用词，≥2字）: {len(word_freq)}")
print(f"\nTop 25 高频词（频次 / 出现文档数 / 文档占比）:")
for w, c in word_freq.most_common(25):
    df = doc_freq[w]
    print(f"  {w:<8} 频次{c:>5}  文档{df:>5}  ({100*df/total:>4.1f}%)")

# ── 3. 区分度好的中频词（DF 在 0.5%-10% 之间，最适合做 TF-IDF 特征）──
print(f"\n区分度较好的中频词样本（出现在 0.5%-8% 文档，适合做特征）:")
mid = [(w, doc_freq[w]) for w in doc_freq if total*0.005 <= doc_freq[w] <= total*0.08]
mid.sort(key=lambda x: -x[1])
print("  " + "  ".join(f"{w}({df})" for w, df in mid[:30]))
print(f"  中频词总数: {len(mid)}")
