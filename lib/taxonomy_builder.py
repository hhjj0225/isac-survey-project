#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
分类法构建器 — lib/taxonomy_builder.py
=============================================================================
基于 TF-IDF + TruncatedSVD (LSA) + 层次聚类的论文分类法构建模块。

管线：
1. 文档向量化：TF-IDF (ngram 1-3, max_features=500)
2. 降维：TruncatedSVD
3. 聚类：Agglomerative Hierarchical Clustering (Ward linkage)
4. 最优簇数：轮廓系数扫描
5. 簇标签：ISAC 关键词词表匹配
6. 输出：taxonomy.md 格式字符串 + 聚类结果字典

用法：
    builder = TaxonomyBuilder()
    result = builder.fit(cards)
    taxonomy_md = builder.generate_taxonomy(cards, result["labels"])
"""

from __future__ import annotations
import re
import sys
import os
import warnings
from typing import List, Dict, Tuple, Optional, Any

import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import normalize
import nltk

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from lib.card_schema import PaperCard

# 抑制 sklearn 的 FutureWarning
warnings.filterwarnings("ignore", category=FutureWarning)


class TaxonomyBuilder:
    """基于层次聚类的论文分类法构建器。"""

    def __init__(
        self,
        max_features: int = None,
        ngram_range: Tuple[int, int] = None,
        max_df: float = None,
        min_df: int = None,
    ):
        """初始化分类法构建器。

        Args:
            max_features: TF-IDF 最大特征数
            ngram_range: n-gram 范围
            max_df: 最大文档频率
            min_df: 最小文档频率
        """
        self.max_features = max_features or config.TFIDF_MAX_FEATURES
        self.ngram_range = ngram_range or config.TFIDF_NGRAM_RANGE
        self.max_df = max_df or config.TFIDF_MAX_DF
        self.min_df = min_df or config.TFIDF_MIN_DF

        self.vectorizer: Optional[TfidfVectorizer] = None
        self.svd: Optional[TruncatedSVD] = None
        self.feature_names: List[str] = []
        self.X_reduced: Optional[np.ndarray] = None

        # 初始化 NLTK 数据
        self._init_nltk()

    @staticmethod
    def _init_nltk() -> None:
        """初始化 NLTK 所需数据包。"""
        for pkg in config.NLTK_PACKAGES:
            try:
                nltk.data.find(f"tokenizers/{pkg}" if pkg == "punkt" else
                               f"tokenizers/{pkg}" if pkg == "punkt_tab" else
                               f"corpora/{pkg}")
            except LookupError:
                try:
                    nltk.download(pkg, quiet=True)
                except Exception:
                    pass

    # ========================================================================
    # 预处理
    # ========================================================================

    @staticmethod
    def _build_document(card: PaperCard) -> str:
        """将论文卡片合并为单个文档字符串用于向量化。

        组合：title + abstract + key_idea（重复 title 以增加权重）

        Args:
            card: 论文卡片

        Returns:
            文档字符串
        """
        parts = [
            card.title,
            card.title,  # 标题重复一次以增加权重
            card.abstract_raw or "",
            card.key_idea or "",
            card.problem or "",
        ]
        doc = " ".join(p for p in parts if p and p != config.PLACEHOLDER_TEXT)
        return doc

    @staticmethod
    def _preprocess_text(text: str) -> str:
        """预处理文本：小写化、移除特殊字符。

        Args:
            text: 输入文本

        Returns:
            预处理后的文本
        """
        text = text.lower()
        # 移除 LaTeX
        text = re.sub(r'\$[^$]*\$', ' ', text)
        text = re.sub(r'\\[a-zA-Z]+\{.*?\}', ' ', text)
        # 移除数字（保留有意义的数字）
        # 移除标点
        text = re.sub(r'[^\w\s]', ' ', text)
        # 规范化空白
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _prepare_documents(self, cards: List[PaperCard]) -> List[str]:
        """为所有卡片准备文档。

        Args:
            cards: 论文卡片列表

        Returns:
            预处理后的文档字符串列表
        """
        docs = []
        for card in cards:
            doc = self._build_document(card)
            doc = self._preprocess_text(doc)
            docs.append(doc)
        return docs

    # ========================================================================
    # 向量化与聚类
    # ========================================================================

    def fit(
        self,
        cards: List[PaperCard],
        n_clusters: Optional[int] = None,
    ) -> Dict[str, Any]:
        """执行完整的聚类管线。

        Args:
            cards: 论文卡片列表
            n_clusters: 指定簇数（None 则自动选择最优）

        Returns:
            聚类结果字典，包含:
            - labels: 每个论文的簇标签 (1-based)
            - n_clusters: 实际簇数
            - silhouette: 轮廓系数
            - feature_names: TF-IDF 特征词列表
            - X_reduced: 降维后的向量矩阵
            - top_terms_per_cluster: 每簇的 top 关键词
        """
        n = len(cards)
        if n < 3:
            return {
                "labels": np.ones(n, dtype=int),
                "n_clusters": 1,
                "silhouette": 0.0,
                "feature_names": [],
                "X_reduced": np.zeros((n, 1)),
                "top_terms_per_cluster": {1: ["insufficient_data"]},
            }

        # 1. 准备文档
        docs = self._prepare_documents(cards)

        # 2. TF-IDF 向量化
        self.vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            max_df=self.max_df,
            min_df=self.min_df,
            ngram_range=self.ngram_range,
            stop_words="english",
            sublinear_tf=True,
        )
        try:
            X_tfidf = self.vectorizer.fit_transform(docs)
        except ValueError:
            # 词汇量太少，回退到更宽松的参数
            self.vectorizer = TfidfVectorizer(
                max_features=self.max_features,
                max_df=1.0,
                min_df=1,
                ngram_range=(1, 2),
                stop_words="english",
                sublinear_tf=True,
            )
            X_tfidf = self.vectorizer.fit_transform(docs)

        self.feature_names = self.vectorizer.get_feature_names_out().tolist()

        # 3. 降维 (TruncatedSVD / LSA)
        n_components = max(
            2,
            min(
                int(config.SVD_N_COMPONENTS_RATIO * n),
                X_tfidf.shape[1] - 1,
                50
            )
        )
        self.svd = TruncatedSVD(n_components=n_components, random_state=42)
        X_reduced = self.svd.fit_transform(X_tfidf)
        X_reduced = normalize(X_reduced, norm="l2")
        self.X_reduced = X_reduced

        # 4. 聚类 — 层次聚类 Ward 方法
        if n < 3:
            labels = np.ones(n, dtype=int)
            best_k = 1
            best_silhouette = 0.0
        else:
            # 计算距离矩阵用于层次聚类
            dist_matrix = pdist(X_reduced, metric="euclidean")
            Z = linkage(dist_matrix, method="ward")

            # 最优 k 选择（轮廓系数扫描）
            k_min = config.CLUSTER_K_MIN
            k_max = max(k_min + 1, min(int(config.CLUSTER_K_MAX_RATIO * n), n - 1, 10))
            best_k = k_min
            best_silhouette = -1.0

            if n_clusters is not None:
                best_k = n_clusters
            else:
                for k in range(k_min, k_max + 1):
                    try:
                        labels_k = fcluster(Z, k, criterion="maxclust")
                        labels_k_0based = labels_k - 1  # silhouette_score 需要 0-based
                        if len(set(labels_k_0based)) < 2:
                            continue
                        sil = silhouette_score(X_reduced, labels_k_0based)
                        if sil > best_silhouette:
                            best_silhouette = sil
                            best_k = k
                    except Exception:
                        continue

            # 使用最优 k 进行聚类
            labels = fcluster(Z, best_k, criterion="maxclust")

        # 5. 提取每簇的 top 关键词
        top_terms = self._extract_top_terms_per_cluster(
            X_tfidf, labels, best_k
        )

        return {
            "labels": labels,
            "n_clusters": best_k,
            "silhouette": best_silhouette,
            "feature_names": self.feature_names,
            "X_reduced": X_reduced,
            "top_terms_per_cluster": top_terms,
        }

    def _extract_top_terms_per_cluster(
        self,
        X_tfidf,
        labels: np.ndarray,
        n_clusters: int,
        top_n: int = 10,
    ) -> Dict[int, List[str]]:
        """提取每个簇的 top TF-IDF 关键词。

        Args:
            X_tfidf: TF-IDF 稀疏矩阵
            labels: 簇标签 (1-based)
            n_clusters: 簇数
            top_n: 每个簇返回的关键词数

        Returns:
            {cluster_id: [term1, term2, ...]}
        """
        top_terms = {}
        for k in range(1, n_clusters + 1):
            mask = labels == k
            if mask.sum() == 0:
                top_terms[k] = ["empty_cluster"]
                continue

            # 计算该簇的平均 TF-IDF
            cluster_tfidf = X_tfidf[mask].mean(axis=0)
            cluster_tfidf = np.asarray(cluster_tfidf).flatten()

            # 获取 top N 索引
            top_indices = np.argsort(cluster_tfidf)[::-1][:top_n]
            terms = [self.feature_names[i] for i in top_indices
                     if i < len(self.feature_names)]
            top_terms[k] = terms if terms else ["no_terms"]

        return top_terms

    # ========================================================================
    # 簇标签生成（与 ISAC 子类别词表匹配）
    # ========================================================================

    def _label_cluster(
        self,
        top_terms: List[str],
        cards_in_cluster: List[PaperCard],
    ) -> str:
        """为单个簇生成双语标签。

        策略：将 top TF-IDF 关键词与 ISAC 子类别词表匹配，
        选择匹配度最高的子类别作为簇标签。

        Args:
            top_terms: 簇的 top TF-IDF 关键词
            cards_in_cluster: 簇中的论文卡片

        Returns:
            簇标签（如 "Beamforming_and_Precoding (波束赋形与预编码)"）
        """
        # 方法1: 使用簇内论文的 best_fit_category 的众数
        cat_votes = {}
        for card in cards_in_cluster:
            cat = card.best_fit_category
            if cat and cat != config.PLACEHOLDER_TEXT:
                cat_votes[cat] = cat_votes.get(cat, 0) + 1
        if cat_votes:
            best_cat = max(cat_votes, key=cat_votes.get)
            if cat_votes[best_cat] >= len(cards_in_cluster) * 0.3:
                return best_cat

        # 方法2: 使用 TF-IDF 关键词与子类别词表匹配
        scores = {}
        terms_lower = set(t.lower() for t in top_terms)
        for cat_key, keywords in config.ISAC_SUBCATEGORIES.items():
            score = sum(
                1 for kw in keywords
                if any(kw.lower() in term or term in kw.lower()
                       for term in terms_lower)
            )
            scores[cat_key] = score

        if scores and max(scores.values()) > 0:
            best_cat = max(scores, key=scores.get)
            return best_cat

        # 方法3: 回退
        return "Standardization_and_Architecture"

    # ========================================================================
    # 分类法 Markdown 生成
    # ========================================================================

    def generate_taxonomy(
        self,
        cards: List[PaperCard],
        cluster_result: Dict[str, Any],
    ) -> str:
        """生成 taxonomy.md 格式的分类法文档。

        Args:
            cards: 论文卡片列表
            cluster_result: fit() 返回的聚类结果字典

        Returns:
            Markdown 格式的分类法文档字符串
        """
        labels = cluster_result["labels"]
        n_clusters = cluster_result["n_clusters"]
        silhouette = cluster_result["silhouette"]
        top_terms = cluster_result["top_terms_per_cluster"]

        lines = []
        lines.append("# ISAC 研究分类法 (Taxonomy)")
        lines.append("")
        lines.append(f"**自动生成时间**: {__import__('datetime').datetime.now().isoformat()}")
        lines.append(f"**论文总数**: {len(cards)}")
        lines.append(f"**分类簇数**: {n_clusters}")
        lines.append(f"**轮廓系数**: {silhouette:.4f}")
        lines.append("")
        lines.append("---")
        lines.append("")

        # 按簇整理论文
        for k in range(1, n_clusters + 1):
            mask = labels == k
            cluster_cards = [cards[i] for i, m in enumerate(mask) if m]
            if not cluster_cards:
                continue

            # 簇标签
            top_k_terms = top_terms.get(k, ["unknown"])
            cluster_label = self._label_cluster(top_k_terms, cluster_cards)
            label_zh = config.ISAC_SUBCATEGORIES.get(cluster_label, ["未知类别"])
            label_display = f"{cluster_label}"

            # 写簇标题
            lines.append(f"## 类别 {k}: {label_display}")
            lines.append("")
            lines.append(f"**论文数量**: {len(cluster_cards)}")
            lines.append(f"**关键词**: {', '.join(top_k_terms[:5])}")
            lines.append("")

            # 子类别分布
            subcats = {}
            for card in cluster_cards:
                sc = card.best_fit_category or "未分类"
                subcats[sc] = subcats.get(sc, 0) + 1
            if len(subcats) > 1:
                lines.append("**子类别分布**:")
                for sc, cnt in sorted(subcats.items(), key=lambda x: -x[1]):
                    lines.append(f"- {sc}: {cnt} 篇")
                lines.append("")

            # 列出论文
            lines.append("| # | 标题 | 创新类型 | 置信度 |")
            lines.append("|---|------|----------|--------|")
            for i, card in enumerate(cluster_cards, 1):
                title_short = card.title[:70] + "..." if len(card.title) > 70 else card.title
                innov_label = config.INNOVATION_TYPES.get(
                    card.innovation_type,
                    {"label_zh": card.innovation_type or "未知"}
                ).get("label_zh", card.innovation_type)
                lines.append(
                    f"| {i} | [{title_short}](https://arxiv.org/abs/{card.arxiv_id}) "
                    f"| {innov_label} | {card.confidence_level.upper()} |"
                )
            lines.append("")

        # 底部统计
        lines.append("---")
        lines.append("")
        lines.append("## 统计信息")
        lines.append("")
        lines.append(f"- 总论文数: {len(cards)}")
        lines.append(f"- 分类簇数: {n_clusters}")
        lines.append(f"- 轮廓系数: {silhouette:.4f} (范围[-1,1], 越高越好)")

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
    print("TaxonomyBuilder 自检")
    print("=" * 60)

    # 构造模拟论文卡片
    from lib.card_schema import PaperCard

    mock_cards = []
    mock_data = [
        ("Deep Learning for ISAC Beamforming", "Beamforming_and_Precoding",
         "deep learning beamforming MIMO precoding neural network ISAC beam management"),
        ("RIS-Assisted ISAC for THz Bands", "RIS_Metasurface_ISAC",
         "RIS reconfigurable intelligent surface THz phase shift metasurface beamforming"),
        ("Joint Radar and Communication Waveform Design", "Waveform_Design",
         "waveform design OFDM radar communication joint optimization modulation"),
        ("Physical Layer Security in ISAC Systems", "Security_and_Privacy",
         "security physical layer secrecy rate eavesdropping jamming secure ISAC"),
        ("Resource Allocation for 6G ISAC Networks", "Resource_Allocation",
         "resource allocation power control spectrum sharing scheduling optimization 6G"),
        ("Channel Estimation Techniques for ISAC", "Channel_Estimation_and_CSI",
         "channel estimation CSI pilot training sparse recovery compressed sensing ISAC"),
        ("Full-Duplex ISAC with Self-Interference Cancellation", "Full_Duplex_and_NOMA_ISAC",
         "full duplex self-interference cancellation FD ISAC simultaneous transmit receive"),
        ("Target Localization and Tracking in ISAC", "Localization_and_Tracking",
         "localization tracking target detection CRB parameter estimation radar sensing"),
        ("NOMA-Enhanced ISAC for IoT Applications", "Full_Duplex_and_NOMA_ISAC",
         "NOMA non-orthogonal multiple access ISAC IoT power domain SIC"),
        ("A Survey of Integrated Sensing and Communication", "Standardization_and_Architecture",
         "survey review overview ISAC 6G taxonomy framework standardization"),
    ] * 2  # 20 篇论文

    for i, (title, cat, abstract) in enumerate(mock_data):
        card = PaperCard(
            arxiv_id=f"2401.{i+1:05d}",
            title=title,
            authors=["Author A", "Author B"],
            abstract_raw=abstract,
            published_date="2024-01-15",
            primary_category="cs.IT",
            categories=["cs.IT", "eess.SP"],
            problem="Test problem",
            key_idea=f"Key idea for {title}",
            method="Test method",
            dataset_or_scenario="Simulation",
            metrics="Spectral efficiency",
            results_summary="Good results",
            innovation_type="novel_approach",
            limitations="Limited scope",
            best_fit_category=cat,
            confidence_level="high",
        )
        mock_cards.append(card)

    # 测试聚类
    builder = TaxonomyBuilder(max_features=100)
    result = builder.fit(mock_cards)
    print(f"\n聚类结果:")
    print(f"  簇数: {result['n_clusters']}")
    print(f"  轮廓系数: {result['silhouette']:.4f}")
    for k, terms in result["top_terms_per_cluster"].items():
        print(f"  簇 {k}: {', '.join(terms[:5])}")

    # 测试分类法生成
    taxonomy_md = builder.generate_taxonomy(mock_cards, result)
    print(f"\n分类法文档长度: {len(taxonomy_md)} 字符")
    print(f"前200字符:\n{taxonomy_md[:200]}...")

    print("\n自检完成。")
