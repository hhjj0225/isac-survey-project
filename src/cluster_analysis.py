#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
阶段3: 聚类分析与分类法生成 — cluster_analysis.py
=============================================================================
读取 paper_cards.jsonl，执行 TF-IDF + SVD + 层次聚类，
输出 taxonomy.md 和 comparison_table.csv。

用法：
    python src/cluster_analysis.py                      # 默认路径
    python src/cluster_analysis.py --input data/paper_cards.jsonl
    python src/cluster_analysis.py --clusters 6         # 指定簇数
"""

from __future__ import annotations
import argparse
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from lib.card_schema import load_cards_from_jsonl
from lib.taxonomy_builder import TaxonomyBuilder
from lib.comparison_table import ComparisonTable


# ============================================================================
# 主函数
# ============================================================================

def run_cluster_analysis(
    cards_path: str = None,
    taxonomy_path: str = None,
    comparison_path: str = None,
    n_clusters: int = None,
    verbose: bool = True,
) -> dict:
    """执行完整的聚类分析流水线。

    Args:
        cards_path: 论文卡片 JSONL 文件路径
        taxonomy_path: 分类法输出路径
        comparison_path: 对比表输出路径
        n_clusters: 指定簇数（None 则自动选择）
        verbose: 是否打印详细信息

    Returns:
        聚类结果字典（来自 TaxonomyBuilder.fit()）
    """
    if cards_path is None:
        cards_path = str(config.PAPER_CARDS_PATH)
    if taxonomy_path is None:
        taxonomy_path = str(config.TAXONOMY_PATH)
    if comparison_path is None:
        comparison_path = str(config.COMPARISON_TABLE_PATH)

    # 加载论文卡片
    if verbose:
        print(f"[阶段 3a] 加载论文卡片: {cards_path}")
    cards = load_cards_from_jsonl(cards_path)
    if verbose:
        print(f"  加载了 {len(cards)} 张论文卡片")

    if len(cards) < 3:
        print("错误: 需要至少 3 篇论文才能聚类", file=sys.stderr)
        sys.exit(1)

    # 聚类
    if verbose:
        print(f"[阶段 3b] 执行层次聚类...")
        if n_clusters:
            print(f"  指定簇数: {n_clusters}")
        else:
            print(f"  自动选择最优簇数 (范围 {config.CLUSTER_K_MIN}-"
                  f"{min(max(config.CLUSTER_K_MIN + 1, int(config.CLUSTER_K_MAX_RATIO * len(cards))), len(cards)-1, 10)})")

    start_time = time.monotonic()
    builder = TaxonomyBuilder()
    cluster_result = builder.fit(cards, n_clusters=n_clusters)
    elapsed = time.monotonic() - start_time

    if verbose:
        print(f"  聚类完成 (用时 {elapsed:.1f} 秒)")
        print(f"  最优簇数: {cluster_result['n_clusters']}")
        print(f"  轮廓系数: {cluster_result['silhouette']:.4f}")
        print(f"\n  各簇关键词:")
        for k, terms in cluster_result["top_terms_per_cluster"].items():
            cluster_size = sum(1 for l in cluster_result["labels"] if l == k)
            print(f"    簇 {k} ({cluster_size}篇): {', '.join(terms[:5])}")

    # 生成分类法
    if verbose:
        print(f"\n[阶段 3c] 生成分类法文档...")
    taxonomy_md = builder.generate_taxonomy(cards, cluster_result)

    with open(taxonomy_path, "w", encoding="utf-8") as f:
        f.write(taxonomy_md)
    if verbose:
        print(f"  分类法已保存至: {taxonomy_path}")

    # 生成对比表
    if verbose:
        print(f"\n[阶段 3d] 生成方法对比表...")
    ct = ComparisonTable()
    df = ct.cards_to_dataframe(cards)
    ct.save_csv(df, comparison_path)
    if verbose:
        print(f"  对比表已保存至: {comparison_path}")
        print(f"  对比表统计:\n{ct.generate_summary_stats(df)}")

    return cluster_result


# ============================================================================
# 命令行入口
# ============================================================================

def main():
    """命令行入口函数。"""
    parser = argparse.ArgumentParser(
        description="ISAC 聚类分析器 — 层次聚类 + 分类法 + 方法对比表",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python src/cluster_analysis.py                       # 默认路径
    python src/cluster_analysis.py --clusters 6          # 指定6簇
    python src/cluster_analysis.py --output-dir custom/  # 自定义输出目录
        """,
    )
    parser.add_argument(
        "--input", type=str, default=None,
        help=f"输入 JSONL 文件 (默认: {config.PAPER_CARDS_PATH})"
    )
    parser.add_argument(
        "--taxonomy", type=str, default=None,
        help=f"分类法输出路径 (默认: {config.TAXONOMY_PATH})"
    )
    parser.add_argument(
        "--comparison", type=str, default=None,
        help=f"对比表输出路径 (默认: {config.COMPARISON_TABLE_PATH})"
    )
    parser.add_argument(
        "--clusters", type=int, default=None,
        help="指定聚类簇数（默认自动选择）"
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="静默模式"
    )

    args = parser.parse_args()

    try:
        result = run_cluster_analysis(
            cards_path=args.input,
            taxonomy_path=args.taxonomy,
            comparison_path=args.comparison,
            n_clusters=args.clusters,
            verbose=not args.quiet,
        )
    except FileNotFoundError as e:
        print(f"错误: 文件未找到 - {e}", file=sys.stderr)
        print("提示: 请先运行 fetch_arxiv.py 和 generate_cards.py", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print(f"\n完成! "
          f"聚类簇数={result['n_clusters']}, "
          f"轮廓系数={result['silhouette']:.4f}")


if __name__ == "__main__":
    main()
