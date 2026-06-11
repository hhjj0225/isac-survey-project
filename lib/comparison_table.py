#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
对比表生成器 — lib/comparison_table.py
=============================================================================
从论文卡片列表生成方法对比 CSV 表格。

输出字段（UTF-8 BOM 编码，兼容 Excel）：
title, arxiv_id, problem, key_idea, method, dataset_or_scenario,
metrics, results_summary, innovation_type, limitations,
best_fit_category, confidence_level, published_date, primary_category
"""

from __future__ import annotations
import csv
import sys
import os
from typing import List, Optional

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from lib.card_schema import PaperCard


class ComparisonTable:
    """论文方法对比表生成器。"""

    # CSV 列定义：字段名 → 中文列标题
    COLUMNS = {
        "arxiv_id": "arXiv ID",
        "title": "论文标题",
        "problem": "研究问题",
        "key_idea": "核心思想",
        "method": "方法/技术路线",
        "dataset_or_scenario": "数据集/仿真场景",
        "metrics": "评价指标",
        "results_summary": "结果摘要",
        "innovation_type": "创新类型",
        "limitations": "局限性",
        "best_fit_category": "ISAC子类别",
        "confidence_level": "置信度",
        "published_date": "发表日期",
        "primary_category": "主分类",
    }

    @staticmethod
    def cards_to_dataframe(cards: List[PaperCard]) -> pd.DataFrame:
        """将论文卡片列表转换为 pandas DataFrame。

        对超长文本进行截断以保持表格可读性。

        Args:
            cards: PaperCard 列表

        Returns:
            pandas DataFrame
        """
        rows = []
        for card in cards:
            # 将 innovation_type 转换为中文标签
            innovation_label = ""
            if card.innovation_type in config.INNOVATION_TYPES:
                innovation_label = config.INNOVATION_TYPES[card.innovation_type].get(
                    "label_zh", card.innovation_type
                )
            else:
                innovation_label = card.innovation_type

            row = {
                "arxiv_id": card.arxiv_id,
                "title": card.title,
                "problem": ComparisonTable._truncate(card.problem, 200),
                "key_idea": ComparisonTable._truncate(card.key_idea, 250),
                "method": ComparisonTable._truncate(card.method, 250),
                "dataset_or_scenario": ComparisonTable._truncate(
                    card.dataset_or_scenario, 150
                ),
                "metrics": ComparisonTable._truncate(card.metrics, 200),
                "results_summary": ComparisonTable._truncate(card.results_summary, 200),
                "innovation_type": innovation_label,
                "limitations": ComparisonTable._truncate(card.limitations, 200),
                "best_fit_category": card.best_fit_category,
                "confidence_level": card.confidence_level.upper(),
                "published_date": card.published_date,
                "primary_category": card.primary_category,
            }
            rows.append(row)

        df = pd.DataFrame(rows)
        return df

    @staticmethod
    def _truncate(text: str, max_len: int = 200) -> str:
        """截断超长文本，添加省略号。

        Args:
            text: 原始文本
            max_len: 最大字符数

        Returns:
            截断后的文本
        """
        if not text or text == config.PLACEHOLDER_TEXT:
            return text or ""
        if len(text) <= max_len:
            return text
        return text[:max_len-3].rsplit(" ", 1)[0] + "..."

    @staticmethod
    def save_csv(
        df: pd.DataFrame,
        output_path: str,
        include_bom: bool = True,
    ) -> None:
        """保存 DataFrame 为 CSV 文件（UTF-8 BOM，兼容 Excel）。

        Args:
            df: pandas DataFrame
            output_path: 输出文件路径
            include_bom: 是否包含 UTF-8 BOM（Excel 需要）
        """
        # 重命名列为中文标题
        df_out = df.rename(columns=ComparisonTable.COLUMNS)

        # 写入 CSV
        with open(output_path, "w", encoding="utf-8-sig" if include_bom else "utf-8",
                  newline="") as f:
            df_out.to_csv(f, index=False, quoting=csv.QUOTE_NONNUMERIC)

        print(f"对比表已保存至: {output_path} ({len(df)} 行)")

    @staticmethod
    def load_csv(filepath: str) -> pd.DataFrame:
        """加载对比表 CSV 文件。

        Args:
            filepath: CSV 文件路径

        Returns:
            pandas DataFrame
        """
        return pd.read_csv(filepath, encoding="utf-8-sig")

    @staticmethod
    def generate_summary_stats(df: pd.DataFrame) -> str:
        """生成对比表的摘要统计信息。

        Args:
            df: 论文对比表 DataFrame

        Returns:
            统计描述文本
        """
        lines = []
        lines.append("## 对比表统计")
        lines.append("")
        lines.append(f"- 总论文数: {len(df)}")
        lines.append("")

        if "best_fit_category" in df.columns:
            lines.append("### ISAC 子类别分布")
            cat_counts = df["best_fit_category"].value_counts()
            for cat, cnt in cat_counts.items():
                lines.append(f"- {cat}: {cnt} 篇")
            lines.append("")

        if "confidence_level" in df.columns:
            lines.append("### 置信度分布")
            conf_counts = df["confidence_level"].value_counts()
            for level, cnt in conf_counts.items():
                lines.append(f"- {level}: {cnt} 篇")
            lines.append("")

        if "published_date" in df.columns:
            dates = pd.to_datetime(df["published_date"], errors="coerce")
            if dates.notna().any():
                lines.append("### 时间范围")
                lines.append(f"- 最早: {dates.min().strftime('%Y-%m-%d')}")
                lines.append(f"- 最晚: {dates.max().strftime('%Y-%m-%d')}")
                lines.append("")

        return "\n".join(lines)


# ============================================================================
# 自检代码
# ============================================================================
if __name__ == "__main__":
    if sys.stdout.encoding != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    print("=" * 60)
    print("ComparisonTable 自检")
    print("=" * 60)

    # 构造测试数据
    from lib.card_schema import PaperCard

    cards = []
    for i in range(5):
        card = PaperCard(
            arxiv_id=f"2401.{i+1:05d}",
            title=f"ISAC Research Paper {i+1}: A Novel Approach",
            authors=["Author"],
            abstract_raw="Test abstract with important findings about ISAC systems.",
            published_date="2024-01-15",
            primary_category="cs.IT",
            categories=["cs.IT", "eess.SP"],
            problem=f"Problem statement {i+1}",
            key_idea=f"Key innovative idea {i+1} for solving the problem",
            method=f"Proposed method {i+1} using advanced techniques",
            dataset_or_scenario="Massive MIMO simulation with 64 antennas",
            metrics="Spectral efficiency, CRB, SINR",
            results_summary=f"Achieves {20+i*5}% improvement over baseline",
            innovation_type="novel_approach",
            limitations="Assumes perfect CSI",
            best_fit_category="Beamforming_and_Precoding",
            confidence_level="high",
        )
        cards.append(card)

    ct = ComparisonTable()
    df = ct.cards_to_dataframe(cards)
    print(f"\nDataFrame: {df.shape[0]} 行 x {df.shape[1]} 列")
    print(f"列名: {list(df.columns)}")

    # 测试 CSV 保存
    test_path = os.path.join(os.path.dirname(__file__), "..", "data", "_test_comparison.csv")
    ct.save_csv(df, test_path)

    # 测试统计
    stats = ct.generate_summary_stats(df)
    print(f"\n{stats}")

    # 清理测试文件
    if os.path.exists(test_path):
        os.remove(test_path)
        print("测试文件已清理。")

    print("自检完成。")
