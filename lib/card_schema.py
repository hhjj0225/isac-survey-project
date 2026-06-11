#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
论文卡片数据模型 — PaperCard 数据类与字段验证
=============================================================================
定义 11 个必填字段的 PaperCard 数据类，提供序列化、反序列化、
字段完整性验证和置信度验证功能。

所有字段内容必须来自论文摘要，严禁编造。
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import json
import sys
import os

# 允许从项目根目录运行
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


@dataclass
class PaperCard:
    """论文卡片 — 11 个必填内容字段 + 元数据字段。

    字段分为两组：
    1. 元数据字段（来自arXiv API直接映射）
    2. 内容字段（通过NLP从摘要中提取，共11个）
    """

    # ========== 元数据字段（arXiv API 直接提供） ==========
    arxiv_id: str = ""
    title: str = ""                     # 同时为11必填字段之一
    authors: List[str] = field(default_factory=list)
    published_date: str = ""            # ISO格式 YYYY-MM-DD
    primary_category: str = ""          # 主分类，如 cs.IT
    categories: List[str] = field(default_factory=list)  # 所有分类
    abstract_raw: str = ""              # 原始摘要文本

    # ========== 11 个必填内容字段 ==========
    # 1. title          — 论文标题（元数据字段，已包含）
    # 2. problem        — 研究问题/挑战
    problem: str = ""
    # 3. key_idea       — 核心思想/贡献
    key_idea: str = ""
    # 4. method         — 方法/技术路线
    method: str = ""
    # 5. dataset_or_scenario — 数据集/仿真场景
    dataset_or_scenario: str = ""
    # 6. metrics        — 评价指标
    metrics: str = ""
    # 7. results_summary — 结果摘要
    results_summary: str = ""
    # 8. innovation_type — 创新类型（枚举值）
    innovation_type: str = ""
    # 9. limitations    — 局限性/未来工作
    limitations: str = ""
    # 10. best_fit_category — 最佳匹配ISAC子类别
    best_fit_category: str = ""
    # 11. confidence_level — 提取置信度（high/medium/low）
    confidence_level: str = "low"

    # ========== 提取元数据 ==========
    extraction_timestamp: str = ""
    confidence_scores: Dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """初始化后处理：设置时间戳、确保列表字段类型正确。"""
        if not self.extraction_timestamp:
            self.extraction_timestamp = datetime.now(timezone.utc).isoformat()
        # 确保 authors 和 categories 是列表
        if isinstance(self.authors, str):
            self.authors = [a.strip() for a in self.authors.split(",") if a.strip()]
        if isinstance(self.categories, str):
            self.categories = [c.strip() for c in self.categories.split(",") if c.strip()]

    # ========================================================================
    # 核心验证方法
    # ========================================================================

    def validate(self) -> List[str]:
        """验证所有 11 个内容字段是否非空。

        Returns:
            错误消息列表；空列表表示验证通过（所有字段已填充）。
            title 由元数据保证，但也检查。
        """
        field_names = [
            "title", "problem", "key_idea", "method",
            "dataset_or_scenario", "metrics", "results_summary",
            "innovation_type", "limitations", "best_fit_category", "confidence_level"
        ]
        errors = []

        for field_name in field_names:
            value = getattr(self, field_name, None)
            if not value or value == config.PLACEHOLDER_TEXT:
                errors.append(f"字段 '{field_name}' 为空或为占位符文本")

        # 验证 innovation_type 是否在已知类型中
        if self.innovation_type and self.innovation_type not in config.INNOVATION_TYPES:
            if self.innovation_type != config.PLACEHOLDER_TEXT:
                errors.append(
                    f"innovation_type '{self.innovation_type}' 不在已知类型 "
                    f"{list(config.INNOVATION_TYPES.keys())} 中"
                )

        # 验证 confidence_level 是否有效
        valid_confidences = {"high", "medium", "low"}
        if self.confidence_level not in valid_confidences:
            errors.append(
                f"confidence_level '{self.confidence_level}' 无效，"
                f"应为 {valid_confidences} 之一"
            )

        return errors

    def is_valid(self) -> bool:
        """快捷方法：卡片是否通过验证。"""
        return len(self.validate()) == 0

    def completeness_score(self) -> float:
        """计算卡片完整度：非空/非占位符字段的比例。

        Returns:
            0.0 ~ 1.0，1.0 表示 11 个字段全部有效填充。
        """
        content_fields = [
            self.problem, self.key_idea, self.method,
            self.dataset_or_scenario, self.metrics, self.results_summary,
            self.innovation_type, self.limitations, self.best_fit_category,
            self.confidence_level
        ]
        valid_count = sum(
            1 for v in content_fields
            if v and v != config.PLACEHOLDER_TEXT
        )
        return valid_count / len(content_fields)

    # ========================================================================
    # 序列化 / 反序列化
    # ========================================================================

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（用于 JSON 序列化）。"""
        d = asdict(self)
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PaperCard":
        """从字典创建 PaperCard 实例。

        自动处理字段名映射和默认值。
        """
        # 提取 data 中存在的 PaperCard 字段
        field_names = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in field_names}
        return cls(**filtered)

    @classmethod
    def from_arxiv_entry(cls, entry: Dict[str, Any]) -> "PaperCard":
        """从 arXiv 原始条目创建 PaperCard（仅填充元数据）。

        这是 generate_cards.py 的输入基础——先用元数据初始化，
        后续由 NLPExtractor 填充内容字段。

        Args:
            entry: fetch_arxiv.py 输出的原始论文字典，包含:
                   arxiv_id, title, authors, published_date,
                   primary_category, categories, abstract

        Returns:
            PaperCard 实例，内容字段为空字符串。
        """
        return cls(
            arxiv_id=entry.get("arxiv_id", ""),
            title=entry.get("title", ""),
            authors=entry.get("authors", []),
            published_date=entry.get("published_date", ""),
            primary_category=entry.get("primary_category", ""),
            categories=entry.get("categories", []),
            abstract_raw=entry.get("abstract", ""),
            # 以下内容字段留空，待 NLPExtractor 填充
            problem="",
            key_idea="",
            method="",
            dataset_or_scenario="",
            metrics="",
            results_summary="",
            innovation_type="",
            limitations="",
            best_fit_category="",
            confidence_level="low",
            extraction_timestamp=datetime.now(timezone.utc).isoformat(),
            confidence_scores={},
        )

    def to_jsonl_line(self) -> str:
        """转换为 JSONL 格式的单行字符串。"""
        return json.dumps(self.to_dict(), ensure_ascii=False) + "\n"

    @classmethod
    def from_jsonl_line(cls, line: str) -> "PaperCard":
        """从 JSONL 行字符串解析 PaperCard。"""
        return cls.from_dict(json.loads(line.strip()))

    # ========================================================================
    # 显示与调试
    # ========================================================================

    def summary(self) -> str:
        """生成单行摘要（中文）。"""
        title_short = self.title[:60] + "..." if len(self.title) > 60 else self.title
        cat_zh = config.INNOVATION_TYPES.get(
            self.innovation_type,
            {"label_zh": self.innovation_type or "未知"}
        ).get("label_zh", self.innovation_type) if isinstance(
            config.INNOVATION_TYPES.get(self.innovation_type, {}), dict
        ) else self.innovation_type

        return (
            f"[{self.confidence_level.upper():>4}] "
            f"{title_short} "
            f"| 类别: {self.best_fit_category or '未分类'} "
            f"| 创新: {cat_zh} "
            f"| 完整度: {self.completeness_score():.0%}"
        )

    def __repr__(self) -> str:
        return f"PaperCard(arxiv_id={self.arxiv_id!r}, title={self.title[:50]!r}...)"


# ============================================================================
# 辅助函数
# ============================================================================

def load_cards_from_jsonl(filepath: str) -> List[PaperCard]:
    """从 JSONL 文件加载所有论文卡片。

    Args:
        filepath: paper_cards.jsonl 文件路径

    Returns:
        PaperCard 列表，跳过解析失败的行
    """
    cards = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    card = PaperCard.from_jsonl_line(line)
                    cards.append(card)
                except (json.JSONDecodeError, TypeError) as e:
                    print(f"警告: 第 {line_no} 行解析失败: {e}", file=sys.stderr)
    except FileNotFoundError:
        print(f"错误: 文件未找到 {filepath}", file=sys.stderr)
        raise
    return cards


def save_cards_to_jsonl(cards: List[PaperCard], filepath: str) -> None:
    """将论文卡片列表写入 JSONL 文件。

    Args:
        cards: PaperCard 列表
        filepath: 输出文件路径
    """
    with open(filepath, "w", encoding="utf-8") as f:
        for card in cards:
            f.write(card.to_jsonl_line())
    print(f"已写入 {len(cards)} 条论文卡片至 {filepath}")


def load_papers_raw(filepath: str) -> List[Dict[str, Any]]:
    """从 JSON 文件加载原始论文数据。

    Args:
        filepath: papers_raw.json 文件路径

    Returns:
        原始论文字典列表
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_papers_raw(papers: List[Dict[str, Any]], filepath: str) -> None:
    """保存原始论文数据至 JSON 文件。

    Args:
        papers: 论文字典列表
        filepath: 输出文件路径
    """
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(papers, f, ensure_ascii=False, indent=2)
    print(f"已保存 {len(papers)} 篇原始论文至 {filepath}")


