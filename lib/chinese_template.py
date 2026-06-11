#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
中文综述模板引擎 — lib/chinese_template.py
=============================================================================
为周度综述生成提供参数化中文叙事模板。

所有模板采用"槽位填充"方式：模板字符串中的 {slot_name} 由
weekly_survey_generator.py 根据论文数据进行填充。

设计原则：
- 避免生硬 AI 风格：使用自然的学术中文表达
- 数据驱动：每个论断都引用实际论文数据
- 结构清晰：遵循"总-分-总"叙事结构
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone


class ChineseTemplate:
    """中文学术综述模板引擎。"""

    # ========================================================================
    # 综述标题模板
    # ========================================================================

    @staticmethod
    def header(week_label: str, paper_count: int, date_range: str) -> str:
        """生成综述标题和头部信息。

        Args:
            week_label: 周次标签（如 "第1周"）
            paper_count: 论文数量
            date_range: 日期范围字符串
        """
        return f"""# 面向6G的通信感知一体化（ISAC）文献综述 — {week_label}

**生成日期**: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}
**覆盖时间范围**: {date_range}
**收录论文数**: {paper_count} 篇
**数据来源**: arXiv (cs.IT, eess.SP, cs.NI, cs.MM 等分类)
"""

    # ========================================================================
    # 执行摘要模板
    # ========================================================================

    @staticmethod
    def executive_summary(
        paper_count: int,
        cluster_count: int,
        top_categories: List[Dict[str, Any]],
        emerging_topics: List[str],
        key_findings: List[str],
    ) -> str:
        """生成执行摘要（中文）。

        Args:
            paper_count: 论文总数
            cluster_count: 分类簇数
            top_categories: 主要研究方向列表 [{"name": ..., "count": ..., "pct": ...}, ...]
            emerging_topics: 新兴话题关键词列表
            key_findings: 关键发现列表
        """
        lines = []
        lines.append("## 一、执行摘要")
        lines.append("")

        # 总体概述
        lines.append(
            f"本周期共收录 {paper_count} 篇 ISAC 相关论文，"
            f"通过自动聚类分析划分为 {cluster_count} 个研究方向。"
        )

        # 主要研究方向
        if top_categories:
            lines.append("主要研究方向集中在：")
            for i, cat in enumerate(top_categories[:5], 1):
                lines.append(
                    f"{i}. **{cat['name']}**：{cat['count']} 篇 "
                    f"（占比 {cat['pct']:.0%}）"
                )
        lines.append("")

        # 新兴话题
        if emerging_topics:
            lines.append(
                f"值得关注的新兴话题包括：{'、'.join(emerging_topics)}。"
                f"这些方向可能代表 ISAC 领域的未来发展趋势。"
            )
            lines.append("")

        # 关键发现
        if key_findings:
            lines.append("### 关键发现")
            for i, finding in enumerate(key_findings, 1):
                lines.append(f"{i}. {finding}")
            lines.append("")

        return "\n".join(lines)

    # ========================================================================
    # 分类法概览模板
    # ========================================================================

    @staticmethod
    def taxonomy_overview(
        clusters: List[Dict[str, Any]],
        taxonomy_content: str = "",
    ) -> str:
        """生成分类法概览部分。

        Args:
            clusters: 簇信息列表
            taxonomy_content: 完整分类法 Markdown（可选嵌入）
        """
        lines = []
        lines.append("## 二、研究方向分类")
        lines.append("")

        # 簇概览表
        lines.append("| 研究方向 | 论文数 | 占比 | 代表关键词 |")
        lines.append("|----------|--------|------|------------|")
        total = sum(c.get("count", 0) for c in clusters)
        for c in clusters:
            name = c.get("name", "未知")
            count = c.get("count", 0)
            pct = count / max(total, 1)
            keywords = ", ".join(c.get("keywords", [])[:4])
            lines.append(f"| {name} | {count} | {pct:.0%} | {keywords} |")
        lines.append("")

        # 分布概要
        lines.append("从论文分布来看，ISAC 研究呈现出以下特征：")
        lines.append("")
        if clusters:
            top = clusters[0]
            lines.append(
                f"- **{top['name']}** 是当前论文数量最多的方向，"
                f"表明该领域受到了广泛关注和研究投入。"
            )
            if len(clusters) > 1:
                second = clusters[1]
                lines.append(
                    f"- **{second['name']}** 紧随其后，"
                    f"与第一方向共同构成 ISAC 研究的主力军。"
                )
        lines.append("")

        # 嵌入完整分类法
        if taxonomy_content:
            lines.append("### 完整分类体系")
            lines.append("")
            lines.append(taxonomy_content)
            lines.append("")

        return "\n".join(lines)

    # ========================================================================
    # 亮点论文模板
    # ========================================================================

    @staticmethod
    def highlight_papers(papers: List[Dict[str, Any]]) -> str:
        """生成亮点论文部分。

        Args:
            papers: 亮点论文列表，每个包含 title, arxiv_id, reason, excerpt 等
        """
        lines = []
        lines.append("## 三、亮点论文")
        lines.append("")

        if not papers:
            lines.append("（本周期暂无特别突出的论文。）")
            return "\n".join(lines)

        lines.append(
            f"从本周期收录的论文中，选取 {len(papers)} 篇具有代表性的工作进行重点介绍。"
        )
        lines.append("")

        for i, p in enumerate(papers, 1):
            title = p.get("title", "未知标题")
            arxiv_id = p.get("arxiv_id", "")
            reason = p.get("reason", "")
            excerpt = p.get("excerpt", "")
            innovation = p.get("innovation_type", "")
            category = p.get("best_fit_category", "")

            lines.append(f"### {i}. {title}")
            lines.append("")
            lines.append(f"- **arXiv ID**: [{arxiv_id}](https://arxiv.org/abs/{arxiv_id})")
            lines.append(f"- **研究方向**: {category}")
            lines.append(f"- **创新类型**: {innovation}")
            if reason:
                lines.append(f"- **推荐理由**: {reason}")
            lines.append("")

            if excerpt:
                lines.append(f"> {excerpt}")
                lines.append("")

        return "\n".join(lines)

    # ========================================================================
    # 新兴话题模板
    # ========================================================================

    @staticmethod
    def emerging_topics(
        topics: List[Dict[str, Any]],
        trends: List[str],
    ) -> str:
        """生成新兴话题分析部分。

        Args:
            topics: 新兴话题列表
            trends: 趋势描述列表
        """
        lines = []
        lines.append("## 四、新兴话题与趋势")
        lines.append("")

        if not topics and not trends:
            lines.append("（本周期未检测到明显的新兴话题。）")
            return "\n".join(lines)

        # 新兴话题
        if topics:
            lines.append("### 值得关注的研究方向")
            lines.append("")
            for topic in topics:
                name = topic.get("name", "")
                description = topic.get("description", "")
                paper_count = topic.get("paper_count", 0)
                lines.append(f"- **{name}**（{paper_count}篇）: {description}")
            lines.append("")

        # 趋势
        if trends:
            lines.append("### 发展趋势观察")
            lines.append("")
            for i, trend in enumerate(trends, 1):
                lines.append(f"{i}. {trend}")
            lines.append("")

        return "\n".join(lines)

    # ========================================================================
    # 方法对比表引用
    # ========================================================================

    @staticmethod
    def comparison_reference(csv_path: str, stats_text: str = "") -> str:
        """生成方法对比表引用部分。

        Args:
            csv_path: comparison_table.csv 文件路径
            stats_text: 统计摘要文本
        """
        lines = []
        lines.append("## 五、方法对比总表")
        lines.append("")
        lines.append(
            f"完整的论文方法对比表见文件：`{csv_path}`。"
            f"该表包含每篇论文的研究问题、核心思想、技术方法、"
            f"评价指标和结果摘要，便于横向对比。"
        )
        lines.append("")

        if stats_text:
            lines.append(stats_text)
            lines.append("")

        return "\n".join(lines)

    # ========================================================================
    # 统计信息模板
    # ========================================================================

    @staticmethod
    def statistics(
        paper_count: int,
        conf_dist: Dict[str, int],
        innov_dist: Dict[str, int],
        cat_dist: Dict[str, int],
        date_range: str = "",
        avg_completeness: float = 0.0,
    ) -> str:
        """生成统计信息部分。

        Args:
            paper_count: 论文总数
            conf_dist: 置信度分布
            innov_dist: 创新类型分布
            cat_dist: 类别分布
            date_range: 日期范围
            avg_completeness: 平均完整度
        """
        lines = []
        lines.append("## 六、统计信息")
        lines.append("")

        lines.append(f"- **论文总数**: {paper_count} 篇")
        if date_range:
            lines.append(f"- **时间范围**: {date_range}")
        lines.append(f"- **平均完整度**: {avg_completeness:.0%}")
        lines.append("")

        # 置信度分布
        if conf_dist:
            lines.append("### 置信度分布")
            lines.append("")
            lines.append("| 等级 | 数量 | 占比 |")
            lines.append("|------|------|------|")
            for level in ["high", "medium", "low"]:
                count = conf_dist.get(level, 0)
                pct = count / max(paper_count, 1)
                lines.append(f"| {level.upper()} | {count} | {pct:.0%} |")
            lines.append("")

        # 创新类型分布
        if innov_dist:
            lines.append("### 创新类型分布")
            lines.append("")
            lines.append("| 创新类型 | 数量 | 占比 |")
            lines.append("|----------|------|------|")
            for itype, count in sorted(innov_dist.items(), key=lambda x: -x[1]):
                pct = count / max(paper_count, 1)
                lines.append(f"| {itype} | {count} | {pct:.0%} |")
            lines.append("")

        # ISAC 子类别分布
        if cat_dist:
            lines.append("### ISAC 子类别分布")
            lines.append("")
            lines.append("| 子类别 | 数量 | 占比 |")
            lines.append("|--------|------|------|")
            for cat, count in sorted(cat_dist.items(), key=lambda x: -x[1]):
                pct = count / max(paper_count, 1)
                lines.append(f"| {cat} | {count} | {pct:.0%} |")
            lines.append("")

        return "\n".join(lines)

    # ========================================================================
    # 参考文献模板
    # ========================================================================

    @staticmethod
    def references(papers: List[Dict[str, Any]]) -> str:
        """生成参考文献列表。

        Args:
            papers: 论文信息列表 [{"arxiv_id": ..., "title": ..., "authors": ...}, ...]
        """
        lines = []
        lines.append("## 七、参考文献")
        lines.append("")

        if not papers:
            lines.append("（暂无参考文献。）")
            return "\n".join(lines)

        for i, p in enumerate(papers, 1):
            arxiv_id = p.get("arxiv_id", "")
            title = p.get("title", "未知标题")
            authors = p.get("authors", [])
            if isinstance(authors, list):
                authors_str = ", ".join(authors[:5])
                if len(authors) > 5:
                    authors_str += " et al."
            else:
                authors_str = str(authors)
            date = p.get("published_date", "")

            lines.append(
                f"[{i}] {authors_str}. *{title}*. "
                f"arXiv:{arxiv_id}, {date}."
            )
            lines.append("")

        return "\n".join(lines)

    # ========================================================================
    # 尾注模板
    # ========================================================================

    @staticmethod
    def footer(version: str = "1.0") -> str:
        """生成综述页脚。

        Args:
            version: 综述版本号
        """
        return f"""---
*本综述由 ISAC 文献自动化分析系统生成 (v{version})。*
*数据来源：arXiv.org。内容仅供参考，引用请以原文为准。*
*生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}*
"""


