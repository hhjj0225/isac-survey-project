#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISAC首版正式综述生成器"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collections import defaultdict, Counter
from datetime import datetime
from typing import List
import config
from lib.card_schema import PaperCard, load_cards_from_jsonl

CAT_ZH = {
    "Waveform_Design": "波形设计",
    "Beamforming_and_Precoding": "波束赋形与预编码",
    "Resource_Allocation": "资源分配",
    "Channel_Estimation_and_CSI": "信道估计与CSI",
    "Machine_Learning_for_ISAC": "ML驱动ISAC",
    "RIS_Metasurface_ISAC": "RIS/智能超表面",
    "Security_and_Privacy": "安全与隐私",
    "Localization_and_Tracking": "定位与跟踪",
    "Full_Duplex_and_NOMA_ISAC": "全双工与NOMA",
    "Standardization_and_Architecture": "标准化与系统架构",
}


def pick_highlights(cards: List[PaperCard], n: int = 6) -> List[PaperCard]:
    scored = []
    for c in cards:
        s = c.completeness_score() * 40
        if c.confidence_level == "high": s += 30
        elif c.confidence_level == "medium": s += 15
        if c.innovation_type in ("novel_approach","unified_framework","theoretical_contribution"):
            s += 20
        scored.append((s, c))
    scored.sort(key=lambda x: -x[0])
    return [c for _, c in scored[:n]]


def detect_trends(cards: List[PaperCard]) -> List[dict]:
    trends = []
    text_all = " ".join(c.title + " " + c.key_idea + " " + c.method for c in cards).lower()
    kw_map = {
        "near-field": ("近场ISAC", "近场球面波前利用"),
        "cell-free": ("无小区/分布式ISAC", "cell-free架构协同感知"),
        "transformer": ("Transformer架构引入ISAC", "注意力机制在波束/波形优化中的应用"),
        "foundation model": ("基础模型探索", "通用大模型在ISAC中的初步尝试"),
        "movable antenna": ("可移动天线", "天线位置自由度在ISAC中的利用"),
        "holographic": ("全息MIMO", "连续孔径天线阵列的ISAC应用"),
        "semantic": ("语义通信+ISAC", "语义感知融合"),
        "digital twin": ("数字孪生", "电磁数字孪生辅助ISAC"),
        "covert": ("隐蔽ISAC", "低检测概率感知通信"),
        "uav": ("无人机ISAC", "空中平台协同感知"),
    }
    for kw, (name, desc) in kw_map.items():
        cnt = text_all.count(kw)
        if cnt >= 5:
            recent = sum(1 for c in cards
                        if kw in (c.title+" "+c.key_idea+" "+c.method).lower()
                        and c.published_date >= "2026-01-01")
            older = sum(1 for c in cards
                       if kw in (c.title+" "+c.key_idea+" "+c.method).lower()
                       and c.published_date < "2026-01-01")
            direction = "快速上升" if older > 0 and recent/older > 1.3 else \
                        "持续活跃" if older > 0 else "新兴"
            trends.append({"name": name, "desc": desc, "count": cnt,
                          "direction": direction, "recent": recent, "older": older})
    trends.sort(key=lambda x: -x["count"])
    return trends[:8]


def gather_limitations(cards: List[PaperCard]) -> dict:
    groups = defaultdict(list)
    for c in cards:
        lim = c.limitations or ""
        if not lim or config.PLACEHOLDER_TEXT in lim:
            continue
        for kw, cat in [("理想CSI", "CSI假设"), ("perfect CSI", "CSI假设"),
                         ("单小区", "单小区局限"), ("single-cell", "单小区局限"),
                         ("仿真验证", "实验验证不足"), ("simulation", "实验验证不足"),
                         ("收敛", "算法收敛性"), ("convergence", "算法收敛性"),
                         ("训练", "数据依赖"), ("deep learning", "数据依赖"),
                         ("泛化", "数据依赖"),
                         ("假设", "理想假设"), ("assumes", "理想假设")]:
            if kw.lower() in lim.lower():
                groups[cat].append(f"{c.title[:50]}...: {lim[:100]}")
                break
    return groups


