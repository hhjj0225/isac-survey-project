#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
阶段1: arXiv 论文抓取器 — fetch_arxiv.py
=============================================================================
功能：
1. 使用主查询 + 回退查询从 arXiv 抓取 ISAC 领域论文
2. 自动去重（按 arXiv ID）
3. 按期日过滤（保留近 N 个月）
4. 断点续传支持（--resume 参数）
5. 输出 papers_raw.json

用法：
    python src/fetch_arxiv.py                          # 完整抓取
    python src/fetch_arxiv.py --max 200                # 指定抓取上限
    python src/fetch_arxiv.py --resume                 # 从断点续传
    python src/fetch_arxiv.py --no-filter              # 不过滤日期/分类
    python src/fetch_arxiv.py --test                   # 测试模式(5篇)
"""

from __future__ import annotations
import argparse
import json
import sys
import os
import time
from datetime import datetime, timezone
from pathlib import Path

# 确保从项目根目录导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from lib.arxiv_client import ArxivClient
from lib.card_schema import save_papers_raw, load_papers_raw


# ============================================================================
# 主抓取函数
# ============================================================================

def fetch_isac_papers(
    max_total: int = None,
    resume: bool = False,
    apply_filters: bool = True,
    test_mode: bool = False,
) -> list:
    """执行完整的 ISAC 论文抓取流程。

    Args:
        max_total: 最大论文总数
        resume: 是否从断点续传
        apply_filters: 是否应用日期/分类过滤
        test_mode: 测试模式（只抓取少量论文）

    Returns:
        论文列表（dict）
    """
    if max_total is None:
        max_total = config.ARXIV_MAX_TOTAL_RESULTS

    client = ArxivClient()

    # 准备查询列表
    if test_mode:
        queries = [config.ARXIV_PRIMARY_QUERY]
        max_per = 10
        max_total = min(max_total, 10)
        print("[测试模式] 仅使用主查询，上限10篇")
    else:
        queries = [config.ARXIV_PRIMARY_QUERY] + config.ARXIV_FALLBACK_QUERIES
        max_per = max(50, max_total // len(queries))

    print("=" * 60)
    print("ISAC 论文自动抓取器")
    print(f"目标总数: ≤{max_total} 篇")
    print(f"主查询 + {len(config.ARXIV_FALLBACK_QUERIES)} 个回退查询")
    print(f"断点续传: {'启用' if resume else '禁用'}")
    print(f"日期/分类过滤: {'启用' if apply_filters else '禁用'}")
    print(f"开始时间: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    start_time = time.monotonic()

    # ---- 阶段 1a: 抓取论文 ----
    if resume and config.FETCH_CHECKPOINT_PATH.exists():
        print("\n[阶段 1a] 从断点续传...")
        # 使用主查询 + 断点续传
        papers = client.fetch_with_resume(
            query=config.ARXIV_PRIMARY_QUERY,
            max_results=max_total,
            checkpoint_path=str(config.FETCH_CHECKPOINT_PATH),
        )
        # 如果断点恢复后还不足，运行回退查询
        if len(papers) < max_total:
            remaining = max_total - len(papers)
            print(f"\n断点论文不足 ({len(papers)}/{max_total})，"
                  f"运行回退查询补充...")
            existing_ids = {p["arxiv_id"] for p in papers}
            fallback_queries = config.ARXIV_FALLBACK_QUERIES
            query_max = max(10, remaining // len(fallback_queries))
            for i, q in enumerate(fallback_queries):
                if len(papers) >= max_total:
                    break
                try:
                    for paper in client.search(q, max_results=query_max):
                        aid = paper.get("arxiv_id", "")
                        if aid and aid not in existing_ids:
                            existing_ids.add(aid)
                            papers.append(paper)
                except Exception as e:
                    print(f"  回退查询出错: {e}")
    else:
        print("\n[阶段 1a] 多查询合并抓取...")
        papers = client.fetch_all_with_queries(
            queries=queries,
            max_per_query=max_per,
        )

    elapsed = time.monotonic() - start_time
    print(f"\n抓取完成: {len(papers)} 篇论文 (用时 {elapsed:.1f} 秒)")

    # ---- 阶段 1b: 多层质量过滤 ----
    if apply_filters:
        print(f"\n[阶段 1b] 多层质量过滤...")
        total_before = len(papers)

        # 1. 日期过滤（近2年）
        before = len(papers)
        papers = ArxivClient.filter_by_date(papers)
        print(f"  [1/5] 日期过滤 (近{config.LOOKBACK_MONTHS}个月): "
              f"{before} → {len(papers)} 篇")

        # 2. 分类过滤（仅保留 ISAC 相关分类）
        before = len(papers)
        papers = ArxivClient.filter_by_categories(papers)
        print(f"  [2/5] 分类过滤 ({len(config.TARGET_CATEGORIES)}个目标分类): "
              f"{before} → {len(papers)} 篇")

        # 3. 摘要质量过滤（移除空摘要和过短摘要）
        before = len(papers)
        papers = ArxivClient.filter_by_abstract_quality(papers)
        print(f"  [3/5] 摘要质量过滤 (≥{config.MIN_ABSTRACT_LENGTH}字符): "
              f"{before} → {len(papers)} 篇")

        # 4. ISAC 相关性过滤（关键词命中检查）
        before = len(papers)
        papers = ArxivClient.filter_by_isac_relevance(papers)
        print(f"  [4/5] ISAC相关性过滤 (≥{config.MIN_ISAC_KEYWORD_HITS}个核心关键词): "
              f"{before} → {len(papers)} 篇")

        # 5. 标题去重（Jaccard相似度）
        before = len(papers)
        papers = ArxivClient.filter_duplicates_by_title(papers)
        print(f"  [5/5] 标题去重: "
              f"{before} → {len(papers)} 篇")

        total_removed = total_before - len(papers)
        print(f"\n  过滤汇总: {total_before} → {len(papers)} 篇 "
              f"(移除 {total_removed} 篇, 保留率 {len(papers)/max(total_before,1)*100:.1f}%)")

    # ---- 阶段 1c: 验证 ----
    print(f"\n{'='*60}")
    if len(papers) < config.ARXIV_MIN_REQUIRED_PAPERS:
        print(f"[WARN] 警告: 仅获取到 {len(papers)} 篇有效论文，"
              f"低于最低要求 {config.ARXIV_MIN_REQUIRED_PAPERS} 篇")
        if len(papers) < 5:
            print("[FAIL] 错误: 有效论文数不足5篇，流水线终止")
            sys.exit(1)
    else:
        print(f"[OK] 论文数量满足要求: {len(papers)} >= {config.ARXIV_MIN_REQUIRED_PAPERS}")

    # 详细统计信息
    print(f"\n--- 有效论文统计 ---")
    print(f"  论文总数: {len(papers)}")

    # 分类分布
    cats = {}
    for p in papers:
        cat = p.get("primary_category", "unknown")
        cats[cat] = cats.get(cat, 0) + 1
    print(f"  主分类分布:")
    for cat, cnt in sorted(cats.items(), key=lambda x: -x[1]):
        bar = "#" * max(1, cnt * 30 // max(len(papers), 1))
        print(f"    {cat:12s}: {cnt:3d} 篇 {bar}")

    # 日期分布
    dates = [p.get("published_date", "") for p in papers if p.get("published_date")]
    if dates:
        from collections import Counter
        year_months = Counter(d[:7] for d in dates if len(d) >= 7)
        print(f"  时间分布 (最近月份):")
        for ym, cnt in sorted(year_months.items(), reverse=True)[:12]:
            print(f"    {ym}: {cnt} 篇")

    # 摘要长度统计
    abstract_lens = [len(p.get("abstract", "")) for p in papers]
    if abstract_lens:
        avg_len = sum(abstract_lens) / len(abstract_lens)
        print(f"  摘要长度: 最短={min(abstract_lens)}, "
              f"最长={max(abstract_lens)}, 平均={avg_len:.0f} 字符")

    return papers


# ============================================================================
# 命令行入口
# ============================================================================

def main():
    """命令行入口函数。"""
    parser = argparse.ArgumentParser(
        description="ISAC 论文自动抓取器 — 从 arXiv 获取 6G ISAC 领域论文",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python src/fetch_arxiv.py                    # 完整抓取
    python src/fetch_arxiv.py --max 200          # 指定上限
    python src/fetch_arxiv.py --resume           # 断点续传
    python src/fetch_arxiv.py --no-filter        # 跳过过滤
    python src/fetch_arxiv.py --test             # 测试模式
        """,
    )
    parser.add_argument(
        "--max", type=int, default=None,
        help=f"最大论文总数 (默认: {config.ARXIV_MAX_TOTAL_RESULTS})"
    )
    parser.add_argument(
        "--resume", action="store_true",
        help="从断点文件续传"
    )
    parser.add_argument(
        "--no-filter", action="store_true",
        help="不应用日期/分类过滤"
    )
    parser.add_argument(
        "--test", action="store_true",
        help="测试模式: 仅抓取少量论文"
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help=f"输出JSON文件路径 (默认: {config.PAPERS_RAW_PATH})"
    )
    parser.add_argument(
        "--print-stats", action="store_true",
        help="仅打印已有文件的统计信息"
    )

    args = parser.parse_args()

    # 仅打印统计
    if args.print_stats:
        output_path = args.output or str(config.PAPERS_RAW_PATH)
        if os.path.exists(output_path):
            papers = load_papers_raw(output_path)
            print(f"文件: {output_path}")
            print(f"论文数: {len(papers)}")
            if papers:
                print(f"日期范围: {papers[-1].get('published_date', '?')} ~ "
                      f"{papers[0].get('published_date', '?')}")
                cats = {}
                for p in papers:
                    c = p.get("primary_category", "?")
                    cats[c] = cats.get(c, 0) + 1
                print("分类分布:")
                for c, n in sorted(cats.items(), key=lambda x: -x[1]):
                    print(f"  {c}: {n}")
        else:
            print(f"文件不存在: {output_path}")
        return

    # 执行抓取
    try:
        papers = fetch_isac_papers(
            max_total=args.max,
            resume=args.resume,
            apply_filters=not args.no_filter,
            test_mode=args.test,
        )
    except KeyboardInterrupt:
        print("\n\n用户中断。如启用了断点续传，下次可使用 --resume 继续。")
        sys.exit(0)
    except Exception as e:
        print(f"\n抓取出错: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # 保存结果
    output_path = args.output or str(config.PAPERS_RAW_PATH)
    save_papers_raw(papers, output_path)

    print(f"\n{'='*60}")
    print(f"[OK] 抓取完成！")
    print(f"  输出文件: {output_path}")
    print(f"  论文总数: {len(papers)}")
    print(f"  完成时间: {datetime.now(timezone.utc).isoformat()}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
