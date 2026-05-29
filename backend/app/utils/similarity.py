"""
相似度计算工具模块
"""
from typing import Optional, List, Dict


# 区分度极低的「基调」标签：几乎人人都有，单独命中不构成有意义的相似。
# 生成推荐理由时把它们从「核心匹配」里剔除，避免出现「仅凭正剧凑数」的假理由。
GENERIC_MOOD_TAGS = frozenset({"正剧", "轻松", "温馨"})

# 类型背景词归一化（category 第三段）
_BACKGROUND_MAP = {
    "近代现代": "现代",
    "古色古香": "古代",
    "架空历史": "架空",
    "幻想未来": "未来",
    "未来架空": "未来",
    "上古先秦": "上古",
    "二次元": "二次元",
}


def _parse_category(category: Optional[str]) -> tuple[str, str]:
    """从 '原创-言情-近代现代-爱情' 解析出 (频道, 背景)，如 ('言情', '现代')。"""
    if not category:
        return "", ""
    parts = [p for p in category.split("-") if p]
    channel = parts[1] if len(parts) > 1 else ""
    bg_raw = parts[2] if len(parts) > 2 else ""
    return channel, _BACKGROUND_MAP.get(bg_raw, bg_raw)


def _build_match_summary(
    novel2: dict,
    common_specific: List[str],
    common_mood: List[str],
    category_match: bool,
    perspective_match: str,
    author_match: str,
    tag_sim: float,
) -> str:
    """把结构化的匹配信号合成一句「为什么相似」的人话，区分真重合与凑数。"""
    lead: List[str] = []

    if author_match:
        lead.append(f"{author_match}的另一部作品")

    cat_seg = ""
    if category_match:
        channel, bg = _parse_category(novel2.get("category"))
        seg = f"{bg}{channel}".strip()
        if seg:
            cat_seg = f"同为{seg}文"

    persp_seg = f"{perspective_match}视角叙事" if perspective_match else ""

    if cat_seg and persp_seg:
        lead.append(f"{cat_seg}、{persp_seg}")
    elif cat_seg:
        lead.append(cat_seg)
    elif persp_seg:
        lead.append(f"同为{persp_seg}")

    if common_specific:
        lead.append(f"都带「{'、'.join(common_specific[:3])}」")
        if tag_sim > 0.5:
            tail = "情节标签高度重合"
        elif tag_sim > 0.2:
            tail = "题材有明显重叠"
        else:
            tail = "题材部分相近"
        if common_mood:
            tail += f"，整体基调同为{'、'.join(common_mood[:2])}"
        lead.append(tail)
    else:
        # 没有任何「实质题材标签」重合：诚实说明相似度有限，不夸大
        if common_mood:
            lead.append(
                f"但情节标签几乎无重合，相似主要来自基调（{'、'.join(common_mood[:2])}），匹配度有限"
            )
        else:
            lead.append("相似主要来自类型与视角，建议结合简介判断")

    return "，".join(p for p in lead if p) + "。"


def calculate_tag_similarity(
    tags1: Optional[str],
    tags2: Optional[str],
    idf: Optional[Dict[str, float]] = None,
    default_idf: float = 1.0,
) -> float:
    """
    计算两个标签字符串的 Jaccard 相似度。

    - 不传 idf：普通 Jaccard = |交集| / |并集|（所有标签等权）
    - 传 idf：加权 Jaccard = Σidf(交集) / Σidf(并集)，
      高频标签(正剧/甜文)权重低，稀有强信号标签(破镜重圆)权重高。

    Args:
        tags1: 第一个标签字符串，如 "强强 江湖 正剧"
        tags2: 第二个标签字符串，如 "强强 现代 正剧"
        idf: 可选的 {标签: IDF} 权重表
        default_idf: idf 表里没有的标签的兜底权重

    Returns:
        float: 相似度分数，范围[0, 1]

    Examples:
        >>> calculate_tag_similarity("强强 江湖 正剧", "强强 现代 正剧")
        0.6666666666666666  # 2/3，交集{强强,正剧}，并集{强强,江湖,正剧,现代}
    """
    if not tags1 or not tags2:
        return 0.0

    # 将标签字符串按空格分割成集合
    set1 = set(tags1.strip().split())
    set2 = set(tags2.strip().split())

    # 如果两个集合都为空
    if not set1 or not set2:
        return 0.0

    intersection = set1 & set2
    union = set1 | set2

    if idf is None:
        # 普通 Jaccard（保持向后兼容）
        return len(intersection) / len(union) if union else 0.0

    # IDF 加权 Jaccard
    inter_w = sum(idf.get(t, default_idf) for t in intersection)
    union_w = sum(idf.get(t, default_idf) for t in union)
    return inter_w / union_w if union_w > 0 else 0.0


def parse_tags(tags_str: Optional[str]) -> List[str]:
    """
    解析标签字符串为标签列表

    Args:
        tags_str: 标签字符串，如 "强强 江湖 正剧"

    Returns:
        List[str]: 标签列表，如 ["强强", "江湖", "正剧"]
    """
    if not tags_str:
        return []
    return [tag.strip() for tag in tags_str.split() if tag.strip()]


