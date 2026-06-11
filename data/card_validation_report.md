# ISAC 论文卡片校验报告

**生成时间**: 2026-06-11T20:15:00.619280
**论文总数**: 411

## 1. 总体校验结论

- **卡片总数**: 411
- **11字段完整率**: 100% (0张占位符)
- **卡片有效数**: 411/411
- **内容来源**: 全部来自论文摘要，无编造
- **智能补充**: 修复了 407 张卡片的弱字段

## 2. 置信度分布

| 等级 | 补充前 | 补充后 | 变化 |
|------|--------|--------|------|
| HIGH | 63 | 74 | +11 |
| MEDIUM | 347 | 337 | -10 |
| LOW | 1 | 0 | -1 |

## 3. 各字段提取质量评估

| 字段 | 平均置信度 | 低分(<0.4) | 评级 | 说明 |
|------|-----------|-----------|------|------|
| ISAC子类别 | 0.549 | 70 (17%) | [WARN] 一般 | 部分卡片需人工审核 |
| 数据集/场景 | 0.585 | 29 (7%) | [OK] 良好 | 大部分卡片提取有效 |
| 创新类型 | 1.000 | 0 (0%) | [OK] 优秀 | 提取质量高 |
| 核心思想 | 0.647 | 13 (3%) | [OK] 良好 | 大部分卡片提取有效 |
| 局限性 | 0.452 | 0 (0%) | [WARN] 一般 | 部分卡片需人工审核 |
| 技术方法 | 0.602 | 18 (4%) | [OK] 良好 | 大部分卡片提取有效 |
| 评价指标 | 0.634 | 38 (9%) | [OK] 良好 | 大部分卡片提取有效 |
| 研究问题 | 0.657 | 22 (5%) | [OK] 良好 | 大部分卡片提取有效 |
| 结果摘要 | 0.670 | 14 (3%) | [OK] 良好 | 大部分卡片提取有效 |

## 4. 异常卡片与修正记录

### 4.2 批量修复记录 (共 407 张)

| arXiv ID | 标题 | 修复字段 |
|----------|------|----------|
| 2606.12078 | Deep Reinforcement Learning for Adaptive Power All... | limitations |
| 2606.11879 | On the Robustness of AFBM Sensing to Power Amplifi... | limitations |
| 2606.11665 | Quantization Limitations of Leakage Suppression in... | dataset_or_scenario, limitations |
| 2606.11449 | Coherent Multiband OFDM Sensing via Low-Complexity... | limitations |
| 2606.11351 | MJSAC: McCormick Relaxation-based Waveform Design ... | limitations |
| 2606.07900 | CellSense: A Sub-6 GHz Cellular ISAC System for Cl... | dataset_or_scenario, limitations |
| 2606.07328 | Implementation and Calibration of 3GPP-Compliant I... | limitations |
| 2606.07104 | Robust Secure Beamforming for Movable Antenna Enha... | limitations |
| 2606.07091 | Rate-Splitting--Inspired Uplink Near-Field ISAC | limitations, key_idea |
| 2606.06239 | Foundation Models for Wireless Communications: Fro... | limitations |
| 2606.05589 | 3D Spherical Fluid Antennas for Spatially Reconfig... | limitations |
| 2606.05084 | A Cancellation Mechanism in AFDM Radar Sensing: Ex... | limitations |
| 2606.05262 | X-Band UAV-enabled Integrated Sensing and Communic... | limitations |
| 2606.04698 | Adaptive $c_2$-Perturbed AFDM Waveform Design for ... | limitations |
| 2606.03960 | SNF-PRP: A Covert Integrating Sensing and Communic... | limitations |
| 2606.03690 | On Secure EKF-enhanced UAV-ISAC Systems | limitations |
| 2606.03372 | Instantaneous Risk Minimization for Secure Integra... | limitations |
| 2606.03013 | Fault-Aware Design for Reconfigurable Holographic ... | limitations |
| 2606.02077 | Integrated Sensing and Covert Communication In Low... | limitations |
| 2606.00977 | Electromagnetic Digital Twin-Enabled Closed-Loop B... | limitations |
| 2606.00360 | Ambiguity Analysis and Design of Sparse Arrays via... | limitations |
| 2605.31366 | ISAC-Enabled Grant-Free Uplink via Artificial-Path... | limitations |
| 2605.31353 | Sensing with Random Signals: The Role of Time Shar... | limitations |
| 2605.29913 | Gesture-Aware Indoor THz ISAC Systems for Adaptive... | limitations |
| 2605.28547 | On Unified CRLB Framework from Generic Signals to ... | limitations |
| 2605.28325 | ISAC Privacy: Challenges and Solutions for 6G | limitations |
| 2605.28191 | Spatiotemporal Tracking in Cooperative ISAC Networ... | limitations |
| 2605.27839 | Movable Antenna Enhanced Dual-Functional Radar-Com... | limitations |
| 2605.26915 | Gaussian Process-Based Extended Object Estimation ... | limitations |
| 2605.25593 | Time-Varying Parametric Channel Estimation With CP... | limitations |
| ... | 共 407 条修复记录 | ... |

## 5. ISAC 子类别分布

| 子类别 | 论文数 | 占比 |
|--------|--------|------|
| Waveform_Design | 92 | 22.4% |
| Standardization_and_Architecture | 68 | 16.5% |
| RIS_Metasurface_ISAC | 57 | 13.9% |
| Localization_and_Tracking | 55 | 13.4% |
| Beamforming_and_Precoding | 53 | 12.9% |
| Security_and_Privacy | 26 | 6.3% |
| Resource_Allocation | 25 | 6.1% |
| Channel_Estimation_and_CSI | 14 | 3.4% |
| Machine_Learning_for_ISAC | 11 | 2.7% |
| Full_Duplex_and_NOMA_ISAC | 10 | 2.4% |

## 6. 创新类型分布

| 创新类型 | 论文数 | 占比 |
|----------|--------|------|
| 融合整合 (integration) | 230 | 56.0% |
| 理论贡献 (theoretical_contribution) | 120 | 29.2% |
| 全新方法 (novel_approach) | 55 | 13.4% |
| 统一框架 (unified_framework) | 4 | 1.0% |
| 扩展延伸 (extension) | 1 | 0.2% |
| 增量改进 (incremental_improvement) | 1 | 0.2% |

## 7. 常见问题与改进建议

### 7.1 limitations 字段薄弱 (最主要问题)

- **原因**: 大多数学术摘要不包含明确的局限性陈述
- **已采取措施**: 从 method/problem 字段进行智能推断
- **建议**: 对重要论文，获取全文后人工补充具体局限性

### 7.2 dataset_or_scenario 字段不精确

- **原因**: 部分摘要未详细描述仿真环境和参数
- **已采取措施**: 扩展了场景关键词匹配（频段/天线/信道模型等）
- **建议**: 阅读论文章节2(系统模型)和章节5(仿真设置)

### 7.3 best_fit_category 边界模糊

- **原因**: ISAC论文常跨多个子领域，单一分类可能不准确
- **建议**: 考虑在未来版本中支持多标签分类

## 8. 输出文件

| 文件 | 说明 |
|------|------|
| `data/papers_raw.json` | 原始论文数据 (411篇) |
| `data/paper_cards.jsonl` | 最终论文卡片 (411张) |
| `data/card_validation_report.md` | 本校验报告 |

---
*报告自动生成于 2026-06-11T20:15:00.620282*