# ============================================================================
# 自检代码
# ============================================================================
if __name__ == "__main__":
    # 设置 stdout 为 UTF-8 编码（兼容 Windows GBK 终端）
    if sys.stdout.encoding != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    # 快速冒烟测试
    print("=" * 60)
    print("PaperCard 模型自检")
    print("=" * 60)

    # 测试 1：创建空卡片
    card = PaperCard()
    errors = card.validate()
    print(f"空卡片验证: {'通过' if not errors else f'发现 {len(errors)} 个缺失字段'}")
    for e in errors:
        print(f"  - {e}")

    # 测试 2：从 arXiv 条目创建
    sample_entry = {
        "arxiv_id": "2401.00001",
        "title": "A Novel ISAC Framework for 6G MIMO Systems",
        "authors": ["Zhang, Wei", "Li, Hao"],
        "published_date": "2024-01-15",
        "primary_category": "cs.IT",
        "categories": ["cs.IT", "eess.SP"],
        "abstract": "We propose a novel integrated sensing and communication "
                    "framework for 6G massive MIMO systems. The framework "
                    "jointly optimizes beamforming and waveform design to "
                    "achieve high sensing accuracy while maintaining "
                    "communication throughput. Simulation results demonstrate "
                    "a 25% improvement over baseline methods.",
    }
    card2 = PaperCard.from_arxiv_entry(sample_entry)
    print(f"\n从arXiv条目创建: {card2}")
    print(f"元数据已填充: title='{card2.title[:50]}...'")
    print(f"内容字段为空: problem='{card2.problem}'")

    # 测试 3：序列化往返
    card2.problem = "ISAC systems face trade-off between sensing and communication"
    card2.key_idea = "Joint beamforming optimization"
    card2.method = "Alternating optimization + MMSE beamforming"
    card2.dataset_or_scenario = "Massive MIMO with 64 antennas, urban microcell"
    card2.metrics = "Spectral efficiency, CRB, SINR"
    card2.results_summary = "25% improvement over TDD-based baseline"
    card2.innovation_type = "novel_approach"
    card2.limitations = "Assumes perfect CSI, limited to single-cell"
    card2.best_fit_category = "Beamforming_and_Precoding"
    card2.confidence_level = "high"

    # 验证
    errors = card2.validate()
    print(f"\n完整卡片验证: {'通过 [OK]' if not errors else f'{len(errors)} 个错误'}")
    print(f"完整度评分: {card2.completeness_score():.0%}")

    # JSONL 往返
    line = card2.to_jsonl_line()
    restored = PaperCard.from_jsonl_line(line)
    print(f"JSONL往返: {'通过 [OK]' if restored.title == card2.title else '失败 [FAIL]'}")

    # 测试 4：批量加载
    print(f"\n摘要预览: {card2.summary()}")

    print("\n自检完成。")