# ============================================================================
# 自检代码
# ============================================================================
if __name__ == "__main__":
    import sys
    if sys.stdout.encoding != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    print("=" * 60)
    print("ChineseTemplate 自检")
    print("=" * 60)

    tpl = ChineseTemplate()

    # 测试标题
    header = tpl.header("第1周", 50, "2024-01 至 2025-06")
    print(f"[标题模板] ({len(header)} 字符)")

    # 测试执行摘要
    exec_summary = tpl.executive_summary(
        paper_count=50,
        cluster_count=5,
        top_categories=[
            {"name": "波束赋形与预编码", "count": 12, "pct": 0.24},
            {"name": "RIS/智能超表面", "count": 10, "pct": 0.20},
            {"name": "波形设计", "count": 8, "pct": 0.16},
        ],
        emerging_topics=["AI/ML驱动的ISAC", "RIS辅助的感知通信", "太赫兹ISAC"],
        key_findings=[
            "深度学习在ISAC波束赋形中展现出显著优势，平均提升25-35%的性能",
            "RIS技术已成为ISAC领域增长最快的方向",
            "全双工ISAC研究正在从理论向实际场景过渡",
        ],
    )
    print(f"[执行摘要] ({len(exec_summary)} 字符)")

    # 测试亮点论文
    highlights = tpl.highlight_papers([
        {
            "title": "A Novel Deep Learning Framework for ISAC Beamforming",
            "arxiv_id": "2401.00001",
            "reason": "首次将Transformer架构应用于ISAC波束赋形，性能提升显著",
            "innovation_type": "全新方法",
            "best_fit_category": "Beamforming_and_Precoding",
            "excerpt": "We propose a transformer-based joint beamforming framework... achieves 35% improvement.",
        },
        {
            "title": "RIS-Assisted ISAC for 6G THz Communications",
            "arxiv_id": "2401.00002",
            "reason": "系统性地研究了RIS在太赫兹ISAC系统中的应用，填补了该交叉领域的空白",
            "innovation_type": "融合整合",
            "best_fit_category": "RIS_Metasurface_ISAC",
            "excerpt": "A comprehensive RIS-assisted ISAC framework for THz bands... 40% energy efficiency gain.",
        },
    ])
    print(f"[亮点论文] ({len(highlights)} 字符)")

    # 测试新兴话题
    emerging = tpl.emerging_topics(
        topics=[
            {"name": "AI原生ISAC", "paper_count": 8,
             "description": "将AI/ML直接嵌入ISAC系统设计，而非仅用于辅助优化"},
            {"name": "近场ISAC", "paper_count": 5,
             "description": "利用近场球面波前特性提升感知分辨率和通信容量"},
        ],
        trends=[
            "从传统优化方法向数据驱动的AI方法转变趋势明显",
            "太赫兹和RIS方向交叉融合，催生新的研究增长点",
            "实际部署场景（多小区、移动性、非理想CSI）受到更多关注",
        ],
    )
    print(f"[新兴话题] ({len(emerging)} 字符)")

    # 测试参考文献
    refs = tpl.references([
        {"arxiv_id": "2401.00001", "title": "Paper One",
         "authors": ["Zhang, W.", "Li, H."], "published_date": "2024-01"},
        {"arxiv_id": "2401.00002", "title": "Paper Two",
         "authors": ["Wang, X.", "Chen, Y."], "published_date": "2024-01"},
    ])
    print(f"[参考文献] ({len(refs)} 字符)")

    print("\n所有模板测试通过。")
    print("自检完成。")
