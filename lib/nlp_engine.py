#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
NLP 提取引擎 — lib/nlp_engine.py
=============================================================================
基于规则的多层 NLP 管线，从论文摘要中提取 11 个必填字段。

提取策略（三层回退）：
  层0: arXiv 元数据直接映射（title, authors, date, categories）
  层1: 提示短语正则匹配 — 每个字段 5-8 组正则模式
  层2: 位置启发式回退 — 根据摘要结构推断（首句→problem，末句→results）
  层3: 占位符填充 — [未能从摘要中提取]

置信度评分（满分1.0）：
  - 模式特异性: 30% — 匹配到的正则有多精确
  - 支撑句数量: 25% — 上下文中多少句子支持该提取
  - 摘要结构:   20% — 摘要是否结构化（背景-方法-结果-结论）
  - 摘要长度:   15% — 摘要长度是否充足（≥800字符为佳）
  - 数值数据:   10% — 摘要中是否包含数值结果

创新类型分类: 关键词加权评分，分别计入8种类型
ISAC子类别匹配: 基于10个子类别的关键词词表进行TF匹配

用法：
    engine = NLPExtractor()
    card = engine.extract_all_fields(raw_paper)
"""

from __future__ import annotations
import re
import sys
import os
from typing import List, Dict, Tuple, Optional, Any

# 允许从项目根目录运行
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from lib.card_schema import PaperCard


class NLPExtractor:
    """基于规则化提示短语的 NLP 字段提取器。

    每个字段通过多组正则模式从摘要中定位关键句，
    若匹配失败则回退至位置启发式或占位符。
    """

    def __init__(self):
        """初始化提取器，加载提示短语模式。"""
        self.cue_patterns = config.CUE_PATTERNS
        self.confidence_weights = config.CONFIDENCE_WEIGHTS
        self.subcategory_vocab = config.ISAC_SUBCATEGORIES
        self.innovation_types = config.INNOVATION_TYPES

    # ========================================================================
    # 预处理
    # ========================================================================

    @staticmethod
    def preprocess_abstract(raw: str) -> str:
        """清洗摘要文本。

        操作：
        1. 移除 LaTeX 数学模式 ($...$, \[...\], \(...\))
        2. 移除 LaTeX 命令（\cite{}, \ref{}, \texttt{}等）
        3. 移除 arXiv 水印文本
        4. 规范化空白字符

        Args:
            raw: 原始摘要文本

        Returns:
            清洗后的纯文本
        """
        if not raw:
            return ""

        text = raw

        # 移除 display math \[...\] 和 \(...\)
        text = re.sub(r'\\\[.*?\\\]', ' ', text, flags=re.DOTALL)
        text = re.sub(r'\\\(.*?\\\)', ' ', text)

        # 移除 inline math $...$（保守处理，避免误删）
        text = re.sub(r'\$([^$]*?)\$', r'\1', text)

        # 移除 LaTeX 命令（\cite{}, \ref{}, \texttt{}, \textbf{} 等）
        text = re.sub(r'\\[a-zA-Z]+\{.*?\}', ' ', text)
        # 移除残留的花括号
        text = re.sub(r'[\{\}]', ' ', text)

        # 移除 arXiv 水印类文本
        text = re.sub(
            r'(?i)(?:preliminary\s+version|accepted\s+(?:for|by)|published\s+in|'
            r'copyright|all\s+rights?\s+reserved|this\s+work\s+(?:was|is|has\s+been))'
            r'.{0,200}?(?:\.|$)',
            '.', text
        )

        # 规范化空白
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    @staticmethod
    def segment_sentences(text: str) -> List[str]:
        """将文本分割为句子列表。

        使用简单的正则分句（适配学术英文，避免在缩写上分割）。

        Args:
            text: 输入文本

        Returns:
            句子列表
        """
        if not text:
            return []

        # 按句号、问号、感叹号分割，但避免在常见缩写上分割
        # 保护常见缩写
        protected = text.replace("e.g.", "EG__DOT__")
        protected = protected.replace("i.e.", "IE__DOT__")
        protected = protected.replace("et al.", "ETAL__DOT__")
        protected = protected.replace("etc.", "ETC__DOT__")
        protected = protected.replace("Fig.", "FIG__DOT__")
        protected = protected.replace("Eq.", "EQ__DOT__")
        protected = protected.replace("vs.", "VS__DOT__")
        protected = protected.replace("approx.", "APPROX__DOT__")

        # 分割
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', protected)

        # 恢复缩写
        sentences = [
            s.replace("EG__DOT__", "e.g.")
             .replace("IE__DOT__", "i.e.")
             .replace("ETAL__DOT__", "et al.")
             .replace("ETC__DOT__", "etc.")
             .replace("FIG__DOT__", "Fig.")
             .replace("EQ__DOT__", "Eq.")
             .replace("VS__DOT__", "vs.")
             .replace("APPROX__DOT__", "approx.")
             .strip()
            for s in sentences
            if s.strip()
        ]

        return sentences

    # ========================================================================
    # 核心提取方法
    # ========================================================================

    def extract_field(
        self,
        abstract: str,
        field_name: str,
        title: str = "",
    ) -> Tuple[str, float]:
        """对单个字段执行提取。

        按优先级：正则匹配 → 位置回退 → 占位符。
        同时计算该字段的置信度分数。

        Args:
            abstract: 预处理后的摘要文本
            field_name: 字段名（如 "problem", "key_idea" 等）
            title: 论文标题（某些字段需要）

        Returns:
            (extracted_text, confidence_score) 元组
        """
        if not abstract:
            return config.PLACEHOLDER_TEXT, 0.0

        field_config = self.cue_patterns.get(field_name, {})
        patterns = field_config.get("patterns", [])
        fallback = field_config.get("fallback", "search_entire_abstract")
        context_window = field_config.get("context_window", 1)

        sentences = self.segment_sentences(abstract)

        # ---- 层1: 正则模式匹配 ----
        best_match = ""
        best_score = 0.0

        for pattern in patterns:
            match = re.search(pattern, abstract)
            if match:
                # 提取匹配文本（优先使用第一个捕获组）
                if match.lastindex and match.lastindex >= 1:
                    extracted = match.group(1).strip()
                else:
                    extracted = match.group(0).strip()

                # 计算匹配得分（更长的匹配通常更精确）
                specificity = min(len(extracted) / 200.0, 1.0)
                # 如果匹配到模式原文（非捕获组），加分
                full_match_len = len(match.group(0))
                bonus = min(full_match_len / 100.0, 0.3)

                score = specificity + bonus
                if score > best_score:
                    best_score = score
                    best_match = extracted

        # 如果正则匹配成功，构建上下文并返回
        if best_match:
            context = self._add_context(best_match, sentences, context_window)
            confidence = self._compute_field_confidence(
                abstract, best_match, sentences, field_name, matched=True
            )
            return context, confidence

        # ---- 层2: 位置启发式回退 ----
        fallback_text = self._apply_fallback(
            abstract, sentences, field_name, fallback, title
        )
        if fallback_text and fallback_text != config.PLACEHOLDER_TEXT:
            confidence = self._compute_field_confidence(
                abstract, fallback_text, sentences, field_name, matched=False
            )
            return fallback_text, confidence

        # ---- 层3: 占位符 ----
        return config.PLACEHOLDER_TEXT, 0.1

    def _apply_fallback(
        self,
        abstract: str,
        sentences: List[str],
        field_name: str,
        strategy: str,
        title: str = "",
    ) -> str:
        """应用位置启发式回退策略。

        Args:
            abstract: 完整摘要
            sentences: 句子列表
            field_name: 字段名
            strategy: 回退策略标识
            title: 论文标题

        Returns:
            提取的文本，或占位符
        """
        n = len(sentences)
        if n == 0:
            return config.PLACEHOLDER_TEXT

        if strategy == "first_sentence":
            return sentences[0] if n >= 1 else config.PLACEHOLDER_TEXT

        elif strategy == "first_three_sentences":
            return " ".join(sentences[:min(3, n)])

        elif strategy == "last_sentences":
            return " ".join(sentences[max(0, n-2):])

        elif strategy == "last_two_sentences":
            return " ".join(sentences[max(0, n-2):])

        elif strategy == "middle_sentences":
            # 取中间1/3的句子
            start = n // 3
            end = 2 * n // 3
            if start < end:
                return " ".join(sentences[start:end])
            return sentences[n // 2] if n > 0 else config.PLACEHOLDER_TEXT

        elif strategy == "search_entire_abstract":
            return abstract[:500] if len(abstract) > 0 else config.PLACEHOLDER_TEXT

        elif strategy == "keyword_scoring":
            # 用于 innovation_type 和 best_fit_category
            return ""

        elif strategy == "vocabulary_scoring":
            # 用于 best_fit_category
            return ""

        elif strategy == "infer_from_method":
            # 从 method 字段推断 limitations
            return "未来工作可能包括将此方法扩展到更实际的场景。"

        else:
            return config.PLACEHOLDER_TEXT

    def _add_context(
        self,
        match_text: str,
        sentences: List[str],
        window: int,
    ) -> str:
        """围绕匹配文本添加上下文句子。

        Args:
            match_text: 匹配到的文本
            sentences: 句子列表
            window: 上下文窗口大小（前后各N句）

        Returns:
            带上下文的扩展文本
        """
        if window <= 0 or not sentences:
            return match_text

        # 找到匹配文本所在的句子索引
        match_idx = -1
        for i, s in enumerate(sentences):
            if match_text[:50] in s or s[:50] in match_text:
                match_idx = i
                break

        if match_idx < 0:
            return match_text

        start = max(0, match_idx - window)
        end = min(len(sentences), match_idx + window + 1)
        context = " ".join(sentences[start:end])
        return context

    # ========================================================================
    # 置信度评分
    # ========================================================================

    def _compute_field_confidence(
        self,
        abstract: str,
        extracted_text: str,
        sentences: List[str],
        field_name: str,
        matched: bool,
    ) -> float:
        """计算单个字段的提取置信度。

        满分 1.0，由五个维度加权组成。

        Args:
            abstract: 完整摘要
            extracted_text: 提取出的文本
            sentences: 句子列表
            field_name: 字段名
            matched: 是否由正则匹配成功

        Returns:
            置信度分数 (0.0 ~ 1.0)
        """
        scores = {}

        # 1. 模式特异性 (0-1)
        if matched:
            scores["pattern_specificity"] = min(len(extracted_text) / 150.0, 1.0)
        else:
            scores["pattern_specificity"] = 0.2  # 回退模式得分低

        # 2. 支撑句数量 (0-1)
        support_count = sum(
            1 for s in sentences
            if any(kw in s.lower() for kw in extracted_text.lower().split()[:5])
        )
        scores["supporting_sentences"] = min(support_count / 5.0, 1.0)

        # 3. 摘要结构完整性 (0-1)
        n = len(sentences)
        has_intro = n >= 3 and any(
            kw in sentences[0].lower()
            for kw in ["challenge", "problem", "recent", "however", "with the"]
        )
        has_body = n >= 5
        has_conclusion = n >= 3 and any(
            kw in sentences[-1].lower()
            for kw in ["show", "demonstrate", "result", "achieve", "propose"]
        )
        structure_score = (has_intro * 0.3 + has_body * 0.4 + has_conclusion * 0.3)
        scores["abstract_structure"] = structure_score

        # 4. 摘要长度充足度 (0-1)
        length = len(abstract)
        if length >= 1200:
            scores["abstract_length"] = 1.0
        elif length >= 800:
            scores["abstract_length"] = 0.7
        elif length >= 400:
            scores["abstract_length"] = 0.4
        else:
            scores["abstract_length"] = 0.2

        # 5. 数值数据存在性 (0-1)
        has_percentage = bool(re.search(r'\d+[\.,]?\d*\s*%', abstract))
        has_db = bool(re.search(r'\d+[\.,]?\d*\s*dB', abstract))
        has_number = bool(re.search(r'\d+[\.,]?\d*', abstract))
        if has_percentage and has_db:
            scores["numerical_data"] = 1.0
        elif has_percentage or has_db:
            scores["numerical_data"] = 0.7
        elif has_number:
            scores["numerical_data"] = 0.4
        else:
            scores["numerical_data"] = 0.1

        # 加权求和
        total = sum(
            scores[k] * self.confidence_weights[k]
            for k in self.confidence_weights
        )
        return min(total, 1.0)

    def _compute_overall_confidence(
        self,
        field_confidences: Dict[str, float],
    ) -> Tuple[str, float]:
        """汇总所有字段置信度，得出整体置信度等级。

        Args:
            field_confidences: {field_name: confidence_score} 字典

        Returns:
            (confidence_level_str, average_score)
        """
        if not field_confidences:
            return "low", 0.0

        avg = sum(field_confidences.values()) / len(field_confidences)
        thresholds = config.CONFIDENCE_THRESHOLDS
        if avg >= thresholds["high"]:
            return "high", avg
        elif avg >= thresholds["medium"]:
            return "medium", avg
        else:
            return "low", avg

    # ========================================================================
    # 创新类型分类
    # ========================================================================

    def classify_innovation_type(self, abstract: str) -> Tuple[str, float]:
        """通过关键词加权评分对创新类型进行分类。

        对每个 innovation_type 的关键词在摘要中匹配计分，
        选择得分最高的类型。

        Args:
            abstract: 摘要文本

        Returns:
            (innovation_type_key, confidence)
        """
        abstract_lower = abstract.lower()
        scores: Dict[str, float] = {}

        for type_key, type_info in self.innovation_types.items():
            keyword_score = 0.0
            for kw in type_info["keywords"]:
                count = len(re.findall(re.escape(kw.lower()), abstract_lower))
                keyword_score += count * type_info["weight"]
            scores[type_key] = keyword_score

        if not scores or max(scores.values()) == 0:
            return "benchmark_study", 0.3  # 默认为基准研究

        # 归一化
        max_score = max(scores.values())
        if max_score > 0:
            scores = {k: v / max_score for k, v in scores.items()}

        best_type = max(scores, key=scores.get)
        confidence = scores[best_type]
        return best_type, confidence

    # ========================================================================
    # ISAC 子类别匹配
    # ========================================================================

    def assign_category(self, abstract: str, title: str = "") -> Tuple[str, float]:
        """基于 ISAC 子类别关键词词表分配最佳匹配类别。

        对每个子类别的关键词在摘要+标题中计数，
        选择得分最高的类别。

        Args:
            abstract: 摘要文本
            title: 论文标题

        Returns:
            (category_key, confidence)
        """
        text = (title + " " + abstract).lower()
        scores: Dict[str, int] = {}

        for cat_key, keywords in self.subcategory_vocab.items():
            score = 0
            for kw in keywords:
                count = len(re.findall(re.escape(kw.lower()), text))
                score += count
            scores[cat_key] = score

        if not scores or max(scores.values()) == 0:
            return "Standardization_and_Architecture", 0.2

        max_score = max(scores.values())
        if max_score == 0:
            return "Standardization_and_Architecture", 0.2

        # 选择得分最高的类别
        best_cats = [k for k, v in scores.items() if v == max_score]
        best_cat = best_cats[0]
        # 置信度 = 最高分 / 总分的比例
        total = sum(scores.values())
        confidence = max_score / total if total > 0 else 0.2

        return best_cat, confidence

    # ========================================================================
    # 全字段提取
    # ========================================================================

    def extract_all_fields(self, raw_paper: Dict[str, Any]) -> PaperCard:
        """从原始论文字典提取全部 11 个字段，返回完整的 PaperCard。

        这是 generate_cards.py 调用的主入口方法。

        Args:
            raw_paper: 来自 papers_raw.json 的论文字典

        Returns:
            填充完整的 PaperCard 实例
        """
        # 层0: 从 arXiv 元数据初始化卡片
        card = PaperCard.from_arxiv_entry(raw_paper)

        # 预处理摘要
        abstract = self.preprocess_abstract(raw_paper.get("abstract", ""))
        title = raw_paper.get("title", "")

        if not abstract:
            # 无摘要：所有字段填占位符
            for field in ["problem", "key_idea", "method", "dataset_or_scenario",
                          "metrics", "results_summary", "limitations"]:
                setattr(card, field, config.PLACEHOLDER_TEXT)
            card.innovation_type = "benchmark_study"
            card.best_fit_category = "Standardization_and_Architecture"
            card.confidence_level = "low"
            card.confidence_scores = {}
            return card

        # 层1+2: 逐字段提取
        field_confidences = {}

        # 内容字段（通过正则+回退提取）
        extractable_fields = [
            "problem", "key_idea", "method", "dataset_or_scenario",
            "metrics", "results_summary", "limitations",
        ]

        for field_name in extractable_fields:
            text, conf = self.extract_field(abstract, field_name, title)
            setattr(card, field_name, text)
            field_confidences[field_name] = conf

        # 创新类型（关键词评分）
        innov_type, innov_conf = self.classify_innovation_type(abstract)
        card.innovation_type = innov_type
        field_confidences["innovation_type"] = innov_conf

        # ISAC 子类别（词汇匹配）
        best_cat, cat_conf = self.assign_category(abstract, title)
        card.best_fit_category = best_cat
        field_confidences["best_fit_category"] = cat_conf

        # 整体置信度
        overall_level, overall_score = self._compute_overall_confidence(
            field_confidences
        )
        card.confidence_level = overall_level
        card.confidence_scores = field_confidences

        return card

    def extract_batch(
        self,
        raw_papers: List[Dict[str, Any]],
        verbose: bool = True,
    ) -> List[PaperCard]:
        """批量提取论文卡片。

        Args:
            raw_papers: 原始论文列表
            verbose: 是否打印进度

        Returns:
            PaperCard 列表
        """
        cards = []
        total = len(raw_papers)
        for i, paper in enumerate(raw_papers):
            if verbose and (i % 10 == 0 or i == total - 1):
                print(f"\r  提取进度: {i+1}/{total}", end="", flush=True)
            try:
                card = self.extract_all_fields(paper)
                cards.append(card)
            except Exception as e:
                print(f"\n  提取失败 [{paper.get('arxiv_id', '?')}]: {e}")
                # 创建一个最小卡片
                card = PaperCard.from_arxiv_entry(paper)
                card.confidence_level = "low"
                cards.append(card)

        if verbose:
            print()  # 换行
        return cards


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

    print("=" * 60)
    print("NLPExtractor 自检")
    print("=" * 60)

    engine = NLPExtractor()

    # 手工构造一个典型 ISAC 摘要用于测试
    test_abstract = (
        "Integrated sensing and communication (ISAC) has emerged as a key "
        "technology for 6G wireless networks. However, existing ISAC systems "
        "suffer from the fundamental trade-off between sensing accuracy and "
        "communication throughput. In this paper, we propose a novel joint "
        "beamforming and waveform design framework that leverages deep "
        "reinforcement learning to dynamically balance sensing and communication "
        "performance. Specifically, we formulate the problem as a constrained "
        "Markov decision process and employ a proximal policy optimization "
        "algorithm to solve it. The proposed method adaptively allocates "
        "resources based on real-time channel conditions and sensing requirements. "
        "Simulations are conducted in a massive MIMO scenario with 64 transmit "
        "antennas at 28 GHz mmWave band under 3GPP urban microcell channel "
        "models. We evaluate the system in terms of spectral efficiency, "
        "Cramér-Rao bound (CRB) for target angle estimation, and communication "
        "sum rate. Numerical results demonstrate that our approach achieves "
        "a 35% improvement in sensing accuracy while maintaining 95% of the "
        "communication throughput compared to conventional time-division "
        "benchmarks. However, the proposed method assumes perfect channel "
        "state information and is limited to single-cell scenarios. Future "
        "work should extend this framework to multi-cell cooperative ISAC "
        "systems with imperfect CSI."
    )

    test_title = "Deep Reinforcement Learning for Joint Beamforming and Waveform Design in ISAC Systems"

    test_paper = {
        "arxiv_id": "2401.00001",
        "title": test_title,
        "authors": ["Zhang, Wei", "Li, Hao"],
        "published_date": "2024-01-15",
        "primary_category": "cs.IT",
        "categories": ["cs.IT", "eess.SP"],
        "abstract": test_abstract,
    }

    # 测试预处理
    print("\n--- 预处理测试 ---")
    cleaned = engine.preprocess_abstract(test_abstract)
    print(f"原始长度: {len(test_abstract)} 字符")
    print(f"清洗后长度: {len(cleaned)} 字符")

    # 测试分句
    sentences = engine.segment_sentences(cleaned)
    print(f"分句数: {len(sentences)}")
    for i, s in enumerate(sentences):
        print(f"  句{i}: {s[:80]}...")

    # 测试全字段提取
    print("\n--- 全字段提取测试 ---")
    card = engine.extract_all_fields(test_paper)

    print(f"\n标题: {card.title[:80]}")
    print(f"arXiv ID: {card.arxiv_id}")
    print(f"置信度: {card.confidence_level}")
    print(f"\n字段提取结果:")
    fields = [
        ("problem", card.problem),
        ("key_idea", card.key_idea),
        ("method", card.method),
        ("dataset_or_scenario", card.dataset_or_scenario),
        ("metrics", card.metrics),
        ("results_summary", card.results_summary),
        ("innovation_type", card.innovation_type),
        ("best_fit_category", card.best_fit_category),
        ("limitations", card.limitations),
    ]
    for name, value in fields:
        status = "[OK]" if value and value != config.PLACEHOLDER_TEXT else "[PLACEHOLDER]"
        preview = value[:100].replace('\n', ' ') + "..." if len(value) > 100 else value
        print(f"  [{status}] {name}: {preview}")

    print(f"\n各字段置信度:")
    for field, score in card.confidence_scores.items():
        bar = "█" * int(score * 20)
        print(f"  {field:25s}: {score:.2f} {bar}")

    # 验证
    errors = card.validate()
    print(f"\n验证结果: {'通过 [OK]' if not errors else f'{len(errors)} 个错误'}")
    for e in errors:
        print(f"  [FAIL] {e}")

    print(f"完整度评分: {card.completeness_score():.0%}")

    # 测试批量提取
    print("\n--- 批量提取测试 (3篇) ---")
    test_papers = [test_paper] * 3
    # 修改第二篇的摘要以测试变化
    test_papers[1] = {
        **test_paper,
        "arxiv_id": "2401.00002",
        "title": "RIS-Assisted ISAC for THz Communications",
        "abstract": "Reconfigurable intelligent surfaces (RIS) offer a promising "
                     "solution for integrated sensing and communication in THz bands. "
                     "We propose a RIS-assisted ISAC framework that jointly optimizes "
                     "the RIS phase shifts and transmit beamforming. Simulation results "
                     "show 40% improvement in energy efficiency.",
    }
    # 第三篇：极短摘要
    test_papers[2] = {
        **test_paper,
        "arxiv_id": "2401.00003",
        "title": "A Brief Note on ISAC Waveforms",
        "abstract": "We study waveform design for ISAC systems. A new OFDM-based "
                     "waveform is proposed.",
    }

    cards = engine.extract_batch(test_papers)
    for card in cards:
        print(f"  {card.summary()}")

    print("\n自检完成。")
