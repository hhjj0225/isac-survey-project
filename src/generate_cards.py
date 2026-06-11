#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
阶段2: 论文卡片生成器 — generate_cards.py
=============================================================================
读取 papers_raw.json，调用 NLPExtractor 对每篇论文执行 11 字段提取，
验证卡片完整性，输出 paper_cards.jsonl。

用法：
    python src/generate_cards.py                          # 默认输入/输出路径
    python src/generate_cards.py --input data/papers_raw.json
    python src/generate_cards.py --output data/paper_cards.jsonl
    python src/generate_cards.py --stats                  # 仅打印统计
"""

from __future__ import annotations
import argparse
import json
import sys
import os
import time
from datetime import datetime, timezone
from typing import List, Dict, Any

# 确保从项目根目录导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from lib.card_schema import (
    PaperCard, load_papers_raw, save_cards_to_jsonl, load_cards_from_jsonl
)
from lib.nlp_engine import NLPExtractor


# ============================================================================
# 主生成函数
# ============================================================================

def generate_cards(
    input_path: str = None,
    output_path: str = None,
    verbose: bool = True,
) -> List[PaperCard]:
    """执行完整的论文卡片生成流程。

    Args:
        input_path: 原始论文 JSON 文件路径
        output_path: 输出 JSONL 文件路径
        verbose: 是否打印详细信息

    Returns:
        PaperCard 列表
    """
    if input_path is None:
        input_path = str(config.PAPERS_RAW_PATH)
    if output_path is None:
        output_path = str(config.PAPER_CARDS_PATH)

    # 加载原始论文
    if verbose:
        print(f"[阶段 2a] 加载原始论文: {input_path}")
    papers = load_papers_raw(input_path)
    if verbose:
        print(f"  加载了 {len(papers)} 篇论文")

    if not papers:
        print("错误: 无有效论文数据", file=sys.stderr)
        return []

    # 初始化 NLP 提取引擎
    if verbose:
        print(f"[阶段 2b] 初始化 NLP 提取引擎...")
    engine = NLPExtractor()

    # 逐篇提取
    if verbose:
        print(f"[阶段 2c] 提取论文卡片字段...")
    start_time = time.monotonic()
    cards = engine.extract_batch(papers, verbose=verbose)
    elapsed = time.monotonic() - start_time
    if verbose:
        print(f"  提取完成: {len(cards)} 张卡片 (用时 {elapsed:.1f} 秒, "
              f"平均 {elapsed/max(len(cards),1):.2f} 秒/篇)")

    # 验证卡片
    if verbose:
        print(f"[阶段 2d] 验证卡片完整性...")
    valid_cards = []
    invalid_cards = []
    for card in cards:
        errors = card.validate()
        if errors:
            invalid_cards.append((card, errors))
        else:
            valid_cards.append(card)

    if verbose:
        print(f"  有效卡片: {len(valid_cards)}")
        print(f"  存在问题: {len(invalid_cards)}")
        if invalid_cards:
            print(f"  问题详情 (前5条):")
            for card, errors in invalid_cards[:5]:
                print(f"    [{card.arxiv_id}] {card.title[:60]}...")
                for e in errors:
                    print(f"      - {e}")

    # 保存
    if verbose:
        print(f"[阶段 2e] 保存卡片至: {output_path}")
    save_cards_to_jsonl(cards, output_path)  # 保存全部（含不完整卡片，供人工审核）

    # 统计报告
    if verbose:
        print_statistics(cards)

    return cards


# ============================================================================
# 统计函数
# ============================================================================

def print_statistics(cards: List[PaperCard]) -> None:
    """打印卡片统计信息。

    Args:
        cards: PaperCard 列表
    """
    total = len(cards)
    if total == 0:
        print("无卡片数据。")
        return

    print(f"\n{'='*60}")
    print(f"论文卡片统计报告")
    print(f"{'='*60}")

    # 置信度分布
    conf_dist = {"high": 0, "medium": 0, "low": 0}
    for c in cards:
        conf_dist[c.confidence_level] = conf_dist.get(c.confidence_level, 0) + 1
    print(f"\n置信度分布:")
    for level in ["high", "medium", "low"]:
        count = conf_dist.get(level, 0)
        bar = "#" * (count * 40 // max(total, 1))
        print(f"  {level.upper():6s}: {count:3d} ({count/total*100:5.1f}%) {bar}")

    # 创新类型分布
    innov_dist = {}
    for c in cards:
        t = c.innovation_type or "unknown"
        innov_dist[t] = innov_dist.get(t, 0) + 1
    print(f"\n创新类型分布:")
    for t, count in sorted(innov_dist.items(), key=lambda x: -x[1]):
        label = config.INNOVATION_TYPES.get(t, {}).get("label_zh", t)
        print(f"  {label:12s} ({t}): {count:3d} ({count/total*100:5.1f}%)")

    # ISAC 子类别分布
    cat_dist = {}
    for c in cards:
        cat = c.best_fit_category or "未分类"
        cat_dist[cat] = cat_dist.get(cat, 0) + 1
    print(f"\nISAC 子类别分布:")
    for cat, count in sorted(cat_dist.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count:3d} ({count/total*100:5.1f}%)")

    # 完整度分布
    completeness_bins = {"100%": 0, "80-99%": 0, "50-79%": 0, "<50%": 0}
    for c in cards:
        score = c.completeness_score()
        if score >= 1.0:
            completeness_bins["100%"] += 1
        elif score >= 0.8:
            completeness_bins["80-99%"] += 1
        elif score >= 0.5:
            completeness_bins["50-79%"] += 1
        else:
            completeness_bins["<50%"] += 1
    print(f"\n完整度分布:")
    for bin_name, count in completeness_bins.items():
        print(f"  {bin_name:8s}: {count:3d} ({count/total*100:5.1f}%)")

    # 平均完整度
    avg_completeness = sum(c.completeness_score() for c in cards) / total
    print(f"\n平均完整度: {avg_completeness:.1%}")

    print(f"{'='*60}")


# ============================================================================
# 命令行入口
# ============================================================================

def main():
    """命令行入口函数。"""
    parser = argparse.ArgumentParser(
        description="论文卡片生成器 — 从原始论文提取结构化卡片",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python src/generate_cards.py                      # 默认路径
    python src/generate_cards.py --input custom.json  # 自定义输入
    python src/generate_cards.py --stats              # 统计已有卡片
        """,
    )
    parser.add_argument(
        "--input", type=str, default=None,
        help=f"输入 JSON 文件 (默认: {config.PAPERS_RAW_PATH})"
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help=f"输出 JSONL 文件 (默认: {config.PAPER_CARDS_PATH})"
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="静默模式（减少输出）"
    )
    parser.add_argument(
        "--stats", action="store_true",
        help="仅打印已有卡片文件的统计信息"
    )

    args = parser.parse_args()

    # 仅打印统计
    if args.stats:
        cards_path = args.output or str(config.PAPER_CARDS_PATH)
        if os.path.exists(cards_path):
            cards = load_cards_from_jsonl(cards_path)
            print_statistics(cards)
        else:
            print(f"文件不存在: {cards_path}")
        return

    # 执行生成
    try:
        cards = generate_cards(
            input_path=args.input,
            output_path=args.output,
            verbose=not args.quiet,
        )
    except FileNotFoundError as e:
        print(f"错误: 文件未找到 - {e}", file=sys.stderr)
        print("提示: 请先运行 fetch_arxiv.py 获取原始论文数据", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

    if cards:
        print(f"\n完成! 共生成 {len(cards)} 张论文卡片。")


if __name__ == "__main__":
    main()
