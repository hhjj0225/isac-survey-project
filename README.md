# 面向6G的通信感知一体化（ISAC）文献综述自动化系统

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![arXiv](https://img.shields.io/badge/data-arXiv-red.svg)](https://arxiv.org/)
[![License](https://img.shields.io/badge/license-Academic-green.svg)]()

## 项目简介

面向6G通信感知一体化（Integrated Sensing and Communication, ISAC）方向的**AI辅助文献综述自动化系统**，实现从论文抓取、结构化提取、聚类分析到中文综述生成的全流程自动化。

### 核心能力

- **自动抓取**: 从 arXiv 检索 ISAC 领域论文（近2年，已收录 411 篇）
- **结构化提取**: 规则化 NLP 引擎从摘要中提取 11 个必填字段，生成结构化论文卡片
- **分类法构建**: TF-IDF + 层次聚类 + ISAC 领域知识库 → 10大方向 / 44个子方向多级分类
- **方法对比**: 自动生成包含方法优缺点、复杂度、适用场景的增强对比表
- **综述生成**: 输出包含领域分类、方法对比、趋势分析、研究空白的正式中文综述
- **质量控制**: 5层过滤（日期/分类/摘要质量/ISAC相关性/去重）+ 置信度评分 + 智能补充

### 数据规模

| 指标 | 数值 |
|------|------|
| 收录论文 | 411 篇 |
| 时间范围 | 2024-06 至 2026-06 |
| 研究方向 | 10 个大方向 |
| 卡片字段 | 11 个必填字段 |
| 置信度分布 | HIGH 18% / MEDIUM 82% / LOW 0% |

---

## 系统架构

```
arXiv API
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  fetch_arxiv.py ───────► data/papers_raw.json               │
│  5层质量过滤: 日期→分类→摘要质量→ISAC相关性→去重              │
├─────────────────────────────────────────────────────────────┤
│  generate_cards.py ────► data/paper_cards.jsonl             │
│  规则化NLP: 11字段提取 + 置信度评分                           │
├─────────────────────────────────────────────────────────────┤
│  cluster_analysis.py ───► data/taxonomy.md                  │
│  enhance_taxonomy.py  ──► data/comparison_table.csv         │
│  层次聚类 + ISAC知识库 → 多级分类 + 方法对比                  │
├─────────────────────────────────────────────────────────────┤
│  generate_final_digest.py ► data/weekly_digest.md           │
│  四大模块: 分类概述/方法对比/趋势分析/研究空白                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 环境配置

### 要求

- **Python**: 3.11 或更高版本
- **操作系统**: Windows 10/11、macOS 或 Linux
- **网络**: 需要访问 arXiv API (export.arxiv.org)

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/YOUR_USERNAME/isac-survey-project.git
cd isac-survey-project

# 2. 创建虚拟环境（推荐）
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt
```

### NLTK 数据

首次运行时会自动下载所需的分词和停用词数据。如遇网络问题，可手动执行：

```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')
```

---

## 快速开始

### 一键运行（推荐）

```bash
# 测试模式（5-10篇论文，2分钟内完成）
python run_pipeline.py --test

# 完整运行（≥200篇论文，约30分钟）
python run_pipeline.py --max 300

# 跳过抓取（使用已有数据）
python run_pipeline.py --skip-fetch --max 300
```

### 分阶段运行

```bash
# 阶段1: arXiv 论文抓取
python src/fetch_arxiv.py --max 300          # 完整抓取
python src/fetch_arxiv.py --resume           # 断点续传
python src/fetch_arxiv.py --test             # 测试模式

# 阶段2: 生成论文卡片
python src/generate_cards.py                 # 完整生成
python src/generate_cards.py --stats         # 查看统计
python src/supplement_cards.py               # 智能补充弱字段

# 阶段3: 聚类分析与增强
python src/cluster_analysis.py               # 基础聚类
python src/enhance_taxonomy.py               # 知识增强分类法

# 阶段4: 周度综述
python src/generate_final_digest.py          # 生成正式综述
```

### Windows 用户

双击 `run_weekly.bat` 一键启动，或在命令提示符中：

```cmd
run_weekly.bat --test
```

---

## 项目结构

```
isac-survey-project/
│
├── README.md                          # 项目文档
├── requirements.txt                   # Python 依赖
├── config.py                          # 中央配置（所有可调参数）
├── run_pipeline.py                    # 主控编排器（端到端执行）
├── run_weekly.bat                     # Windows 一键启动脚本
├── .gitignore                         # Git 忽略规则
│
├── src/                               # 流水线阶段模块
│   ├── fetch_arxiv.py                 # 阶段1: arXiv 抓取 + 5层过滤
│   ├── generate_cards.py              # 阶段2: NLP 卡片生成
│   ├── supplement_cards.py            #        智能补充低置信度卡片
│   ├── cluster_analysis.py            # 阶段3: 层次聚类 + 分类法
│   ├── enhance_taxonomy.py            #        知识增强分类法 + 对比表
│   ├── weekly_survey_generator.py     # 阶段4: 基础周度综述
│   └── generate_final_digest.py       #        正式综述（四大模块）
│
├── lib/                               # 公共库
│   ├── card_schema.py                 # PaperCard 数据模型（11字段验证）
│   ├── arxiv_client.py                # arXiv API 客户端（限速/重试/续传）
│   ├── nlp_engine.py                  # NLP 提取引擎（正则+置信度）
│   ├── taxonomy_builder.py            # 层次聚类管线（TF-IDF+SVD+Ward）
│   ├── comparison_table.py            # 对比表生成（CSV UTF-8 BOM）
│   └── chinese_template.py            # 中文综述参数化模板
│
├── data/                              # 输出文件（Git 跟踪）
│   ├── papers_raw.json                # 原始论文数据（411篇）
│   ├── paper_cards.jsonl              # 结构化论文卡片
│   ├── taxonomy.md                    # 多级分类法
│   ├── comparison_table.csv           # 方法对比表（19列）
│   ├── weekly_digest.md               # 周度正式综述
│   ├── card_validation_report.md      # 卡片校验报告
│   ├── method_analysis_report.md      # 方法分析报告
│   └── fetch_report.md                # 抓取统计报告
│
├── tests/                             # 单元测试
│   ├── __init__.py
│   └── fixtures/                      # 测试数据
│
├── logs/                              # 运行日志（Git 忽略）
└── .github/workflows/                 # GitHub Actions
    └── weekly-update.yml              # 每周自动更新
```

---

## 论文卡片字段说明

每篇论文经 NLP 提取后生成包含 **11 个必填字段** 的卡片：

| 字段 | 说明 | 提取方式 |
|------|------|----------|
| `title` | 论文标题 | arXiv 元数据直接映射 |
| `problem` | 研究问题/挑战 | 提示短语正则匹配 |
| `key_idea` | 核心思想 | 提示短语正则匹配 |
| `method` | 技术方法 | 提示短语正则匹配 |
| `dataset_or_scenario` | 数据集/仿真场景 | 关键词匹配 + 正则 |
| `metrics` | 评价指标 | 提示短语正则匹配 |
| `results_summary` | 结果摘要 | 提示短语正则匹配 |
| `innovation_type` | 创新类型（8类） | 关键词加权评分 |
| `limitations` | 局限性/未来工作 | 正则 + 智能推断 |
| `best_fit_category` | ISAC 子类别（10类） | 关键词词表匹配 |
| `confidence_level` | 提取置信度 | 5维加权评分 → high/medium/low |

**内容来源**: 所有字段均基于论文摘要提取，严禁编造。`[未能从摘要中提取]` 占位符确保字段永不空置。

---

## ISAC 研究方向分类

| 方向 | 英文标识 | 论文数 |
|------|----------|--------|
| 波形设计 | Waveform_Design | 92 |
| 标准化与系统架构 | Standardization_and_Architecture | 68 |
| RIS/智能超表面 | RIS_Metasurface_ISAC | 57 |
| 定位与跟踪 | Localization_and_Tracking | 55 |
| 波束赋形与预编码 | Beamforming_and_Precoding | 53 |
| 安全与隐私 | Security_and_Privacy | 26 |
| 资源分配 | Resource_Allocation | 25 |
| 信道估计与CSI | Channel_Estimation_and_CSI | 14 |
| ML驱动的ISAC | Machine_Learning_for_ISAC | 11 |
| 全双工与NOMA | Full_Duplex_and_NOMA_ISAC | 10 |

---

## GitHub 仓库配置

### 本地项目上传

```bash
# 1. 初始化 Git 仓库
cd isac-survey-project
git init

# 2. 配置 .gitignore（已提供，排除日志和缓存文件）
git add .gitignore

# 3. 添加所有文件
git add .

# 4. 首次提交
git commit -m "初始提交: ISAC文献综述自动化系统 v1.0

- 411篇ISAC论文自动抓取 (arXiv 2024-2026)
- 规则化NLP 11字段论文卡片提取
- 10大方向/44子方向多级分类法
- 增强方法对比表 (19列含优缺点/复杂度/场景)
- 首版正式中文综述 (四大模块)
- 5层质量过滤 + 置信度评分 + 智能补充"

# 5. 关联远程仓库（替换为你的仓库地址）
git remote add origin https://github.com/YOUR_USERNAME/isac-survey-project.git

# 6. 推送
git branch -M main
git push -u origin main
```

### GitHub Actions 自动更新（可选）

仓库已包含 `.github/workflows/weekly-update.yml` 工作流文件。
启用步骤：

1. 推送代码到 GitHub 后，工作流会自动生效
2. 默认每周一 UTC 08:00 自动运行
3. 也可在 GitHub 仓库页面 **Actions** → **Weekly ISAC Survey Update** → **Run workflow** 手动触发
4. 运行结果（更新后的 data/ 文件）会自动提交回仓库

---

## 常见问题

**Q: arXiv 抓取速度慢？**
A: 系统内置 3 秒礼貌间隔（符合 arXiv 使用政策）。200篇论文约需10-15分钟。

**Q: NLTK 数据下载失败？**
A: 手动执行 `python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"`

**Q: Windows 终端中文乱码？**
A: 系统已自动配置 UTF-8 编码。如仍有问题，在终端执行 `chcp 65001` 后重试。

**Q: 如何增加新的 ISAC 子方向？**
A: 编辑 `config.py` 中的 `ISAC_SUBCATEGORIES` 和 `ISAC_CORE_KEYWORDS`，重新运行 `enhance_taxonomy.py`。

---

## 课程作业进度

| 周次 | 任务 | 状态 |
|------|------|------|
| 第1周 | 选题 + 架构设计 + 抓取 ≥20篇 | ✅ 完成（411篇） |
| 第3周 | 累计 ≥50篇 + 完整卡片 + 初步分类 | ✅ 完成（411张卡片） |
| 第5周 | 首版综述 + 方法对比表 + 趋势分析 | ✅ 完成 |
| 第7周 | 完整项目 + 3次周度更新 + 最终报告 | 🔄 进行中 |

---

## 许可

本项目仅用于学术研究与课程作业。论文数据来源为 arXiv.org，引用请以原文为准。