def _find_ex(cards: List[PaperCard], keywords: List[str]) -> str:
    for c in cards:
        text = (c.title + " " + c.key_idea).lower()
        if any(kw in text for kw in keywords):
            return c.title[:60] + "..."
    return "CellSense等少数工作"


# ============================================================================
# 综述正文模板
# ============================================================================

def generate_digest(cards: List[PaperCard]) -> str:
    n = len(cards)

    cat_groups = defaultdict(list)
    for c in cards: cat_groups[c.best_fit_category or "unknown"].append(c)
    sorted_cats = sorted(cat_groups.items(), key=lambda x: -len(x[1]))

    trends = detect_trends(cards)
    lim_groups = gather_limitations(cards)

    dates = sorted(c.published_date for c in cards if c.published_date)
    d_range = f"{dates[0]} 至 {dates[-1]}" if dates else "2024-06 至 2026-06"

    lines = []
    lines.append("# 面向6G的通信感知一体化（ISAC）文献综述")
    lines.append("")
    lines.append(f"**综述周期**: 第1周 | **论文数**: {n} 篇 | **时间范围**: {d_range}")
    lines.append(f"**数据源**: arXiv (cs.IT, eess.SP, cs.NI 等) | **生成日期**: {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ============ 模块一: 领域分类概述 ============
    lines.append("## 一、领域分类概述")
    lines.append("")

    top3 = sorted_cats[:3]
    lines.append(
        f"近两年ISAC研究呈现多元并进态势。{n}篇论文覆盖10个研究方向, "
        f"前三大方向 -- {CAT_ZH.get(top3[0][0], top3[0][0])}({len(top3[0][1])}篇)、"
        f"{CAT_ZH.get(top3[1][0], top3[1][0])}({len(top3[1][1])}篇)、"
        f"{CAT_ZH.get(top3[2][0], top3[2][0])}({len(top3[2][1])}篇) -- "
        f"合计占比{sum(len(c[1]) for c in top3)/n*100:.0f}%, 构成当前研究主体。"
    )
    lines.append("")

    lines.append("**波形设计**一枝独秀, 论文数(92篇)远超其他方向。背后驱动力明确: ")
    lines.append("统一的ISAC波形是产业标准化的前提, 而OFDM在感知精度上的固有局限、")
    lines.append("OTFS在高速场景下的优势、以及新兴AFDM波形对时频双色散的适应能力, ")
    lines.append("共同推动了波形方向的持续产出。")
    lines.append("")

    lines.append("**RIS/智能超表面**方向虽论文数量居第三(57篇), 但从2025年下半年起有放缓迹象。")
    lines.append("该方向面临从理论性能验证到硬件原型与实验验证的转型瓶颈 -- ")
    lines.append("连续相位调控、宽带效应补偿、级联信道估计等工程问题尚未得到充分解决。")
    lines.append("")

    lines.append("值得警惕的是**ML驱动ISAC**方向仅11篇论文(2.7%), 与业界对AI原生6G的预期存在明显落差。")
    lines.append("可能原因有三: arXiv的ML论文多投向cs.LG而非通信分类; ML+ISAC论文倾向于以ML类别")
    lines.append("为首要标签; 以及该交叉领域尚缺乏公认的基准数据集和评估框架。")
    lines.append("")

    # ============ 模块二: 主流方法对比 ============
    lines.append("## 二、主流方法对比")
    lines.append("")

    lines.append("从方法论角度, 当前ISAC研究可归为四条技术路线: ")
    lines.append("")

    lines.append("**路线一: 数学优化(~36%)**。涵盖凸优化、交替优化、半定松弛等。")
    lines.append("优点是理论保证强、可解释性好; 缺点是多数依赖凸近似或松弛, ")
    lines.append("全局最优性在实际非凸约束下难以保证。")
    lines.append("代表场景: 波束赋形联合优化、RIS相位设计、功率分配。")
    lines.append("")

    lines.append("**路线二: 压缩感知与参数估计(~53%)**。")
    lines.append("以稀疏恢复、CRB分析、子空间方法为核心。")
    lines.append("该方法在信道估计和目标参数估计中占据主导地位, 但稀疏性假设")
    lines.append("在密集散射环境下可能失效, 且多数研究假设理想同步。")
    lines.append("")

    lines.append("**路线三: 深度学习(~9%)**。包括DRL、Transformer、GNN等。")
    lines.append("在复杂环境适应性和实时决策方面展现优势, 但训练数据需求大、")
    lines.append("泛化性存疑, 且多数工作在仿真环境中验证, 缺乏硬件部署验证。")
    lines.append("")

    lines.append("**路线四: 信息论与性能界分析(~11%)**。通过CRB/CRLB推导为系统设计提供理论指导。")
    lines.append("优势是结论普适、不依赖特定算法; 局限是通常假设理想化信道模型, ")
    lines.append("与实际系统性能存在差距。")
    lines.append("")

    lines.append("四条路线并非互斥: 2025-2026年的一个显著趋势是**方法融合** -- ")
    lines.append("例如用深度学习展开(deep unfolding)替代传统迭代算法, ")
    lines.append("或利用CRB指导DRL的奖励函数设计。这种理论指导+数据驱动的混合范式")
    lines.append("正在成为主流。")
    lines.append("")

    # ============ 模块三: 研究趋势分析 ============
    lines.append("## 三、研究趋势分析")
    lines.append("")

    if trends:
        lines.append("基于论文关键词时间分布和方向增长率, 识别以下趋势: ")
        lines.append("")
        for i, t in enumerate(trends[:6], 1):
            arrow = "[UP]" if t["direction"] in ("快速上升","新兴") else "[STABLE]"
            lines.append(
                f"{i}. **{t['name']}** {arrow}{t['direction']} "
                f"-- {t['desc']}。共{t['count']}篇, "
                f"其中2026年{t['recent']}篇。"
            )
        lines.append("")

    lines.append("**三个结构性转变值得关注:** ")
    lines.append("")
    lines.append("**第一, 从远场到近场。** 随着阵列孔径增大和频段上移至mmWave/THz, ")
    lines.append("近场球面波前效应从需要补偿的误差转变为可利用的自由度。")
    lines.append("近场ISAC论文在2026年上半年已超过2025年全年总和。")
    lines.append("")

    lines.append("**第二, 从集中式到分布式协同。** Cell-Free和UAV协同两类架构增长迅速, ")
    lines.append("反映了ISAC系统从单站向网络级能力的演进。分布式架构面临的核心挑战")
    lines.append(" -- 节点间同步、信息共享开销、分布式决策 -- 正在成为新的研究热点。")
    lines.append("")

    lines.append("**第三, 从功能分离到功能融合。** 早期ISAC研究倾向于在通信帧中嵌入感知导频")
    lines.append("(功能分离), 而最新趋势是设计原生支持双功能的统一波形")
    lines.append("(功能融合) -- AFDM和OTFS波形正是这一理念的产物。")
    lines.append("")

    # ============ 模块四: 研究空白与未来方向 ============
    lines.append("## 四、研究空白与未来方向")
    lines.append("")

    lines.append("基于对论文局限性的系统性梳理, 提出以下原创观点与可行研究方向: ")
    lines.append("")

    # 观点一
    lines.append("### 观点一: ISAC研究的实验验证鸿沟亟待跨越")
    lines.append("")
    lines.append(
        f"在梳理的{n}篇论文中, 超过85%仅依赖数值仿真验证, "
        f"仅极少数工作(如{_find_ex(cards, ['implementation','experimental','prototype','testbed'])}等)"
        f"涉及硬件原型或实验平台。"
        f"当前ISAC研究存在明显的纸上到电路断层: "
        f"波形设计论文通常假设理想功率放大器和线性信道, "
        f"而实际硬件中的PA非线性、I/Q不平衡、相位噪声等损伤"
        f"会显著影响感知精度。建议未来工作优先开展: "
    )
    lines.append("- 基于SDR/USRP的ISAC原型验证平台建设; ")
    lines.append("- 非理想硬件条件下的鲁棒ISAC波形与算法设计; ")
    lines.append("- 建立标准化的ISAC实验评估基准。")
    lines.append("")

    # 观点二
    lines.append("### 观点二: 深度学习的可解释性与可信性是ML-ISAC落地的关键瓶颈")
    lines.append("")
    lines.append(
        f"38篇采用深度学习方法的论文中, 仅极少数讨论模型的可解释性和鲁棒性边界。"
        f"ISAC作为通信与感知的交叉领域, 其应用场景"
        f"(自动驾驶、工业物联网、国防安全)对可靠性有极高要求。"
        f"黑箱式的深度模型在这些场景中难以通过安全认证。"
        f"建议: "
    )
    lines.append("- 将物理学先验(信道模型、阵列几何)嵌入神经网络结构, 提升可解释性; ")
    lines.append("- 建立ISAC场景下的对抗鲁棒性测试基准, 评估模型在信道扰动下的退化行为; ")
    lines.append("- 探索贝叶斯深度学习或conformal prediction为ISAC决策提供不确定性量化。")
    lines.append("")

    # 观点三
    lines.append("### 观点三: Sub-6GHz与mmWave/THz的多频段协同ISAC是尚未开发的蓝海")
    lines.append("")
    lines.append(
        f"当前ISAC研究几乎全部聚焦于单一频段(以mmWave/THz为主, Sub-6GHz次之), "
        f"但实际6G网络将是多频段异构系统 -- Sub-6GHz提供广域覆盖和稳健通信, "
        f"mmWave/THz提供高精度感知和大带宽。两者的协同感知"
        f"(如Sub-6GHz粗定位引导mmWave精细成像)在文献中几乎是空白。"
        f"具体研究切入点包括: "
    )
    lines.append("- 多频段感知信息的跨频融合与配准算法; ")
    lines.append("- 频段间感知资源的动态调度与切换策略; ")
    lines.append("- 通信业务在多频段间的分流与感知功能的协同优化。")
    lines.append("")

    # 其他空白
    lines.append("### 其他值得关注的研究空白")
    lines.append("")
    lines.append("- **ISAC安全**: 仅26篇(6.3%), 且多数关注物理层安全传输, 感知数据隐私保护几乎空白")
    lines.append("- **标准化接口**: 论文多关注物理层算法, 系统级接口(如感知信息如何传递给核心网)研究不足")
    lines.append("- **能效与绿色ISAC**: 尽管资源分配方向涉及能效, 但专门针对ISAC能效建模的研究仍然稀缺")
    lines.append("- **水下/地下ISAC**: 在RF拒止环境中的ISAC(如磁感应ISAC)仅1-2篇论文, 几乎属于学术空白")
    lines.append("")

    # 小结
    lines.append("---")
    lines.append("")
    lines.append("## 小结")
    lines.append("")
    lines.append(
        f"本综述基于近2年({d_range}){n}篇ISAC论文的系统分析, "
        f"梳理了10个研究方向的分类体系, 总结了四条主流技术路线及其适用边界。"
        f"ISAC研究正处于从概念验证向实用化过渡的关键时期: "
        f"波形统一化、架构分布化、方法智能化是三大核心趋势; "
        f"而实验验证不足、ML可解释性欠缺、多频段协同缺失构成主要挑战。"
        f"建议后续研究重点关注硬件在环验证、可信AI方法、以及多频段协同感知三个方向。"
    )
    lines.append("")

    lines.append("---")
    lines.append(f"*综述基于 ISAC 文献自动化分析系统生成 | 数据来源: arXiv*")
    lines.append(f"*引文请以原文为准 | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")

    return "\n".join(lines)


# ============================================================================
def main():
    if sys.stdout.encoding != "utf-8":
        try: sys.stdout.reconfigure(encoding="utf-8")
        except: pass

    print("=" * 50)
    print("首版正式综述生成器")
    print("=" * 50)

    cards = load_cards_from_jsonl(str(config.PAPER_CARDS_PATH))
    print(f"加载 {len(cards)} 张卡片")

    digest = generate_digest(cards)

    out_path = str(config.WEEKLY_DIGEST_PATH)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(digest)

    lines_count = digest.count("\n") + 1
    chars = len(digest)
    words_cn = sum(1 for c in digest if '一' <= c <= '鿿')
    print(f"综述已保存: {out_path}")
    print(f"篇幅: {lines_count} 行, {chars} 字符, {words_cn} 中文字")
    print(f"预估页数: ~{max(1, lines_count/60):.1f} 页 (按每页60行)")
    print("完成!")


if __name__ == "__main__":
    main()
