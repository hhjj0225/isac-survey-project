#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
ISAC 文献综述自动化系统 — 中央配置文件
研究方向：面向6G的通信感知一体化 (Integrated Sensing and Communication for 6G)
=============================================================================
所有可调参数集中于此，各模块通过 import config 统一引用。
修改配置无需改动业务代码。
"""

import os
from pathlib import Path

# ============================================================================
# 项目路径
# ============================================================================
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
LOG_DIR = PROJECT_ROOT / "logs"
TEST_DIR = PROJECT_ROOT / "tests"
CHECKPOINT_DIR = DATA_DIR  # 断点文件存放位置

# 确保必要目录存在
for _d in [DATA_DIR, LOG_DIR]:
    _d.mkdir(parents=True, exist_ok=True)

# ============================================================================
# 输出文件路径
# ============================================================================
PAPERS_RAW_PATH = DATA_DIR / "papers_raw.json"
PAPER_CARDS_PATH = DATA_DIR / "paper_cards.jsonl"
TAXONOMY_PATH = DATA_DIR / "taxonomy.md"
COMPARISON_TABLE_PATH = DATA_DIR / "comparison_table.csv"
WEEKLY_DIGEST_PATH = DATA_DIR / "weekly_digest.md"
FETCH_CHECKPOINT_PATH = DATA_DIR / ".fetch_checkpoint.json"

# ============================================================================
# arXiv API 配置
# ============================================================================
ARXIV_API_BASE = "http://export.arxiv.org/api/query"
ARXIV_DELAY_SECONDS = 3.0         # 礼貌间隔（秒），arXiv要求至少3秒
ARXIV_MAX_RETRIES = 3             # HTTP错误最大重试次数
ARXIV_TIMEOUT = 30                # 请求超时（秒）
ARXIV_PAGE_SIZE = 100             # 每次请求最大返回数（arXiv上限）
ARXIV_MAX_TOTAL_RESULTS = 300     # 抓取总数上限（需≥50有效论文）
ARXIV_MIN_REQUIRED_PAPERS = 50    # 阶段1最低论文数要求（课程要求≥50）
ARXIV_WARN_THRESHOLD = 50         # 低于此数发出警告

# ============================================================================
# arXiv 主查询 — ISAC 综合检索式（优化版）
# 策略：title+abstract 精确匹配 ISAC 核心术语，all 匹配具体子方向
# 避免 all:"ISAC" 的宽泛匹配引入无关论文
# ============================================================================
ARXIV_PRIMARY_QUERY = (
    # 核心ISAC术语 — 限定 title/abstract 避免全文误匹配
    '(ti:"integrated sensing and communication"'
    ' OR abs:"integrated sensing and communication"'
    ' OR ti:"integrated sensing and communications"'
    ' OR abs:"integrated sensing and communications"'
    ' OR ti:"joint sensing and communication"'
    ' OR abs:"joint sensing and communication"'
    ' OR ti:"joint communication and sensing"'
    ' OR abs:"joint communication and sensing"'
    ' OR ti:"dual-function radar communication"'
    ' OR abs:"dual-function radar communication"'
    ' OR ti:"dual-functional radar communication"'
    ' OR abs:"dual-functional radar communication"'
    ' OR ti:"radar-communication"'
    ' OR abs:"radar-communication"'
    # 缩写和变体 — 结合6G/通信上下文
    ' OR (ti:ISAC AND (cat:cs.IT OR cat:eess.SP OR cat:cs.NI OR cat:cs.MM))'
    ' OR (ti:DFRC AND (cat:cs.IT OR cat:eess.SP))'
    ' OR (abs:"ISAC" AND (abs:"6G" OR abs:"MIMO" OR abs:"beamforming" OR abs:"waveform"))'
    # 具体ISAC子方向
    ' OR all:"sensing and communication coexistence"'
    ' OR (all:"joint radar" AND all:"communication" AND (cat:cs.IT OR cat:eess.SP))'
    ')'
)

# 回退查询 — 各子方向补充检索（title+abstract 级别精准匹配）
ARXIV_FALLBACK_QUERIES = [
    # 波束赋形方向
    '(ti:"ISAC" AND abs:"beamforming") OR (abs:"ISAC" AND ti:"beamforming")',
    # 波形设计方向
    '(ti:"ISAC" AND abs:"waveform") OR (abs:"ISAC" AND ti:"waveform")',
    # MIMO方向
    '(ti:"ISAC" AND abs:"MIMO") OR (abs:"ISAC" AND ti:"MIMO") OR (ti:"integrated sensing" AND abs:"MIMO")',
    # RIS方向
    '(ti:"ISAC" AND abs:"RIS") OR (abs:"ISAC" AND ti:"RIS") OR (abs:"ISAC" AND abs:"reconfigurable intelligent")',
    # 全双工方向
    '(ti:"ISAC" AND abs:"full duplex") OR (abs:"ISAC" AND abs:"full-duplex")',
    # NOMA方向
    '(ti:"ISAC" AND abs:"NOMA") OR (abs:"ISAC" AND ti:"NOMA")',
    # 资源分配方向
    '(ti:"ISAC" AND abs:"resource allocation") OR (abs:"joint sensing" AND abs:"resource")',
    # 信道估计方向
    '(abs:"ISAC" AND abs:"channel estimation") OR (abs:"integrated sensing" AND abs:"channel estimation")',
    # OFDM方向
    '(ti:"ISAC" AND abs:"OFDM") OR (abs:"ISAC" AND ti:"OFDM") OR (abs:"ISAC" AND abs:"OTFS")',
    # 6G + sensing方向
    'ti:"6G" AND abs:"sensing" AND (cat:cs.IT OR cat:eess.SP)',
    # 定位/感知精度方向
    '(abs:"ISAC" AND abs:"localization") OR (abs:"integrated sensing" AND abs:"CRB")',
    # 深度学习/ML方向
    '(abs:"ISAC" AND abs:"deep learning") OR (abs:"ISAC" AND abs:"neural network") OR (abs:"ISAC" AND abs:"reinforcement learning")',
    # 安全方向
    '(abs:"ISAC" AND abs:"security") OR (abs:"ISAC" AND abs:"physical layer security")',
    # 最新补充：2024-2025年新兴方向
    'abs:"integrated sensing" AND abs:"semantic communication"',
    'abs:"integrated sensing" AND abs:"near-field"',
]

# ============================================================================
# 日期过滤 — 近18个月
# ============================================================================
# arXiv API 不直接支持日期过滤，在 post-filter 阶段按 submittedDate 筛选
LOOKBACK_MONTHS = 24             # 近2年（课程要求）

# ============================================================================
# arXiv 目标分类（仅保留与 ISAC/6G 直接相关的分类）
# ============================================================================
TARGET_CATEGORIES = [
    "cs.IT",     # 信息论 — ISAC主要发表分类
    "eess.SP",   # 信号处理 — ISAC主要发表分类
    "cs.NI",     # 网络与互联网架构
    "cs.MM",     # 多媒体通信
    "cs.SY",     # 系统与控制
    "eess.SY",   # 电气系统
    "math.OC",   # 优化与控制
]

# ============================================================================
# ISAC 子类别关键词词表（用于聚类标注和卡片分类）
# ============================================================================
ISAC_SUBCATEGORIES = {
    "Waveform_Design": [
        "waveform", "OFDM", "OTFS", "modulation", "preamble",
        "pilot", "training sequence", "frame structure", "time-frequency",
        "resource block", "symbol", "subcarrier", "cyclic prefix"
    ],
    "Beamforming_and_Precoding": [
        "beamforming", "precoding", "beam management", "beam training",
        "beam alignment", "beam tracking", "codebook", "analog beamforming",
        "digital beamforming", "hybrid beamforming", "MIMO beamforming",
        "multiuser beamforming", "transmit beamforming", "beam pattern"
    ],
    "Resource_Allocation": [
        "resource allocation", "power allocation", "bandwidth allocation",
        "spectrum sharing", "resource management", "scheduling",
        "power control", "subcarrier allocation", "frequency allocation",
        "time allocation", "resource optimization", "energy efficiency"
    ],
    "Channel_Estimation_and_CSI": [
        "channel estimation", "channel state information", "CSI",
        "channel model", "channel prediction", "channel feedback",
        "channel reciprocity", "sparse channel", "compressed sensing channel",
        "pilot-based", "blind estimation", "semi-blind"
    ],
    "Machine_Learning_for_ISAC": [
        "deep learning", "neural network", "reinforcement learning",
        "machine learning", "CNN", "DNN", "transformer", "autoencoder",
        "federated learning", "online learning", "transfer learning",
        "generative model", "diffusion model", "graph neural network"
    ],
    "RIS_Metasurface_ISAC": [
        "RIS", "reconfigurable intelligent surface", "IRS",
        "intelligent reflecting surface", "metasurface", "meta-surface",
        "passive beamforming", "phase shift", "reflecting element"
    ],
    "Security_and_Privacy": [
        "security", "privacy", "eavesdropping", "secrecy rate",
        "physical layer security", "covert communication", "secure transmission",
        "jamming", "anti-jamming", "authentication", "encryption"
    ],
    "Localization_and_Tracking": [
        "localization", "tracking", "positioning", "sensing accuracy",
        "target detection", "parameter estimation", "CRB", "Cramér-Rao",
        "DoA", "ToA", "angle estimation", "range estimation", "velocity estimation",
        "radar detection", "multi-target", "clutter"
    ],
    "Full_Duplex_and_NOMA_ISAC": [
        "full duplex", "full-duplex", "self-interference cancellation",
        "NOMA", "non-orthogonal multiple access", "successive interference cancellation",
        "rate splitting", "RSMA"
    ],
    "Standardization_and_Architecture": [
        "standardization", "3GPP", "architecture", "protocol",
        "network architecture", "system-level", "deployment", "framework",
        "trade-off", "performance analysis", "fundamental limit", "capacity",
        "degrees of freedom", "information-theoretic"
    ],
}

# ============================================================================
# 创新类型定义
# ============================================================================
INNOVATION_TYPES = {
    "novel_approach": {
        "label_zh": "全新方法",
        "keywords": ["novel", "new framework", "first", "pioneering",
                      "unprecedented", "paradigm shift", "breakthrough"],
        "weight": 5
    },
    "incremental_improvement": {
        "label_zh": "增量改进",
        "keywords": ["improved", "enhanced", "better performance",
                      "outperforms", "superior", "gain of"],
        "weight": 1
    },
    "extension": {
        "label_zh": "扩展延伸",
        "keywords": ["extend", "extension", "generalize", "generalization",
                      "multi-user", "multi-antenna", "multi-cell"],
        "weight": 2
    },
    "integration": {
        "label_zh": "融合整合",
        "keywords": ["integrate", "integration", "combine", "unified",
                      "joint", "co-design", "holistic", "hybrid"],
        "weight": 3
    },
    "theoretical_contribution": {
        "label_zh": "理论贡献",
        "keywords": ["closed-form", "bound", "theorem", "proof", "convergence",
                      "optimal", "fundamental", "information-theoretic",
                      "derive", "analytical", "expression"],
        "weight": 4
    },
    "survey_or_review": {
        "label_zh": "综述/调研",
        "keywords": ["survey", "review", "overview", "tutorial",
                      "state-of-the-art", "comprehensive review",
                      "taxonomy", "classification"],
        "weight": 0
    },
    "unified_framework": {
        "label_zh": "统一框架",
        "keywords": ["unified framework", "general framework",
                      "unifying", "holistic approach", "end-to-end"],
        "weight": 4
    },
    "benchmark_study": {
        "label_zh": "基准研究",
        "keywords": ["benchmark", "comparison", "experimental evaluation",
                      "simulation study", "numerical results", "performance evaluation"],
        "weight": 1
    },
}

# ============================================================================
# NLP 提取配置
# ============================================================================
# 11个必填字段（不含元数据）的提示短语正则模式
# 每个字段包含: patterns(正则列表), fallback_position(位置回退策略),
#              context_window(上下文窗口句数)
CUE_PATTERNS = {
    "problem": {
        "patterns": [
            r"(?i)(?:however|but|nevertheless)\s*,?\s*(.+?(?:challenge|problem|issue|limitation|difficult|hard|critical|bottleneck|constraint).*?)(?:\.|$)",
            r"(?i)(.+?(?:suffer(?:s|ing)?\s*from|plagued\s*by|limited\s*by|hampered\s*by|degrad(?:es|ed|ation)\s*(?:due|because)|remains?\s*(?:a\s*)?challenge).*?)(?:\.|$)",
            r"(?i)(?:existing\s+(?:method|approach|technique|system|scheme|work)s?\s*.{0,40}?(?:cannot|fail|struggle|lack|unable|ineffective|insufficient|poor).*?)(?:\.|$)",
            r"(?i)(?:the\s+(?:main|key|major|critical|fundamental)\s+(?:challenge|problem|issue|difficulty|limitation|obstacle)\s*(?:is|lies?\s*in|concerns?|involves?)\s*(.+?))(?:\.|$)",
            r"(?i)(?:in\s+(?:contrast|practice)\s*,?\s*(.+?(?:issue|problem|challenge|difficulty).*?))(?:\.|$)",
            r"(?i)(?:despite\s+(?:the\s+)?(?:recent\s+)?(?:advances?|progress|development)s?\s*(?:in\s+)?.{0,60}?\s*,?\s*(.+?(?:still|remain|yet|continues?\s*to).*?))(?:\.|$)",
            r"(?i)^(.{20,200}?(?:challenge|problem|issue|limitation|difficulty).{0,80}?)(?:\.|$)",
        ],
        "fallback": "first_sentence",
        "context_window": 1,
    },
    "key_idea": {
        "patterns": [
            r"(?i)(?:we\s+(?:propose|present|introduce|develop|put\s+forward|suggest)\s+(?:a\s+)?(?:novel\s+)?(.{30,250}?)(?:\.\s+(?:Specifically|In\s+particular|The\s+key\s+idea|Our\s+approach))|(?:\.|$))",
            r"(?i)(?:this\s+(?:paper|work|letter|study|article)\s+(?:proposes?|presents?|introduces?|focuses?\s*on|investigates?)\s+(.{20,250}?))(?:\.|$)",
            r"(?i)(?:the\s+(?:key|core|main|central|fundamental|essential)\s+(?:idea|concept|insight|contribution|novelty|innovation)\s*(?:is|lies?\s*in|behind)\s*(.{20,250}?))(?:\.|$)",
            r"(?i)(?:our\s+(?:key\s+)?(?:contribution|proposal|approach|solution|framework|scheme|method)\s+(?:is|involves?|consists?\s*of|leverages?)\s*(.{20,250}?))(?:\.|$)",
            r"(?i)(?:we\s+(?:develop|design|formulate|construct|establish|build)\s+(?:a\s+)?(.{20,250}?)(?:framework|scheme|approach|method|technique|algorithm|system|architecture))",
            r"(?i)(?:unlike\s+(?:existing|conventional|traditional|prior|previous)\s+(?:work|approach|method|scheme)s?\s*,?\s*(.{20,250}?)(?:we\s+(?:propose|develop|introduce|present)))",
            r"(?i)^(.{30,300}?(?:propose|present|introduce|novel|new\s+(?:approach|method|framework|scheme|technique)).{0,100}?)(?:\.|$)",
        ],
        "fallback": "first_three_sentences",
        "context_window": 1,
    },
    "method": {
        "patterns": [
            r"(?i)(?:(?:we|our\s+(?:approach|method|framework|scheme|solution))\s+(?:employ|use|utilize|leverage|adopt|apply|exploit|harness|rely\s*on|based?\s*on)\s+(.{20,300}?))(?:\.|$)",
            r"(?i)(?:the\s+(?:proposed|developed|presented)\s+(?:method|approach|framework|scheme|technique|algorithm)\s+(?:is\s+based\s+on|relies?\s+on|utilizes?|employs?|leverages?|consists?\s*of)\s+(.{20,300}?))(?:\.|$)",
            r"(?i)(?:specifically\s*,?\s*(?:we|the\s+(?:proposed|developed)\s+(?:method|approach))\s+(?:formulate|model|characterize|derive|solve|optimize|design|implement)\s+(.{20,300}?))(?:\.|$)",
            r"(?i)(?:the\s+(?:optimization|problem|formulation)\s+(?:is|can\s+be)\s+(?:solved|tackled|addressed|handled|approached)\s+(?:by|using|via|through|with)\s+(.{20,250}?))(?:\.|$)",
            r"(?i)(?:by\s+(?:employing|using|leveraging|adopting|applying|exploiting|incorporating|integrating)\s+(.{20,300}?)(?:,\s*we|,\s*the|,\s*our|,\s*this))",
            r"(?i)(?:mathematically\s*,?\s*(.{20,300}?)(?:,\s*(?:where|with|and|the)))",
            r"(?i)(?:algorithm|technique|approach|method|framework|scheme).{0,40}?(?:based\s+on|using|employing|leveraging)\s+(.{20,250}?)(?:\.|,|$)",
        ],
        "fallback": "middle_sentences",
        "context_window": 1,
    },
    "dataset_or_scenario": {
        "patterns": [
            r"(?i)(?:(?:simulation|experiment|evaluation|validation|test|assessment)\s+(?:(?:is|was|are|were)\s+)?(?:conducted|performed|carried\s*out|done|executed)\s+(?:in|under|using|based\s*on|with|considering)\s+(.{15,200}?))(?:\.|,|$)",
            r"(?i)(?:we\s+(?:consider|assume|simulate|evaluate|investigate|study|analyze)\s+(?:a\s+)?(.{15,200}?)(?:scenario|setting|setup|system|environment|channel|network|configuration))",
            r"(?i)(?:(?:dataset|data\s+set)\s+(?:is\s+)?(?:from|based\s+on|collected\s+from|provided\s+by|available\s+at)\s+(.{15,150}?))(?:\.|,|$)",
            r"(?i)(?:(?:in|under)\s+(?:a\s+)?(.{15,120}?)(?:scenario|setting|setup|environment|deployment|configuration|condition))",
            r"(?i)(?:(?:channel\s+)?(?:model|fading)\s+(?:is|of|:)?\s*(.{10,100}?)(?:Rayleigh|Rician|Nakagami|mmWave|THz|sub-6|LOS|NLOS|urban|indoor|outdoor|vehicular))",
            r"(?i)(?:frequency\s+(?:band\s+)?(?:is|of|at|:)?\s*(.{10,100}?)(?:GHz|MHz|mmWave|sub-6|THz|band))",
            r"(?i)(?:(?:MIMO|antenna)\s+(?:configuration|setup|setting|array)\s+(?:with|of|:)?\s*(.{10,150}?))(?:\.|,|$)",
        ],
        "fallback": "search_entire_abstract",
        "context_window": 0,
    },
    "metrics": {
        "patterns": [
            r"(?i)(?:(?:performance|system|method|approach|scheme|framework)\s+(?:is|was|are|were)\s+(?:evaluated|assessed|measured|quantified|compared|validated|verified|analyzed)\s+(?:in\s+terms?\s+of|using|by|based\s+on|via|through)\s+(.{10,200}?))(?:\.|,|;|$)",
            r"(?i)(?:we\s+(?:evaluate|assess|measure|compare|quantify|analyze)\s+(?:the\s+)?(.{10,200}?)(?:performance|metric|result|gain|improvement|trade-off|efficiency|accuracy|rate|capacity|latency|throughput|coverage))",
            r"(?i)\b((?:spectral\s+efficiency|energy\s+efficiency|sum\s+rate|achievable\s+rate|data\s+rate|throughput|latency|BER|SER|BLER|SINR|SNR|MSE|RMSE|NMSE|CRB|CRLB|detection\s+probability|probability\s+of\s+detection|false\s+alarm|outage\s+probability|coverage\s+probability|localization\s+accuracy|positioning\s+error|tracking\s+error|beamforming\s+gain)\b.{0,120}?(?:\.|,|;))",
            r"(?i)(?:compared\s+(?:to|with)\s+(?:the\s+)?(?:baseline|benchmark|conventional|existing|traditional|state-of-the-art)\s*,?\s*(?:our|the\s+proposed)\s+(?:method|approach|scheme|framework)\s+(?:achieves?|obtains?|yields?|provides?|offers?|demonstrates?)\s+(.{10,200}?))(?:\.|,|$)",
            r"(?i)(?:achieves?\s+(?:a\s+)?(.{10,150}?)(?:gain|improvement|enhancement|increase|reduction|decrease|boost|saving)s?\s*(?:of|up\s+to|about|around|approximately|over|compared))",
            r"(?i)(?:(?:numerical|simulation|experimental)\s+results?\s+(?:show|demonstrate|indicate|reveal|confirm|verify|validate|illustrate|suggest)\s+(?:that\s+)?(.{15,200}?))(?:\.|$)",
        ],
        "fallback": "last_sentences",
        "context_window": 1,
    },
    "results_summary": {
        "patterns": [
            r"(?i)(?:(?:numerical|simulation|experimental|extensive)\s+results?\s+(?:show|demonstrate|indicate|reveal|confirm|verify|validate|illustrate|suggest|prove|evidence)\s+(?:that\s+)?(.{20,300}?))(?:\.|$)",
            r"(?i)(?:the\s+(?:proposed|developed|presented)\s+(?:method|approach|framework|scheme|technique|algorithm)\s+(?:achieves?|obtains?|yields?|provides?|offers?|delivers?|demonstrates?|shows?|exhibits?)\s+(.{20,300}?))(?:\.|$)",
            r"(?i)(?:(?:compared|relative)\s+(?:to|with)\s+(?:the\s+)?(?:baseline|benchmark|conventional|existing|traditional|state-of-the-art)\s*,?\s*(.{20,300}?)(?:gain|improvement|enhancement|increase|reduction|decrease|boost|outperform|superior|advantage))",
            r"(?i)(?:(?:our|the\s+proposed)\s+(?:method|approach|framework|scheme|technique)\s+(?:outperforms?|surpasses?|exceeds?|beats?)\s+(?:the\s+)?(?:existing|conventional|baseline|benchmark|state-of-the-art)\s+(?:by|with)\s+(.{15,200}?))(?:\.|,|$)",
            r"(?i)(?:achieves?\s+(?:a\s+)?(?:significant|remarkable|substantial|considerable|notable|promising)\s+(.{10,200}?)(?:gain|improvement|enhancement|increase|reduction|decrease|boost))",
            r"(?i)(?:in\s+(?:particular|summary|conclusion|essence)\s*,?\s*(.{20,300}?)(?:demonstrate|show|achieve|obtain|confirm|verify))",
            r"(?i)(?:(?:significantly|substantially|considerably|remarkably|notably)\s+(?:improves?|enhances?|increases?|reduces?|decreases?|boosts?|outperforms?)\s+(.{15,200}?))(?:\.|,|$)",
        ],
        "fallback": "last_two_sentences",
        "context_window": 1,
    },
    "innovation_type": {
        "patterns": [],  # 通过关键词评分函数 classify_innovation_type() 处理
        "fallback": "keyword_scoring",
        "context_window": 0,
    },
    "limitations": {
        "patterns": [
            r"(?i)(?:(?:future|further|more|additional|subsequent)\s+work\s+(?:should|could|may|can|will|must|need(?:s)?\s*to)\s*(?:address|consider|investigate|explore|study|examine|extend|improve|develop|focus\s*on)\s*(.{15,250}?))(?:\.|$)",
            r"(?i)(?:(?:however|nevertheless|nonetheless|yet|still|but)\s*,?\s*(?:the|our|this)\s+(?:proposed\s+)?(?:method|approach|framework|scheme|work|study)\s+(?:is\s+)?(?:limited|restricted|constrained|only|solely|exclusively)\s+(?:to|by|in)\s*(.{15,250}?))(?:\.|$)",
            r"(?i)(?:(?:limitation|shortcoming|drawback|weakness|disadvantage|downside|caveat|restriction|constraint)\s+(?:is|of|includes?|involves?|concerns?)\s*(.{15,250}?))(?:\.|$)",
            r"(?i)(?:(?:does|do)\s+not\s+(?:consider|account|address|handle|deal\s+with|capture|model|include|incorporate)\s*(.{15,250}?))(?:\.|$)",
            r"(?i)(?:(?:assumes?|presumes?|supposes?)\s+(?:ideal|perfect|full|complete|accurate|error-free|noiseless)\s*(.{15,200}?))(?:\.|,|$)",
            r"(?i)(?:(?:only|merely|just|solely|exclusively|purely)\s+(?:considers?|focuses?\s*on|deals?\s*with|addresses?|handles?|applies?\s+to|valid\s+for|works?\s+(?:for|in|under|when))\s*(.{15,200}?))(?:\.|$)",
            r"(?i)(?:extension\s+(?:to|towards?)\s+(.{15,200}?)(?:would|could|may|should|will)\s+(?:be|prove)\s+(?:interesting|valuable|useful|beneficial|important|necessary|needed))",
        ],
        "fallback": "infer_from_method",
        "context_window": 0,
    },
    "best_fit_category": {
        "patterns": [],  # 通过 ISAC_SUBCATEGORIES 词汇匹配函数处理
        "fallback": "vocabulary_scoring",
        "context_window": 0,
    },
}

# ============================================================================
# 置信度评分权重（总和100%）
# ============================================================================
CONFIDENCE_WEIGHTS = {
    "pattern_specificity": 0.30,   # 正则匹配特异性
    "supporting_sentences": 0.25,  # 支撑句数量
    "abstract_structure": 0.20,    # 摘要结构完整性
    "abstract_length": 0.15,       # 摘要长度充足度
    "numerical_data": 0.10,        # 数值数据存在性
}

CONFIDENCE_THRESHOLDS = {
    "high": 0.70,
    "medium": 0.40,
    # < 0.40 → "low"
}

# ============================================================================
# 聚类配置
# ============================================================================
TFIDF_MAX_FEATURES = 500
TFIDF_MAX_DF = 0.7
TFIDF_MIN_DF = 2                    # 最少出现在2篇论文中
TFIDF_NGRAM_RANGE = (1, 3)          # 1-3元词组
SVD_N_COMPONENTS_RATIO = 0.5        # SVD成分数 = min(50, n_papers * 0.5)
CLUSTER_K_MIN = 3                   # 最少簇数
CLUSTER_K_MAX_RATIO = 0.33          # 最多簇数 = n_papers * 0.33

# ============================================================================
# 周度综述配置
# ============================================================================
DIGEST_SECTIONS = [
    "executive_summary",       # 执行摘要
    "taxonomy_overview",       # 分类法概览
    "highlight_papers",        # 亮点论文（Top 3）
    "emerging_topics",         # 新兴话题
    "comparison_table_ref",    # 对比表引用
    "statistics",              # 统计信息
    "references",              # 参考文献
]

HIGHLIGHT_TOP_N = 3           # 亮点论文数量

# ============================================================================
# 日志配置
# ============================================================================
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ============================================================================
# 占位符文本（字段提取失败时使用）
# ============================================================================
PLACEHOLDER_TEXT = "[未能从摘要中提取]"

# ============================================================================
# NLTK 数据配置
# ============================================================================
NLTK_PACKAGES = ["punkt", "stopwords", "punkt_tab"]

# ============================================================================
# 论文质量过滤配置
# ============================================================================
# 硬性过滤条件：
# 1. 摘要长度 ≥ MIN_ABSTRACT_LENGTH 字符
# 2. 标题+摘要必须包含 ≥ MIN_ISAC_KEYWORD_HITS 个 ISAC 核心关键词
# 3. 排除明确无关的 arXiv 分类

MIN_ABSTRACT_LENGTH = 200          # 最小摘要长度（字符）

# ISAC 核心关键词 — 标题+摘要至少命中 N 个才算 ISAC 相关
MIN_ISAC_KEYWORD_HITS = 2          # 最少命中数

ISAC_CORE_KEYWORDS = [
    # 核心术语（每个命中计1分）
    "integrated sensing and communication",
    "ISAC",
    "dual-function radar communication",
    "joint sensing and communication",
    "joint communication and sensing",
    "DFRC",
    "radar-communication",
    "sensing and communication",
    "integrated sensing",
    "joint radar",
    # ISAC子方向术语（每个命中计1分）
    "sensing-assisted communication",
    "communication-assisted sensing",
    "radar sensing",
    "perceptive mobile network",
    "networked sensing",
    "integrated localization and communication",
    # 6G相关术语（与sensing共同出现时计分）
    "6G sensing",
    "6G ISAC",
    "sensing for 6G",
]

# 排除分类 — 明确与 ISAC 不相关的 arXiv 分类
EXCLUDED_CATEGORIES = [
    "q-bio",     # 定量生物学
    "q-fin",     # 定量金融
    "stat.AP",   # 应用统计
    "cond-mat",  # 凝聚态物理（非ISAC相关子类）
    "hep-th",    # 高能理论物理
    "hep-ph",    # 高能现象学
    "hep-ex",    # 高能实验
    "nucl-th",   # 核理论
    "nucl-ex",   # 核实验
    "astro-ph",  # 天体物理
    "gr-qc",     # 广义相对论
    "physics.bio", # 生物物理
    "physics.chem-ph", # 化学物理
    "physics.geo-ph", # 地球物理
    "physics.med-ph", # 医学物理
    "q-fin",      # 金融
]
