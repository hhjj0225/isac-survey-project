#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
阶段4: 周度综述生成器 — weekly_survey_generator.py
=============================================================================
读取 paper_cards.jsonl + taxonomy.md + comparison_table.csv，
生成结构化的中文周度综述 weekly_digest.md。

综述包含 7 个部分：
1. 执行摘要
2. 研究方向分类
3. 亮点论文 (Top 3)
4. 新兴话题与趋势
5. 方法对比总表
6. 统计信息
7. 参考文献

用法：
    python src/weekly_survey_generator.py                # 默认路径
    python src/weekly_survey_generator.py --week 1       # 指定周次
    python src/weekly_survey_generator.py --date-range "2024-01 至 2024-03"
"""

from __future__ import annotations
import argparse
import sys
import os
import time
from typing import List, Dict, Any
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from lib.card_schema import load_cards_from_jsonl, PaperCard
from lib.chinese_template import ChineseTemplate
from lib.comparison_table import ComparisonTable


# ============================================================================
# 主生成函数
# ============================================================================

def generate_weekly_digest(
    cards_path: str = None,
    taxonomy_path: str = None,
    comparison_path: str = None,
    output_path: str = None,
    week_number: int = 1,
    date_range: str = "",
    verbose: bool = True,
) -> str:
    """生成完整的周度综述。

    Args:
        cards_path: 论文卡片 JSONL 文件路径
        taxonomy_path: 分类法 Markdown 文件路径
        comparison_path: 对比表 CSV 文件路径
        output_path: 输出路径
        week_number: 周次编号
        date_range: 日期范围字符串
        verbose: 是否打印详细信息

    Returns:
        综述 Markdown 字符串
    """
    if cards_path is None:
        cards_path = str(config.PAPER_CARDS_PATH)
    if taxonomy_path is None:
        taxonomy_path = str(config.TAXONOMY_PATH)
    if comparison_path is None:
        comparison_path = str(config.COMPARISON_TABLE_PATH)
    if output_path is None:
        output_path = str(config.WEEKLY_DIGEST_PATH)

    tpl = ChineseTemplate()
    week_label = f"第{week_number}周"

    # ---- 加载数据 ----
    if verbose:
        print(f"[加载] 论文卡片: {cards_path}")
    cards = load_cards_from_jsonl(cards_path)
    if verbose:
        print(f"  加载 {len(cards)} 张卡片")

    # 读取分类法
    taxonomy_content = ""
    if os.path.exists(taxonomy_path):
        with open(taxonomy_path, "r", encoding="utf-8") as f:
            taxonomy_content = f.read()
        if verbose:
            print(f"[加载] 分类法: {taxonomy_path} ({len(taxonomy_content)} 字符)")
    else:
        if verbose:
            print(f"[警告] 分类法文件不存在: {taxonomy_path}")

    # 读取对比表
    comparison_stats = ""
    if os.path.exists(comparison_path):
        df = ComparisonTable.load_csv(comparison_path)
        comparison_stats = ComparisonTable.generate_summary_stats(df)
        if verbose:
            print(f"[加载] 对比表: {comparison_path} ({len(df)} 行)")
    else:
        if verbose:
            print(f"[警告] 对比表文件不存在: {comparison_path}")

    # ---- 数据提取与统计 ----
    if verbose:
        print(f"[分析] 提取统计信息...")

    # 日期范围
    if not date_range and cards:
        dates = [c.published_date for c in cards if c.published_date]
        if dates:
            date_range = f"{min(dates)} 至 {max(dates)}"

    # 置信度分布
    conf_dist = {"high": 0, "medium": 0, "low": 0}
    for c in cards:
        conf_dist[c.confidence_level] = conf_dist.get(c.confidence_level, 0) + 1

    # 创新类型分布
    innov_dist = {}
    for c in cards:
        t = c.innovation_type or "unknown"
        innov_dist[t] = innov_dist.get(t, 0) + 1

    # ISAC 子类别分布
    cat_dist = {}
    for c in cards:
        cat = c.best_fit_category or "未分类"
        cat_dist[cat] = cat_dist.get(cat, 0) + 1

    # 平均完整度
    avg_completeness = (
        sum(c.completeness_score() for c in cards) / max(len(cards), 1)
    )

    # ---- 构建分类概览 ----
    # 从分类法中提取簇信息（如果可用）
    clusters = _extract_clusters_from_cards(cards)
    cluster_count = len(set(c.best_fit_category for c in cards
                            if c.best_fit_category != config.PLACEHOLDER_TEXT))

    # ---- 构建亮点论文 ----
    highlight_papers = _select_highlight_papers(cards, top_n=config.HIGHLIGHT_TOP_N)

    # ---- 构建新兴话题 ----
    emerging = _detect_emerging_topics(cards)

    # ---- 构建关键发现 ----
    key_findings = _generate_key_findings(cards, conf_dist, cat_dist)

    # ---- 组装综述 ----
    if verbose:
        print(f"[生成] 组装综述文档...")

    sections = []

    # 1. 标题
    sections.append(tpl.header(week_label, len(cards), date_range))

    # 2. 执行摘要
    top_cats = [
        {"name": cat, "count": cnt, "pct": cnt / max(len(cards), 1)}
        for cat, cnt in sorted(cat_dist.items(), key=lambda x: -x[1])
    ]
    emerging_names = [e.get("name", "") for e in emerging]
    sections.append(tpl.executive_summary(
        paper_count=len(cards),
        cluster_count=max(cluster_count, 1),
        top_categories=top_cats[:5],
        emerging_topics=emerging_names[:3],
        key_findings=key_findings,
    ))

    # 3. 分类法概览
    cluster_summaries = []
    for cat, cnt in sorted(cat_dist.items(), key=lambda x: -x[1]):
        cluster_summaries.append({
            "name": cat,
            "count": cnt,
            "keywords": _extract_keywords_for_category(cards, cat),
        })
    sections.append(tpl.taxonomy_overview(
        clusters=cluster_summaries,
        taxonomy_content=taxonomy_content,
    ))

    # 4. 亮点论文
    sections.append(tpl.highlight_papers(highlight_papers))

    # 5. 新兴话题
    trend_descriptions = [
        "深度学习与强化学习方法在ISAC中的应用持续增长，尤其在波束管理和资源分配方面",
        "RIS/智能超表面技术成为ISAC硬件实现的重要支撑",
        "全双工和NOMA技术与ISAC的融合研究逐步深入",
        "面向实际部署的研究（多小区、非理想CSI、移动场景）正在增多",
    ]
    sections.append(tpl.emerging_topics(emerging, trend_descriptions))

    # 6. 对比表引用
    sections.append(tpl.comparison_reference(
        csv_path=comparison_path,
        stats_text=comparison_stats,
    ))

    # 7. 统计信息
    sections.append(tpl.statistics(
        paper_count=len(cards),
        conf_dist=conf_dist,
        innov_dist=innov_dist,
        cat_dist=cat_dist,
        date_range=date_range,
        avg_completeness=avg_completeness,
    ))

    # 8. 参考文献
    refs = []
    for c in cards:
        refs.append({
            "arxiv_id": c.arxiv_id,
            "title": c.title,
            "authors": c.authors,
            "published_date": c.published_date,
        })
    sections.append(tpl.references(refs))

    # 9. 页脚
    sections.append(tpl.footer())

    # 组合
    digest = "\n\n".join(sections)

    # ---- 保存 ----
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(digest)

    if verbose:
        print(f"[保存] 综述已保存至: {output_path}")
        print(f"  总长度: {len(digest)} 字符")
        print(f"  论文数: {len(cards)}")

    return digest


# ============================================================================
# 辅助函数
# ============================================================================

def _extract_clusters_from_cards(cards: List[PaperCard]) -> List[Dict[str, Any]]:
    """从论文卡片中提取分类簇信息。

    Args:
        cards: 论文卡片列表

    Returns:
        簇信息列表
    """
    clusters = {}
    for c in cards:
        cat = c.best_fit_category or "未分类"
        if cat not in clusters:
            clusters[cat] = {"name": cat, "count": 0, "cards": []}
        clusters[cat]["count"] += 1
        clusters[cat]["cards"].append(c)

    return sorted(clusters.values(), key=lambda x: -x["count"])


def _extract_keywords_for_category(
    cards: List[PaperCard],
    category: str,
    top_n: int = 5,
) -> List[str]:
    """为给定类别提取代表性关键词。

    使用该类别下论文的 best_fit_category 对应的 ISAC 关键词词表。

    Args:
        cards: 论文卡片列表
        category: 类别名
        top_n: 返回关键词数

    Returns:
        关键词列表
    """
    # 从 ISAC_SUBCATEGORIES 词表中获取该类别的主要关键词
    if category in config.ISAC_SUBCATEGORIES:
        return config.ISAC_SUBCATEGORIES[category][:top_n]
    # 回退：返回类别名本身
    return [category]


def _select_highlight_papers(
    cards: List[PaperCard],
    top_n: int = 3,
) -> List[Dict[str, Any]]:
    """从论文卡片中选择亮点论文。

    选择标准：高置信度 + 高完整度 + 清晰的创新表述。

    Args:
        cards: 论文卡片列表
        top_n: 选择数量

    Returns:
        亮点论文信息列表
    """
    scored = []
    for c in cards:
        # 计算综合得分
        score = 0.0
        score += c.completeness_score() * 40  # 完整度 40%
        if c.confidence_level == "high":
            score += 30
        elif c.confidence_level == "medium":
            score += 15
        # 鼓励非默认创新类型
        if c.innovation_type in ["novel_approach", "unified_framework", "theoretical_contribution"]:
            score += 20
        elif c.innovation_type in ["integration", "extension"]:
            score += 10
        # 标题长度适中（不极端）
        title_len = len(c.title)
        if 40 < title_len < 150:
            score += 10

        scored.append((score, c))

    scored.sort(key=lambda x: -x[0])

    highlights = []
    for score, c in scored[:top_n]:
        highlights.append({
            "title": c.title,
            "arxiv_id": c.arxiv_id,
            "reason": _generate_recommendation_reason(c),
            "innovation_type": config.INNOVATION_TYPES.get(
                c.innovation_type, {}
            ).get("label_zh", c.innovation_type) if isinstance(
                config.INNOVATION_TYPES.get(c.innovation_type, {}), dict
            ) else c.innovation_type,
            "best_fit_category": c.best_fit_category,
            "excerpt": c.key_idea[:300] if c.key_idea and c.key_idea != config.PLACEHOLDER_TEXT else c.abstract_raw[:300],
        })
    return highlights


def _generate_recommendation_reason(card: PaperCard) -> str:
    """为论文生成推荐理由。

    Args:
        card: 论文卡片

    Returns:
        中文推荐理由
    """
    reasons = []

    if card.confidence_level == "high":
        reasons.append("摘要信息完整、提取质量高")
    if card.innovation_type == "novel_approach":
        reasons.append("提出了全新的技术方案")
    elif card.innovation_type == "unified_framework":
        reasons.append("构建了统一的理论框架")
    elif card.innovation_type == "theoretical_contribution":
        reasons.append("具有扎实的理论分析基础")

    if card.completeness_score() >= 0.9:
        reasons.append("方法描述完整清晰")

    if not reasons:
        reasons.append("方法具有一定参考价值")

    return "；".join(reasons[:3])


def _detect_emerging_topics(cards: List[PaperCard]) -> List[Dict[str, Any]]:
    """检测新兴研究话题。

    基于论文的 key_idea 和 best_fit_category 进行趋势分析。

    Args:
        cards: 论文卡片列表

    Returns:
        新兴话题列表
    """
    topics = []

    # 检测关键词热度
    keyword_hits = {}
    emerging_keywords = [
        ("transformer", "Transformer架构", "将Transformer等新型神经网络架构应用于ISAC"),
        ("diffusion", "扩散模型", "利用扩散模型进行ISAC信号处理和资源优化"),
        ("semantic", "语义通信", "ISAC与语义通信的融合研究"),
        ("near-field", "近场ISAC", "利用近场球面波前特性增强ISAC性能"),
        ("XL-MIMO", "超大规模MIMO", "超大规模天线阵列在ISAC系统中的应用"),
        ("multi-functional", "多功能网络", "将ISAC能力融入多功能网络架构"),
    ]

    for keyword, name, description in emerging_keywords:
        count = sum(
            1 for c in cards
            if keyword.lower() in (c.key_idea + " " + c.title + " " + c.abstract_raw).lower()
        )
        if count >= 1:
            keyword_hits[name] = {"name": name, "description": description, "paper_count": count}

    # 排序返回
    for name, info in sorted(keyword_hits.items(), key=lambda x: -x[1]["paper_count"]):
        topics.append(info)

    return topics


def _generate_key_findings(
    cards: List[PaperCard],
    conf_dist: Dict[str, int],
    cat_dist: Dict[str, int],
) -> List[str]:
    """从论文数据生成关键发现。

    Args:
        cards: 论文卡片列表
        conf_dist: 置信度分布
        cat_dist: 类别分布

    Returns:
        关键发现（中文描述列表）
    """
    findings = []

    # 发现1: 主要研究方向
    if cat_dist:
        top_cat = max(cat_dist, key=cat_dist.get)
        top_count = cat_dist[top_cat]
        findings.append(
            f"本周期研究最活跃的方向是 **{top_cat}**，"
            f"共收录 {top_count} 篇相关论文，"
            f"占论文总数的 {top_count/max(len(cards),1):.0%}"
        )

    # 发现2: 置信度情况
    high_ratio = conf_dist.get("high", 0) / max(len(cards), 1)
    if high_ratio >= 0.5:
        findings.append(
            f"论文摘要质量总体较高，{high_ratio:.0%} 的论文达到 HIGH 置信度提取水平"
        )
    elif high_ratio >= 0.3:
        findings.append(
            f"约 {high_ratio:.0%} 的论文摘要包含充足的结构化信息，"
            f"建议对 MEDIUM/LOW 置信度的论文进行人工补充审核"
        )
    else:
        findings.append(
            f"仅 {high_ratio:.0%} 的论文达到高置信度提取，"
            f"建议优先获取完整全文以补充卡片内容"
        )

    # 发现3: 方法趋势
    dl_count = sum(
        1 for c in cards
        if any(kw in (c.method + " " + c.key_idea).lower()
               for kw in ["deep learning", "neural network", "reinforcement learning",
                          "machine learning", "CNN", "DNN", "transformer"])
    )
    if dl_count > len(cards) * 0.2:
        findings.append(
            f"基于深度学习/机器学习的方法持续增长，"
            f"约 {dl_count} 篇论文采用了AI相关技术"
        )

    return findings


# ============================================================================
# 命令行入口
# ============================================================================

def main():
    """命令行入口函数。"""
    parser = argparse.ArgumentParser(
        description="ISAC 周度综述生成器 — 生成结构化中文文献综述",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python src/weekly_survey_generator.py               # 默认路径
    python src/weekly_survey_generator.py --week 1      # 指定周次
    python src/weekly_survey_generator.py --week 3 --date-range "2024-01~2024-03"
        """,
    )
    parser.add_argument(
        "--cards", type=str, default=None,
        help=f"论文卡片 JSONL (默认: {config.PAPER_CARDS_PATH})"
    )
    parser.add_argument(
        "--taxonomy", type=str, default=None,
        help=f"分类法 Markdown (默认: {config.TAXONOMY_PATH})"
    )
    parser.add_argument(
        "--comparison", type=str, default=None,
        help=f"对比表 CSV (默认: {config.COMPARISON_TABLE_PATH})"
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help=f"综述输出路径 (默认: {config.WEEKLY_DIGEST_PATH})"
    )
    parser.add_argument(
        "--week", type=int, default=1,
        help="周次编号 (默认: 1)"
    )
    parser.add_argument(
        "--date-range", type=str, default="",
        help="日期范围，如 '2024-01 至 2024-03'"
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="静默模式"
    )

    args = parser.parse_args()

    try:
        digest = generate_weekly_digest(
            cards_path=args.cards,
            taxonomy_path=args.taxonomy,
            comparison_path=args.comparison,
            output_path=args.output,
            week_number=args.week,
            date_range=args.date_range,
            verbose=not args.quiet,
        )
    except FileNotFoundError as e:
        print(f"错误: 文件未找到 - {e}", file=sys.stderr)
        print("提示: 请先运行完整的流水线 (fetch → generate → cluster)", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print(f"\n完成! 综述已生成。")


if __name__ == "__main__":
    main()
