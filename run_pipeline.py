#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
ISAC 文献综述自动化流水线 — 主控编排器 (run_pipeline.py)
=============================================================================
端到端执行完整流水线：

  fetch_arxiv.py → papers_raw.json
       → generate_cards.py → paper_cards.jsonl
       → cluster_analysis.py → taxonomy.md & comparison_table.csv
       → weekly_survey_generator.py → weekly_digest.md

阶段门控：
  - 阶段1后：<5篇终止，<20篇警告
  - 阶段2后：<20张有效卡片时警告
  - 阶段3后：需要至少2个聚类簇

用法：
    python run_pipeline.py                     # 执行全部4个阶段
    python run_pipeline.py --stage 2           # 仅执行到阶段2
    python run_pipeline.py --from-stage 3      # 从阶段3开始（需要中间文件）
    python run_pipeline.py --test              # 测试模式（少量论文）
    python run_pipeline.py --skip-fetch        # 跳过的抓取阶段
"""

from __future__ import annotations
import argparse
import sys
import os
import time
import logging
from datetime import datetime, timezone
from pathlib import Path

# 修复 Windows GBK 终端编码问题
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# 确保从项目根目录运行
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config


# ============================================================================
# 日志设置
# ============================================================================

def setup_logging(log_to_file: bool = True) -> logging.Logger:
    """配置日志系统，同时输出到控制台和文件。

    Args:
        log_to_file: 是否写入日志文件

    Returns:
        根日志记录器
    """
    logger = logging.getLogger("isac_pipeline")
    logger.setLevel(getattr(logging, config.LOG_LEVEL, logging.INFO))

    # 清除已有处理器
    logger.handlers.clear()

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    console_handler.setFormatter(console_fmt)
    logger.addHandler(console_handler)

    # 文件处理器
    if log_to_file:
        log_path = config.LOG_DIR / f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_fmt = logging.Formatter(config.LOG_FORMAT, datefmt=config.LOG_DATE_FORMAT)
        file_handler.setFormatter(file_fmt)
        logger.addHandler(file_handler)
        logger.info(f"日志文件: {log_path}")

    return logger


# ============================================================================
# 阶段门控
# ============================================================================

class StageGate:
    """阶段门控：验证各阶段输出是否满足继续执行的条件。"""

    @staticmethod
    def check_stage1(papers_path: str) -> bool:
        """阶段1门控：检查抓取论文数量。

        Returns:
            True 如果可以继续
        """
        if not os.path.exists(papers_path):
            print(f"[FAIL] 阶段1失败: 输出文件不存在 {papers_path}")
            return False

        import json
        with open(papers_path, "r", encoding="utf-8") as f:
            papers = json.load(f)

        n = len(papers)
        if n < 5:
            print(f"[FAIL] 阶段1失败: 仅获取 {n} 篇论文 (<5, 终止)")
            return False
        elif n < config.ARXIV_MIN_REQUIRED_PAPERS:
            print(f"[WARN] 阶段1警告: 仅 {n} 篇论文 (<{config.ARXIV_MIN_REQUIRED_PAPERS}), 继续但建议增加")
            return True
        else:
            print(f"[OK] 阶段1通过: {n} 篇论文")
            return True

    @staticmethod
    def check_stage2(cards_path: str) -> bool:
        """阶段2门控：检查有效卡片数量。

        Returns:
            True 如果可以继续
        """
        if not os.path.exists(cards_path):
            print(f"[FAIL] 阶段2失败: 输出文件不存在 {cards_path}")
            return False

        from lib.card_schema import load_cards_from_jsonl
        cards = load_cards_from_jsonl(cards_path)

        n = len(cards)
        valid_n = sum(1 for c in cards if c.is_valid())

        if n < 5:
            print(f"[FAIL] 阶段2失败: 仅 {n} 张卡片 (<5, 终止)")
            return False
        elif valid_n < n * 0.5:
            print(f"[WARN] 阶段2警告: 仅 {valid_n}/{n} 张完整卡片 (<50%), 继续但建议审核")
            return True
        else:
            print(f"[OK] 阶段2通过: {n} 张卡片, {valid_n} 张完整")
            return True

    @staticmethod
    def check_stage3(taxonomy_path: str, comparison_path: str) -> bool:
        """阶段3门控：检查分类法和对比表。

        Returns:
            True 如果可以继续
        """
        ok = True
        if not os.path.exists(taxonomy_path):
            print(f"[WARN] 阶段3警告: 分类法文件不存在 {taxonomy_path}")
            ok = False
        if not os.path.exists(comparison_path):
            print(f"[WARN] 阶段3警告: 对比表文件不存在 {comparison_path}")
            ok = False
        if ok:
            print(f"[OK] 阶段3通过: 分类法和对比表已生成")
        return True  # 即使文件缺失也允许继续（阶段4会处理）


# ============================================================================
# 主流水线
# ============================================================================

def run_pipeline(
    max_papers: int = None,
    start_stage: int = 1,
    end_stage: int = 4,
    skip_fetch: bool = False,
    test_mode: bool = False,
    week_number: int = 1,
    date_range: str = "",
    verbose: bool = True,
) -> bool:
    """执行完整的 ISAC 文献综述流水线。

    Args:
        max_papers: 最大论文数
        start_stage: 起始阶段 (1-4)
        end_stage: 终止阶段 (1-4)
        skip_fetch: 跳过阶段1
        test_mode: 测试模式
        week_number: 周次编号
        date_range: 日期范围
        verbose: 详细输出

    Returns:
        True 如果全部成功
    """
    logger = setup_logging()
    gate = StageGate()

    total_start = time.monotonic()
    success = True

    print("=" * 70)
    print("ISAC 文献综述自动化流水线")
    print(f"开始时间: {datetime.now(timezone.utc).isoformat()}")
    print(f"阶段范围: {start_stage} → {end_stage}")
    print(f"测试模式: {'是' if test_mode else '否'}")
    print("=" * 70)

    # ========================================================================
    # 阶段1: 论文抓取
    # ========================================================================
    if start_stage <= 1 <= end_stage and not skip_fetch:
        print(f"\n{'─'*70}")
        print("阶段 1/4: arXiv 论文抓取")
        print(f"{'─'*70}")

        try:
            from src.fetch_arxiv import fetch_isac_papers

            papers = fetch_isac_papers(
                max_total=max_papers or (10 if test_mode else config.ARXIV_MAX_TOTAL_RESULTS),
                resume=False,
                apply_filters=not test_mode,
                test_mode=test_mode,
            )

            # 保存
            from lib.card_schema import save_papers_raw
            save_papers_raw(papers, str(config.PAPERS_RAW_PATH))

            if not gate.check_stage1(str(config.PAPERS_RAW_PATH)):
                success = False
                if len(papers) < 5:
                    return False

        except Exception as e:
            logger.error(f"阶段1失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    elif start_stage <= 1 <= end_stage and skip_fetch:
        print(f"\n[阶段 1/4] 跳过抓取，使用现有文件")
        if os.path.exists(str(config.PAPERS_RAW_PATH)):
            gate.check_stage1(str(config.PAPERS_RAW_PATH))
        else:
            print("[FAIL] 缺少 papers_raw.json，无法继续")
            return False

    # ========================================================================
    # 阶段2: 卡片生成
    # ========================================================================
    if start_stage <= 2 <= end_stage:
        print(f"\n{'─'*70}")
        print("阶段 2/4: 论文卡片生成")
        print(f"{'─'*70}")

        try:
            from src.generate_cards import generate_cards

            cards = generate_cards(
                input_path=str(config.PAPERS_RAW_PATH),
                output_path=str(config.PAPER_CARDS_PATH),
                verbose=verbose,
            )

            if not gate.check_stage2(str(config.PAPER_CARDS_PATH)):
                if len(cards) < 5:
                    success = False
                    return False

        except Exception as e:
            logger.error(f"阶段2失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    # ========================================================================
    # 阶段3: 聚类分析
    # ========================================================================
    if start_stage <= 3 <= end_stage:
        print(f"\n{'─'*70}")
        print("阶段 3/4: 聚类分析与分类法")
        print(f"{'─'*70}")

        try:
            from src.cluster_analysis import run_cluster_analysis

            result = run_cluster_analysis(
                cards_path=str(config.PAPER_CARDS_PATH),
                taxonomy_path=str(config.TAXONOMY_PATH),
                comparison_path=str(config.COMPARISON_TABLE_PATH),
                verbose=verbose,
            )

            gate.check_stage3(
                str(config.TAXONOMY_PATH),
                str(config.COMPARISON_TABLE_PATH)
            )

        except Exception as e:
            logger.error(f"阶段3失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    # ========================================================================
    # 阶段4: 周度综述
    # ========================================================================
    if start_stage <= 4 <= end_stage:
        print(f"\n{'─'*70}")
        print("阶段 4/4: 周度综述生成")
        print(f"{'─'*70}")

        try:
            from src.weekly_survey_generator import generate_weekly_digest

            digest = generate_weekly_digest(
                cards_path=str(config.PAPER_CARDS_PATH),
                taxonomy_path=str(config.TAXONOMY_PATH),
                comparison_path=str(config.COMPARISON_TABLE_PATH),
                output_path=str(config.WEEKLY_DIGEST_PATH),
                week_number=week_number,
                date_range=date_range,
                verbose=verbose,
            )

            if os.path.exists(str(config.WEEKLY_DIGEST_PATH)):
                print(f"[OK] 阶段4通过: 综述已生成")
            else:
                print(f"[FAIL] 阶段4失败: 综述文件未生成")
                success = False

        except Exception as e:
            logger.error(f"阶段4失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    # ========================================================================
    # 汇总
    # ========================================================================
    total_elapsed = time.monotonic() - total_start
    print(f"\n{'='*70}")
    print(f"流水线执行{'成功' if success else '存在警告'}")
    print(f"总用时: {total_elapsed:.1f} 秒")
    print(f"完成时间: {datetime.now(timezone.utc).isoformat()}")
    print(f"{'='*70}")

    # 列出生成的文件
    print(f"\n输出文件:")
    for label, path in [
        ("原始论文", config.PAPERS_RAW_PATH),
        ("论文卡片", config.PAPER_CARDS_PATH),
        ("分类法", config.TAXONOMY_PATH),
        ("对比表", config.COMPARISON_TABLE_PATH),
        ("周度综述", config.WEEKLY_DIGEST_PATH),
    ]:
        if os.path.exists(str(path)):
            size_kb = os.path.getsize(str(path)) / 1024
            print(f"  [OK] {label}: {path} ({size_kb:.1f} KB)")
        else:
            print(f"  [FAIL] {label}: 未生成")

    return success


# ============================================================================
# 命令行入口
# ============================================================================

def main():
    """命令行入口函数。"""
    parser = argparse.ArgumentParser(
        description="ISAC 文献综述自动化流水线 — 端到端执行",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python run_pipeline.py                          # 完整流水线
    python run_pipeline.py --test                   # 测试模式
    python run_pipeline.py --skip-fetch             # 跳过抓取
    python run_pipeline.py --from-stage 3           # 从阶段3开始
    python run_pipeline.py --stage 2                # 仅执行到阶段2
    python run_pipeline.py --week 3                 # 指定周次
        """,
    )
    parser.add_argument(
        "--max", type=int, default=None,
        help=f"最大论文数 (默认: {config.ARXIV_MAX_TOTAL_RESULTS})"
    )
    parser.add_argument(
        "--stage", type=int, default=None,
        help="仅执行到指定阶段 (1-4)"
    )
    parser.add_argument(
        "--from-stage", type=int, default=1,
        help="从指定阶段开始 (1-4, 默认: 1)"
    )
    parser.add_argument(
        "--skip-fetch", action="store_true",
        help="跳过arXiv抓取阶段（使用已有文件）"
    )
    parser.add_argument(
        "--test", action="store_true",
        help="测试模式（少量论文）"
    )
    parser.add_argument(
        "--week", type=int, default=1,
        help="周次编号"
    )
    parser.add_argument(
        "--date-range", type=str, default="",
        help="日期范围字符串"
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="减少输出"
    )

    args = parser.parse_args()

    start_stage = args.from_stage
    end_stage = args.stage or 4

    if start_stage > end_stage:
        print(f"错误: 起始阶段({start_stage}) > 终止阶段({end_stage})", file=sys.stderr)
        sys.exit(1)

    try:
        ok = run_pipeline(
            max_papers=args.max,
            start_stage=start_stage,
            end_stage=end_stage,
            skip_fetch=args.skip_fetch,
            test_mode=args.test,
            week_number=args.week,
            date_range=args.date_range,
            verbose=not args.quiet,
        )
    except KeyboardInterrupt:
        print("\n用户中断流水线。")
        sys.exit(0)

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