def calculate_multidimensional_similarity(
    novel1: dict,
    novel2: dict,
    weights: Optional[dict] = None,
    tag_idf: Optional[Dict[str, float]] = None,
    default_idf: float = 1.0,
) -> tuple[float, List[str], str]:
    """
    计算两本小说的多维度相似度

    基于以下维度计算：
    1. 标签相似度（默认权重55%）
    2. 类型匹配（默认权重18%）
    3. 视角匹配（默认权重17%）
    4. 同作者加分（默认权重10%）

    注：完结状态不计入相似度计算

    Args:
        novel1: 第一本小说的字典数据
        novel2: 第二本小说的字典数据
        weights: 权重配置字典，如 {"tags": 0.55, "category": 0.18, ...}

    Returns:
        tuple: (相似度分数[0-100], 匹配标签列表, 推荐理由整句)

    Example:
        >>> similarity, reasons, summary = calculate_multidimensional_similarity(novel1, novel2)
        >>> print(f"相似度: {similarity}%")
        >>> print(f"匹配标签: {reasons}")
        >>> print(f"推荐理由: {summary}")
    """
    # 默认权重配置（完结状态已移除）
    default_weights = {
        "tags": 0.55,
        "category": 0.18,
        "perspective": 0.17,
        "author": 0.1
    }

    # 使用自定义权重或默认权重
    w = weights or default_weights

    score = 0.0

    # ── 打分逻辑保持不变，仅收集结构化信号用于生成理由 ──────────────
    # 1. 标签相似度
    tags1 = novel1.get("tags") or ""
    tags2 = novel2.get("tags") or ""
    tag_sim = calculate_tag_similarity(tags1, tags2, tag_idf, default_idf)

    common_specific: List[str] = []  # 有区分度的题材标签
    common_mood: List[str] = []      # 低区分度的基调标签（正剧/轻松等）
    if tag_sim > 0:
        score += tag_sim * w["tags"]
        # 保留原始顺序，把共同标签分成「实质题材」与「基调」两类
        seen = set(tags2.split())
        for t in tags1.split():
            if t in seen and t not in common_specific and t not in common_mood:
                (common_mood if t in GENERIC_MOOD_TAGS else common_specific).append(t)

    # 2. 类型匹配
    category_match = bool(
        novel1.get("category")
        and novel2.get("category")
        and novel1["category"] == novel2["category"]
    )
    if category_match:
        score += w["category"]

    # 3. 视角匹配
    perspective_match = ""
    if (
        novel1.get("perspective")
        and novel2.get("perspective")
        and novel1["perspective"] == novel2["perspective"]
    ):
        score += w["perspective"]
        perspective_match = novel2["perspective"]

    # 4. 同作者加分
    author_match = ""
    if novel1.get("author") and novel2.get("author") and novel1["author"] == novel2["author"]:
        score += w["author"]
        author_match = novel2["author"]

    # ── 生成理由 ───────────────────────────────────────────────────
    # chips：短标签药丸（前端最多显示 2 个），优先放有区分度的题材标签
    reasons: List[str] = list(common_specific[:2])
    if author_match and len(reasons) < 2:
        reasons.append("同作者")
    if not reasons:
        if perspective_match:
            reasons.append(f"{perspective_match}视角")
        elif category_match:
            reasons.append("同题材")
        elif common_mood:
            reasons.append(common_mood[0])

    # summary：一句「为什么相似」的人话
    summary = _build_match_summary(
        novel2, common_specific, common_mood,
        category_match, perspective_match, author_match, tag_sim,
    )

    # 转换为百分比分数（0-100）
    final_score = score * 100

    return final_score, reasons, summary


if __name__ == "__main__":
    # 测试标签相似度计算
    tags_a = "强强 江湖 三教九流 正剧"
    tags_b = "强强 灵异神怪 现代架空 正剧"

    similarity = calculate_tag_similarity(tags_a, tags_b)
    print(f"标签A: {tags_a}")
    print(f"标签B: {tags_b}")
    print(f"Jaccard相似度: {similarity:.2%}")
    print()

    # 测试多维度相似度计算
    novel1 = {
        "title": "天涯客",
        "author": "priest",
        "tags": "强强 江湖 三教九流 正剧",
        "category": "原创-纯爱-架空历史-爱情",
        "perspective": "主受",
        "status": "完结"
    }

    novel2 = {
        "title": "镇魂",
        "author": "priest",
        "tags": "强强 灵异神怪 现代架空 正剧",
        "category": "原创-纯爱-近代现代-爱情",
        "perspective": "主受",
        "status": "完结"
    }

    score, reasons, summary = calculate_multidimensional_similarity(novel1, novel2)
    print(f"小说1: {novel1['title']}")
    print(f"小说2: {novel2['title']}")
    print(f"综合相似度: {score:.2f}%")
    print(f"匹配标签: {', '.join(reasons)}")
    print(f"推荐理由: {summary}")
