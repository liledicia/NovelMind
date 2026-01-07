"""
相似度计算工具模块
"""
from typing import Optional, List


def calculate_tag_similarity(tags1: Optional[str], tags2: Optional[str]) -> float:
    """
    计算两个标签字符串的Jaccard相似度

    Jaccard相似系数 = |交集| / |并集|

    Args:
        tags1: 第一个标签字符串，如 "强强 江湖 正剧"
        tags2: 第二个标签字符串，如 "强强 现代 正剧"

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

    # 计算交集和并集
    intersection = len(set1 & set2)  # 交集
    union = len(set1 | set2)  # 并集

    # 返回Jaccard系数
    return intersection / union if union > 0 else 0.0


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
    weights: Optional[dict] = None
) -> tuple[float, List[str]]:
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
        tuple: (相似度分数[0-100], 匹配原因列表)

    Example:
        >>> similarity, reasons = calculate_multidimensional_similarity(novel1, novel2)
        >>> print(f"相似度: {similarity}%")
        >>> print(f"匹配原因: {reasons}")
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
    reasons = []

    # 1. 标签相似度
    tags1 = novel1.get("tags") or ""
    tags2 = novel2.get("tags") or ""
    tag_sim = calculate_tag_similarity(tags1, tags2)

    if tag_sim > 0:
        score += tag_sim * w["tags"]
        # 找出共同标签
        common_tags = list(set(tags1.split()) & set(tags2.split()))
        if common_tags:
            # 只显示前2个共同标签
            tag_display = '、'.join(common_tags[:2])
            if len(common_tags) > 2:
                reasons.append(f"共同标签：{tag_display}等")
            else:
                reasons.append(f"共同标签：{tag_display}")

    # 2. 类型匹配
    if novel1.get("category") and novel2.get("category"):
        if novel1["category"] == novel2["category"]:
            score += w["category"]
            # 提取类型的关键词
            category = novel2.get("category", "")
            if category:
                # 从类型中提取最后一个词作为核心类型
                parts = category.split('-')
                core_type = parts[-1] if parts else "相似类型"
                reasons.append(f"同为{core_type}题材")

    # 3. 视角匹配
    if novel1.get("perspective") and novel2.get("perspective"):
        if novel1["perspective"] == novel2["perspective"]:
            score += w["perspective"]
            perspective = novel2.get("perspective", "")
            reasons.append(f"{perspective}视角叙事")

    # 4. 同作者加分
    if novel1.get("author") and novel2.get("author"):
        if novel1["author"] == novel2["author"]:
            score += w["author"]
            author = novel2.get("author", "")
            reasons.append(f"{author}的其他作品")

    # 转换为百分比分数（0-100）
    final_score = score * 100

    return final_score, reasons


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

    score, reasons = calculate_multidimensional_similarity(novel1, novel2)
    print(f"小说1: {novel1['title']}")
    print(f"小说2: {novel2['title']}")
    print(f"综合相似度: {score:.2f}%")
    print(f"匹配原因: {', '.join(reasons)}")
