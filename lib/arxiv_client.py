#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
arXiv API 客户端封装 — 速率限制、重试机制、断点续传
=============================================================================
对 arXiv API (export.arxiv.org) 的 HTTP 客户端封装，提供：
- 礼貌速率限制（≥3秒间隔）
- 指数退避重试（3s → 9s → 27s）
- 断点续传（checkpoint JSON）
- 多查询合并去重
- Atom XML 解析

arXiv API 规范：
- 请求间隔 ≥ 3 秒（礼貌使用政策）
- 每次最多返回 100 条（max_results 参数上限为 2000 但分页推荐 100）
- 响应格式：Atom XML
"""

from __future__ import annotations
import time
import json
import sys
import os
import urllib.request
import urllib.error
import urllib.parse
import xml.etree.ElementTree as ET
from typing import List, Dict, Generator, Optional, Set, Any
from datetime import datetime, timezone, timedelta
from pathlib import Path

# 允许从项目根目录运行
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


# ============================================================================
# XML 命名空间
# ============================================================================
ARXIV_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
    "opensearch": "http://a9.com/-/spec/opensearch/1.1/",
}


class ArxivClient:
    """arXiv API 客户端，封装速率限制、重试和断点续传逻辑。

    使用方式：
        client = ArxivClient()
        papers = client.fetch_all_primary()
        # 或逐步：
        for paper in client.search(query, max_results=100):
            process(paper)
    """

    def __init__(
        self,
        delay_seconds: float = None,
        max_retries: int = None,
        timeout: int = None,
    ):
        """初始化 arXiv 客户端。

        Args:
            delay_seconds: 请求间礼貌间隔（秒），默认从 config 读取
            max_retries: HTTP 错误最大重试次数
            timeout: 请求超时（秒）
        """
        self.delay_seconds = delay_seconds or config.ARXIV_DELAY_SECONDS
        self.max_retries = max_retries or config.ARXIV_MAX_RETRIES
        self.timeout = timeout or config.ARXIV_TIMEOUT
        self._last_request_time: float = 0.0
        self._request_count: int = 0

    # ========================================================================
    # 核心方法：执行查询
    # ========================================================================

    def search(
        self,
        query: str,
        max_results: int = 100,
        start: int = 0,
        sort_by: str = "submittedDate",
        sort_order: str = "descending",
    ) -> Generator[Dict[str, Any], None, None]:
        """执行单次 arXiv API 查询，返回论文生成器。

        自动处理分页：arXiv API 每次最多返回 page_size 条，
        此方法通过递增 start 参数循环获取直到达到 max_results。

        Args:
            query: arXiv API 搜索查询字符串
            max_results: 总计希望获取的论文数
            start: 起始偏移量（用于续传）
            sort_by: 排序字段（submittedDate / relevance / lastUpdatedDate）
            sort_order: 排序方向（ascending / descending）

        Yields:
            每篇论文的字典，包含：
            arxiv_id, title, authors, abstract, published_date,
            primary_category, categories, updated_date, pdf_url, comment
        """
        fetched = 0
        current_start = start
        page_size = min(config.ARXIV_PAGE_SIZE, max_results)

        while fetched < max_results:
            # 构造请求 URL
            params = {
                "search_query": query,
                "start": current_start,
                "max_results": min(page_size, max_results - fetched),
                "sortBy": sort_by,
                "sortOrder": sort_order,
            }
            url = config.ARXIV_API_BASE + "?" + urllib.parse.urlencode(params)

            # 发送请求（含速率限制和重试）
            xml_data = self._fetch_url(url)
            if xml_data is None:
                break  # 请求失败且重试耗尽

            # 解析 XML
            papers_in_page = self._parse_atom_response(xml_data)
            if not papers_in_page:
                break  # 空结果，停止分页

            for paper in papers_in_page:
                yield paper
                fetched += 1

            current_start += len(papers_in_page)

            # 如果返回数少于请求数，说明已到末尾
            if len(papers_in_page) < min(page_size, max_results - fetched + len(papers_in_page)):
                break

    # ========================================================================
    # 高级方法：多查询合并、断点续传
    # ========================================================================

    def fetch_all_with_queries(
        self,
        queries: List[str],
        max_per_query: int = 100,
    ) -> List[Dict[str, Any]]:
        """执行多个查询，合并去重后返回论文列表。

        主查询获取大部分结果，回退查询补充遗漏方向。
        按 arXiv ID 去重（保留首次出现的条目）。

        Args:
            queries: 查询字符串列表（第一个为主查询）
            max_per_query: 每个查询的最大返回数

        Returns:
            去重后的论文列表
        """
        seen_ids: Set[str] = set()
        all_papers: List[Dict[str, Any]] = []

        for i, query in enumerate(queries):
            query_label = "主查询" if i == 0 else f"回退查询 #{i}"
            print(f"\n{'='*50}")
            print(f"执行{query_label}: {query[:80]}...")
            print(f"{'='*50}")

            query_papers = 0
            try:
                for paper in self.search(query, max_results=max_per_query):
                    arxiv_id = paper.get("arxiv_id", "")
                    if arxiv_id and arxiv_id not in seen_ids:
                        seen_ids.add(arxiv_id)
                        all_papers.append(paper)
                        query_papers += 1
                        if query_papers % 10 == 0:
                            print(f"  已获取 {query_papers} 篇 (累计去重: {len(all_papers)})")
            except Exception as e:
                print(f"  查询出错: {e}", file=sys.stderr)
                continue

            print(f"  本查询新增: {query_papers} 篇 (累计去重: {len(all_papers)})")

        return all_papers

    def fetch_with_resume(
        self,
        query: str,
        max_results: int,
        checkpoint_path: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """支持断点续传的论文抓取。

        首次运行完整抓取；中断后再次调用时从上次断点继续。
        断点信息写入 checkpoint JSON 文件。

        Args:
            query: arXiv 查询字符串
            max_results: 最大论文数
            checkpoint_path: 断点文件路径，None 则使用默认路径

        Returns:
            论文列表（含之前已抓取 + 新抓取的）
        """
        if checkpoint_path is None:
            checkpoint_path = str(config.FETCH_CHECKPOINT_PATH)
        cp_path = Path(checkpoint_path)

        # 尝试加载断点
        existing_papers: List[Dict[str, Any]] = []
        fetched_ids: Set[str] = set()
        start_offset = 0

        if cp_path.exists():
            try:
                with open(cp_path, "r", encoding="utf-8") as f:
                    cp = json.load(f)
                existing_papers = cp.get("papers", [])
                fetched_ids = set(cp.get("fetched_ids", []))
                start_offset = cp.get("total_fetched", 0)
                print(f"[OK] 从断点恢复: 已保存 {len(existing_papers)} 篇论文, "
                      f"将从此处继续抓取 (offset={start_offset})")
            except (json.JSONDecodeError, KeyError) as e:
                print(f"警告: 断点文件损坏，重新开始 ({e})")
                existing_papers, fetched_ids, start_offset = [], set(), 0

        # 继续抓取
        new_papers = []
        try:
            for paper in self.search(
                query, max_results=max_results,
                start=start_offset,
            ):
                arxiv_id = paper.get("arxiv_id", "")
                if arxiv_id and arxiv_id not in fetched_ids:
                    fetched_ids.add(arxiv_id)
                    new_papers.append(paper)
                    existing_papers.append(paper)

                    # 每抓取 10 篇保存一次断点
                    if len(new_papers) % 10 == 0:
                        self._save_checkpoint(
                            cp_path, existing_papers, list(fetched_ids),
                            start_offset + len(new_papers)
                        )
                        print(f"  进度: {start_offset + len(new_papers)}/{max_results} "
                              f"(本批次新增 {len(new_papers)})")
        except KeyboardInterrupt:
            print("\n\n用户中断！正在保存断点...")
            self._save_checkpoint(
                cp_path, existing_papers, list(fetched_ids),
                start_offset + len(new_papers)
            )
            print(f"断点已保存。共 {len(existing_papers)} 篇论文。")
            raise

        # 完成：删除断点文件
        if cp_path.exists():
            cp_path.unlink()
            print(f"抓取完成，已清除断点文件。")

        return existing_papers

    # ========================================================================
    # HTTP 底层
    # ========================================================================

    def _fetch_url(self, url: str) -> Optional[str]:
        """发送 HTTP GET 请求，含速率限制和指数退避重试。

        Args:
            url: 完整的 arXiv API URL

        Returns:
            响应体 XML 字符串，或 None（请求失败）
        """
        # 速率限制：确保距上次请求 ≥ delay_seconds
        elapsed = time.monotonic() - self._last_request_time
        if elapsed < self.delay_seconds:
            wait = self.delay_seconds - elapsed
            time.sleep(wait)

        for attempt in range(1, self.max_retries + 1):
            try:
                self._last_request_time = time.monotonic()
                self._request_count += 1

                req = urllib.request.Request(
                    url,
                    headers={"User-Agent": "ISAC-Survey-Bot/1.0 (Academic Research)"}
                )
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    xml_data = resp.read().decode("utf-8")
                    return xml_data

            except urllib.error.HTTPError as e:
                if e.code == 503:
                    # arXiv 过载 — 指数退避
                    wait = 3 ** attempt  # 3, 9, 27 秒
                    print(f"  arXiv返回503(过载)，{wait}秒后重试 (第{attempt}/{self.max_retries}次)...")
                    time.sleep(wait)
                elif e.code == 400:
                    print(f"  arXiv返回400(错误请求): {e}", file=sys.stderr)
                    return None
                else:
                    print(f"  HTTP错误 {e.code}: {e}", file=sys.stderr)
                    if attempt < self.max_retries:
                        time.sleep(3 ** attempt)
                    else:
                        return None

            except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
                print(f"  网络错误: {e}，重试中... (第{attempt}/{self.max_retries}次)")
                if attempt < self.max_retries:
                    time.sleep(3 ** attempt)
                else:
                    return None

            except Exception as e:
                print(f"  未知错误: {e}", file=sys.stderr)
                return None

        return None

    # ========================================================================
    # XML 解析
    # ========================================================================

    def _parse_atom_response(self, xml_data: str) -> List[Dict[str, Any]]:
        """解析 arXiv API 返回的 Atom XML 响应。

        Args:
            xml_data: Atom XML 字符串

        Returns:
            解析后的论文字典列表
        """
        papers = []
        try:
            root = ET.fromstring(xml_data)
        except ET.ParseError as e:
            print(f"  XML解析错误: {e}", file=sys.stderr)
            return papers

        # 遍历每个 <entry> 元素
        for entry in root.findall("atom:entry", ARXIV_NS):
            try:
                paper = self._parse_entry(entry)
                if paper and paper.get("arxiv_id"):
                    papers.append(paper)
            except Exception as e:
                print(f"  条目解析错误: {e}", file=sys.stderr)
                continue

        return papers

    def _parse_entry(self, entry: ET.Element) -> Optional[Dict[str, Any]]:
        """解析单个 Atom <entry> 元素。

        Args:
            entry: XML Element

        Returns:
            论文字典
        """
        def _text(tag: str, default: str = "") -> str:
            """安全获取元素文本内容。"""
            el = entry.find(tag, ARXIV_NS)
            return el.text.strip() if el is not None and el.text else default

        def _list(tag: str) -> List[str]:
            """安全获取元素列表文本。"""
            els = entry.findall(tag, ARXIV_NS)
            return [e.text.strip() for e in els if e.text]

        # ---- 提取各字段 ----
        # arXiv ID（从 URL 中提取）
        id_url = _text("atom:id")
        arxiv_id = ""
        if id_url:
            # 典型格式: http://arxiv.org/abs/2401.00001v1
            arxiv_id = id_url.split("/abs/")[-1].split("v")[0] if "/abs/" in id_url else ""

        title = _text("atom:title")
        # 清理标题中的多余空白
        title = " ".join(title.split()) if title else ""

        # 摘要
        abstract = _text("atom:summary")
        abstract = " ".join(abstract.split()) if abstract else ""

        # 作者
        authors = _list("atom:author/atom:name")

        # 日期
        published_str = _text("atom:published")
        published_date = ""
        if published_str:
            try:
                # 格式: 2024-01-15T18:00:00Z
                published_date = published_str[:10]
            except (ValueError, IndexError):
                published_date = published_str

        updated_str = _text("atom:updated")
        updated_date = ""
        if updated_str:
            try:
                updated_date = updated_str[:10]
            except (ValueError, IndexError):
                updated_date = updated_str

        # 分类
        categories = []
        primary_category = ""
        cat_el = entry.find("arxiv:primary_category", ARXIV_NS)
        if cat_el is not None:
            primary_category = cat_el.get("term", "")
        for cat in entry.findall("atom:category", ARXIV_NS):
            term = cat.get("term", "")
            if term:
                categories.append(term)

        # PDF 链接
        pdf_url = ""
        for link in entry.findall("atom:link", ARXIV_NS):
            if link.get("title") == "pdf":
                pdf_url = link.get("href", "")
                break

        # 注释
        comment = _text("arxiv:comment")

        # 跳过无效条目
        if not arxiv_id or not title:
            return None

        return {
            "arxiv_id": arxiv_id,
            "title": title,
            "authors": authors,
            "abstract": abstract,
            "published_date": published_date,
            "updated_date": updated_date,
            "primary_category": primary_category,
            "categories": categories,
            "pdf_url": pdf_url,
            "comment": comment,
        }

    # ========================================================================
    # 后处理与过滤
    # ========================================================================

    @staticmethod
    def filter_by_date(
        papers: List[Dict[str, Any]],
        months_back: int = None,
    ) -> List[Dict[str, Any]]:
        """按发表日期过滤论文（保留近 N 个月的）。

        Args:
            papers: 论文列表
            months_back: 保留近几个月，默认从 config 读取

        Returns:
            过滤后的论文列表
        """
        if months_back is None:
            months_back = config.LOOKBACK_MONTHS

        cutoff = datetime.now(timezone.utc) - timedelta(days=months_back * 30)
        filtered = []
        for p in papers:
            date_str = p.get("published_date", "")
            if not date_str:
                # 无日期信息，保留（不过滤）
                filtered.append(p)
                continue
            try:
                pub_date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                if pub_date >= cutoff:
                    filtered.append(p)
            except ValueError:
                # 日期格式无法解析，保留
                filtered.append(p)
        return filtered

    @staticmethod
    def filter_by_categories(
        papers: List[Dict[str, Any]],
        target_categories: List[str] = None,
    ) -> List[Dict[str, Any]]:
        """按分类过滤论文。

        Args:
            papers: 论文列表
            target_categories: 目标分类列表，默认从 config 读取

        Returns:
            匹配任一目标分类的论文列表
        """
        if target_categories is None:
            target_categories = config.TARGET_CATEGORIES

        filtered = []
        for p in papers:
            cats = set(p.get("categories", []))
            cats.add(p.get("primary_category", ""))
            if cats.intersection(target_categories):
                filtered.append(p)
        return filtered

    @staticmethod
    def filter_by_abstract_quality(
        papers: List[Dict[str, Any]],
        min_length: int = None,
    ) -> List[Dict[str, Any]]:
        """过滤摘要质量不足的论文。

        移除以下情况的论文：
        - 摘要为空或仅含空白字符
        - 摘要长度不足 min_length 字符
        - 摘要为 arXiv 自动生成的占位符

        Args:
            papers: 论文列表
            min_length: 最小摘要长度，默认从 config 读取

        Returns:
            过滤后的论文列表
        """
        if min_length is None:
            min_length = config.MIN_ABSTRACT_LENGTH

        filtered = []
        removed_empty = 0
        removed_short = 0

        for p in papers:
            abstract = (p.get("abstract", "") or "").strip()
            if not abstract:
                removed_empty += 1
                continue
            if len(abstract) < min_length:
                removed_short += 1
                continue
            filtered.append(p)

        if removed_empty or removed_short:
            print(f"  摘要质量过滤: 移除 {removed_empty} 篇空摘要, "
                  f"{removed_short} 篇摘要过短 (<{min_length}字符)")
        return filtered

    @staticmethod
    def filter_by_isac_relevance(
        papers: List[Dict[str, Any]],
        min_hits: int = None,
    ) -> List[Dict[str, Any]]:
        """过滤与 ISAC 领域不相关的论文。

        检查每篇论文的标题+摘要中是否包含足够的 ISAC 核心关键词。
        同时排除明确不相关的 arXiv 分类。

        Args:
            papers: 论文列表
            min_hits: 最少 ISAC 关键词命中数，默认从 config 读取

        Returns:
            过滤后的论文列表
        """
        if min_hits is None:
            min_hits = config.MIN_ISAC_KEYWORD_HITS

        keywords_lower = [kw.lower() for kw in config.ISAC_CORE_KEYWORDS]
        excluded_prefixes = tuple(
            cat.split(".")[0].lower() if "." in cat else cat.lower()
            for cat in config.EXCLUDED_CATEGORIES
        )

        filtered = []
        removed_irrelevant = 0
        removed_category = 0

        for p in papers:
            # 检查排除分类
            cats = [c.lower() for c in p.get("categories", [])]
            cats.append((p.get("primary_category", "") or "").lower())
            if any(
                any(c.startswith(ep) for ep in excluded_prefixes)
                for c in cats if c
            ):
                removed_category += 1
                continue

            # 检查 ISAC 关键词命中数
            text = (
                (p.get("title", "") or "") + " " +
                (p.get("abstract", "") or "")
            ).lower()

            hits = sum(1 for kw in keywords_lower if kw in text)
            if hits < min_hits:
                removed_irrelevant += 1
                continue

            filtered.append(p)

        if removed_category or removed_irrelevant:
            print(f"  ISAC相关性过滤: 移除 {removed_category} 篇排除分类, "
                  f"{removed_irrelevant} 篇关键词不足 (<{min_hits}命中)")
        return filtered

    @staticmethod
    def filter_duplicates_by_title(
        papers: List[Dict[str, Any]],
        threshold: float = 0.85,
    ) -> List[Dict[str, Any]]:
        """基于标题相似度去除疑似重复论文。

        使用简单的词集合 Jaccard 相似度检测标题相似的论文，
        保留首次出现的条目。

        Args:
            papers: 论文列表
            threshold: 相似度阈值

        Returns:
            去重后的论文列表
        """
        if len(papers) <= 1:
            return papers

        filtered = []
        seen_title_words = []

        for p in papers:
            title = (p.get("title", "") or "").lower()
            words = set(title.split())
            if not words:
                filtered.append(p)
                continue

            is_dup = False
            for prev_words in seen_title_words:
                if not prev_words:
                    continue
                intersection = words & prev_words
                union = words | prev_words
                if len(union) == 0:
                    continue
                jaccard = len(intersection) / len(union)
                if jaccard > threshold:
                    is_dup = True
                    break

            if not is_dup:
                filtered.append(p)
                seen_title_words.append(words)

        removed = len(papers) - len(filtered)
        if removed > 0:
            print(f"  标题去重: 移除 {removed} 篇疑似重复论文 "
                  f"(Jaccard阈值={threshold})")

        return filtered

    # ========================================================================
    # 内部辅助
    # ========================================================================

    def _save_checkpoint(
        self,
        path: Path,
        papers: List[Dict[str, Any]],
        fetched_ids: List[str],
        total_fetched: int,
    ) -> None:
        """保存断点信息。"""
        cp = {
            "papers": papers,
            "fetched_ids": fetched_ids,
            "total_fetched": total_fetched,
            "query_timestamp": datetime.now(timezone.utc).isoformat(),
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cp, f, ensure_ascii=False, indent=2)


# ============================================================================
# 自检代码
# ============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("ArxivClient 自检")
    print("=" * 60)

    client = ArxivClient()

    # 测试小规模查询（仅取 5 篇验证连通性）
    print("\n执行测试查询 (max_results=5)...")
    test_query = 'all:"integrated sensing and communication" AND cat:cs.IT'

    count = 0
    try:
        for paper in client.search(test_query, max_results=5):
            count += 1
            print(f"  #{count}: [{paper['arxiv_id']}] {paper['title'][:80]}...")
            print(f"       作者: {', '.join(paper['authors'][:3])}")
            print(f"       日期: {paper.get('published_date', 'N/A')}")
            print(f"       分类: {paper.get('primary_category', 'N/A')}")
            abstract_preview = paper.get('abstract', '')[:120]
            print(f"       摘要: {abstract_preview}...")
            print()
    except Exception as e:
        print(f"  测试查询失败: {e}")

    print(f"\n成功获取 {count} 篇论文。")
    print(f"总请求次数: {client._request_count}")
    print("自检完成。")
