# 面向6G的通信感知一体化（ISAC）研究分类法

**生成时间**: 2026-06-11T20:19:08.486887
**论文总数**: 411
**覆盖时间**: 2024-06 至 2026-06 (近2年)

---

## 分类体系总览

本分类法将 ISAC 研究划分为 **10 个大方向**，每个大方向下设 **2-5 个子方向**，
形成两级分类体系。分类依据：论文核心研究问题、技术方法和应用场景。

| 大方向 | 论文数 | 占比 | 子方向数 |
|--------|--------|------|----------|
| 波形设计 | 92 | 22.4% | 5 |
| 标准化与系统架构 | 68 | 16.5% | 5 |
| RIS/智能超表面ISAC | 57 | 13.9% | 5 |
| 定位与跟踪 | 55 | 13.4% | 5 |
| 波束赋形与预编码 | 53 | 12.9% | 5 |
| 安全与隐私 | 26 | 6.3% | 5 |
| 资源分配 | 25 | 6.1% | 5 |
| 信道估计与CSI获取 | 14 | 3.4% | 5 |
| 机器学习驱动的ISAC | 11 | 2.7% | 5 |
| 全双工与NOMA-ISAC | 10 | 2.4% | 4 |

---

## 波形设计 (Waveform_Design)

- **论文数量**: 92 篇
- **占比**: 22.4%

### 研究目标

设计同时支持高速通信和高精度感知的统一波形，解决通信与感知在时频资源上的冲突，降低峰均比(PAPR)和带外泄露(OOBE)，提升对时延-多普勒双色散信道的鲁棒性。

### 核心技术特征

1. OFDM/OTFS/AFDM等多载波波形设计
2. 时延-多普勒域信号处理
3. 低PAPR波形优化（如DFT-s-OFDM）
4. 感知导频/前导码嵌入设计
5. 帧结构与时频资源栅格联合优化
6. 波形模糊函数分析与旁瓣抑制

### 代表性方法

OFDM感知、OTFS调制、AFDM波形、滤波器组多载波(FBMC)、GFDM等。

### 子方向细分

#### OFDM增强感知 (46 篇)

| 论文 | 创新点 |
|------|--------|
| [Coherent Multiband OFDM Sensing via Low-Complexity Gap Reconstruction](https://arxiv.org/abs/2606.11449) | This paper investigates coherent multiband orthogonal frequency division multipl... |
| [A Cancellation Mechanism in AFDM Radar Sensing: Exact Fisher Informati...](https://arxiv.org/abs/2606.05084) | We consider radar sensing with affine frequency division multiplexing (AFDM), a ... |
| [Reliable UAV Detection with ISAC](https://arxiv.org/abs/2605.23561) | Unmanned Aerial Vehicle (UAV) detection is one prominent use case of Integrated ... |
| [AFDM as a Software Upgrade of OFDM: One Firmware Patch, a New Frontier](https://arxiv.org/abs/2605.23062) | In this white paper, we summarize for the benefit of the wider research communit... |
| [α-Fair Multistatic ISAC Beamforming for Multi-User MIMO-OFDM Systems v...](https://arxiv.org/abs/2603.29717) | This paper proposes an α-fair multistatic integrated sensing and communication (... |
| ... | 共 46 篇论文 |

#### OTFS/时延-多普勒 (16 篇)

| 论文 | 创新点 |
|------|--------|
| [A Cancellation Mechanism in AFDM Radar Sensing: Exact Fisher Informati...](https://arxiv.org/abs/2606.05084) | We consider radar sensing with affine frequency division multiplexing (AFDM), a ... |
| [A Novel ISAC Waveform Based on Orthogonal Delay-Doppler Division Multi...](https://arxiv.org/abs/2602.02248) | In this work, we propose the orthogonal delay-Doppler (DD) division multiplexing... |
| [OpenISAC: An Open-Source Real-Time Experimentation Platform for OFDM-I...](https://arxiv.org/abs/2601.03535) | Integrated sensing and communication (ISAC) is envisioned to be one of the key u... |
| [Securing the Sensing Functionality in ISAC: KLD-Based Ambiguity Functi...](https://arxiv.org/abs/2512.19974) | We develop ISAC system models for the base station (BS), communication user equi... |
| [ISAC with Affine Frequency Division Multiplexing: An FMCW-Based Signal...](https://arxiv.org/abs/2511.12308) | This connection not only provides a clear physical insight into AFDM's sensing m... |
| ... | 共 16 篇论文 |

#### AFDM/仿射频分复用 (2 篇)

| 论文 | 创新点 |
|------|--------|
| [On the Robustness of AFBM Sensing to Power Amplifier Nonlinearities](https://arxiv.org/abs/2606.11879) | We investigate the impact of power amplifier (PA) nonlinearities on the sensing ... |
| [Affine Filter Bank Modulation (AFBM): A Novel 6G ISAC Waveform with Lo...](https://arxiv.org/abs/2509.05683) | We propose the affine filter bank modulation (AFBM) waveform for enhanced integr... |

#### 感知帧结构设计 (0 篇)

（当前数据集中暂无该子方向的论文）

#### 波形模糊函数优化 (0 篇)

（当前数据集中暂无该子方向的论文）

### 代表论文 (Top 3)

1. **Movable Antenna Enhanced Dual-Functional Radar-Communication: A Symbol-Level Precoding Approach** (arXiv:2605.27839)
   - 核心思想: This letter investigates a symbol-level precoder design for movable antenna (MA)-enhanced dual-functional radar-communication (DFRC) systems. To enhan...
   - 技术方法: deep reinforcement learning (DRL). Specifically...
   - 主要结果: Specifically, the twin delayed deep deterministic policy gradient (TD3) algorithm is employed in the outer layer to opti...

2. **A Multi-Objective Learning Approach for Adaptive Waveform Selection in Integrated Sensing and Communications Systems** (arXiv:2603.14017)
   - 核心思想: Integrated Sensing and Communications (ISAC) has emerged as a key enabler for sixth generation (6G) wireless systems by jointly supporting data transm...
   - 技术方法: In this paper, a multi objective learning approach for adaptive waveform selection in ISAC systems is proposed. A simula...
   - 主要结果: Machine learning models are trained to learn the mapping between network conditions and Pareto optimal waveform sets, en...

3. **OFDM Waveform Optimization for Bistatic Integrated Sensing and Communications** (arXiv:2603.08442)
   - 核心思想: This paper investigates the design of orthogonal frequency-division multiplexing (OFDM) waveforms for bistatic integrated sensing and communication (I...
   - 技术方法: Building on this insight, we formulate an OFDM waveform optimization problem to maximize the CDR subject to sensing-accu...
   - 主要结果: Our results reveal that a subcarrier is allocated for sensing if and only if its Fisher information gain exceeds the cor...

---

## 标准化与系统架构 (Standardization_and_Architecture)

- **论文数量**: 68 篇
- **占比**: 16.5%

### 研究目标

研究ISAC系统级架构设计、3GPP标准化进展、网络部署策略，以及通信-感知性能折衷的理论框架，为ISAC从理论走向标准化提供指导。

### 核心技术特征

1. 3GPP ISAC研究项目(SI)进展追踪
2. 网络架构设计（集中式/分布式/Cell-Free）
3. 通信-感知性能折衷理论框架
4. ISAC系统级仿真与评估方法
5. 多频段/多节点协同架构
6. 感知即服务(SaaS)商业模式

### 代表性方法

系统级仿真、标准化分析、架构设计、性能折衷分析、信息论方法等。

### 子方向细分

#### 3GPP标准化 (4 篇)

| 论文 | 创新点 |
|------|--------|
| [Implementation and Calibration of 3GPP-Compliant ISAC Channel Simulato...](https://arxiv.org/abs/2606.07328) | Integrated sensing and communication (ISAC) has emerged as a key technology for ... |
| [System-Level Comparison of Multimodal and In-Band mmWave Sensing for B...](https://arxiv.org/abs/2601.01033) | Integrated sensing and communication (ISAC) can reduce beam-training overhead in... |
| [A Universal Neural Receiver that Learns at the Speed of Wireless](https://arxiv.org/abs/2602.15458) | Today we design wireless networks using mathematical models that govern communic... |
| [Unconsented Sensing: A Sociotechnical Governance Framework for 6G ISAC](https://arxiv.org/abs/2605.07328) | The forthcoming deployment of 6G Integrated Sensing and Communication (ISAC) wil... |

#### 系统架构设计 (0 篇)

（当前数据集中暂无该子方向的论文）

#### 性能折衷理论 (10 篇)

| 论文 | 创新点 |
|------|--------|
| [Continuous-Aperture Array-Based ISAC Over Fading Channels](https://arxiv.org/abs/2603.03184) | A framework of continuous-aperture array (CAPA)-based integrated sensing and com... |
| [Phase-Coherent D-MIMO ISAC: Multi-Target Estimation and Spectral Effic...](https://arxiv.org/abs/2512.21953) | We investigate distributed multiple-input multiple-output (D-MIMO) integrated se... |
| [Cross-layer Integrated Sensing and Communication: A Joint Industrial a...](https://arxiv.org/abs/2505.10933) | Integrated sensing and communication (ISAC) enables radio systems to simultaneou... |
| [ISAC for AI: A Trade-off Framework Across Data Acquisition and Transfe...](https://arxiv.org/abs/2605.11915) | we derive a closed-form convergence upper bound... |
| [Detecting Unauthorized Drones with Cell-Free Integrated Sensing and Co...](https://arxiv.org/abs/2501.15227) | Integrated sensing and communication (ISAC) boosts network efficiency by using e... |
| ... | 共 10 篇论文 |

#### Cell-Free架构 (5 篇)

| 论文 | 创新点 |
|------|--------|
| [A Unified KLD Framework for Duplexity and Deployment Paradigms in Cell...](https://arxiv.org/abs/2605.25018) | This paper develops a unifying analytical framework for comparing deployment and... |
| [Cell-free ISAC for Drone Detection Considering Coverage and Age of Sen...](https://arxiv.org/abs/2512.06998) | The growing presence of unauthorized drones poses significant threats to public ... |
| [Detecting Unauthorized Drones with Cell-Free Integrated Sensing and Co...](https://arxiv.org/abs/2501.15227) | Integrated sensing and communication (ISAC) boosts network efficiency by using e... |
| [Learning-Enabled Elastic Network Topology for Distributed ISAC Service...](https://arxiv.org/abs/2512.20722) | Conventional mobile networks, including both localized cell-centric and cooperat... |
| [ASSENT: Learning-Based Association Optimization for Distributed Cell-F...](https://arxiv.org/abs/2511.09992) | Integrated Sensing and Communication (ISAC) is a key emerging 6G technology. Des... |

#### 调查与综述 (4 篇)

| 论文 | 创新点 |
|------|--------|
| [Agentic Graph Neural Networks for Wireless Communications and Networki...](https://arxiv.org/abs/2508.08620) | The rapid advancement of communication technologies has driven the evolution of ... |
| [The Role of ISAC in 6G Networks: Enabling Next-Generation Wireless Sys...](https://arxiv.org/abs/2510.04413) | The commencement of the sixth-generation (6G) wireless networks represents a fun... |
| [Path to Diversity: A Primer on ISAC-izing Commodity Wi-Fi for Practica...](https://arxiv.org/abs/2601.12980) | Integrated Sensing and Communication (ISAC) has emerged as a key paradigm in nex... |
| [AI-Native Integrated Sensing and Communications for Self-Organizing Wi...](https://arxiv.org/abs/2601.02398) | Integrated Sensing and Communications (ISAC) is emerging as a foundational parad... |

### 代表论文 (Top 3)

1. **Cooperative Multi-Satellite ISAC Networks: Centralized vs. Distributed Sensing** (arXiv:2603.07622)
   - 核心思想: This paper investigates a downlink multi-satellite integrated sensing and communication (ISAC) network, in which multiple satellites simultaneously tr...
   - 技术方法: In the centralized framework, each gateway forwards its sensing observations to a central unit (CU), where the positions...
   - 主要结果: The final target positions are then obtained by minimizing the distance estimation error. Simulation results demonstrate...

2. **Continuous-Aperture Array-Based ISAC Over Fading Channels** (arXiv:2603.03184)
   - 核心思想: A framework of continuous-aperture array (CAPA)-based integrated sensing and communications (ISAC) under a fading communication channel is proposed. A...
   - 技术方法: On this basis, the performance of the CAPA-based ISAC system is analyzed by considering three continuous beamforming des...
   - 主要结果: For the Pareto-optimal design, the Pareto-optimal beamformer achieving the Pareto boundary is derived, and the achievabl...

3. **ISAC-over-NTN: HAPS-UAV Framework for Post-Disaster Responsive 6G Networks** (arXiv:2601.15422)
   - 核心思想: In disaster scenarios, ensuring both reliable communication and situational awareness becomes a critical challenge due to the partial or complete coll...
   - 技术方法: We aim to achieve two main objectives: i) provide a reliable communication infrastructure, thereby ensuring the continui...
   - 主要结果: We employ an innovative beamforming method that simultaneously transmits data and detects Doppler-based mobility by inte...

---

## RIS/智能超表面ISAC (RIS_Metasurface_ISAC)

- **论文数量**: 57 篇
- **占比**: 13.9%

### 研究目标

利用可重构智能表面(RIS/IRS)主动调控无线传播环境，增强ISAC系统的覆盖范围、感知分辨率和通信容量，尤其在遮挡和NLoS场景下。

### 核心技术特征

1. RIS相位优化（被动波束赋形）
2. 联合有源-无源波束赋形
3. STAR-RIS（同时透射反射RIS）实现全空间覆盖
4. RIS辅助感知增强（虚拟视距路径）
5. 全息RIS/动态超表面
6. RIS级联信道估计与配置

### 代表性方法

交替优化、半定松弛(SDR)、梯度下降、智能优化算法、深度展开等。

### 子方向细分

#### RIS被动波束赋形 (0 篇)

（当前数据集中暂无该子方向的论文）

#### STAR-RIS全空间ISAC (5 篇)

| 论文 | 创新点 |
|------|--------|
| [Secure and Robust Beamforming Design for STAR-RIS-aided MU-MIMO ISAC S...](https://arxiv.org/abs/2603.07719) | This formulation jointly designs the active transmit beamforming at the BS and t... |
| [Joint beamforming and mode optimization for multi-functional STAR-RIS-...](https://arxiv.org/abs/2602.16383) | This paper investigates the design of integrated sensing and communication (ISAC... |
| [Fairness-Aware Secure Communication in ISAC Systems with STAR-RIS and ...](https://arxiv.org/abs/2511.00721) | In this paper, we investigate the integration of simultaneously transmitting and... |
| [Multiple Active STAR-RIS-Assisted Secure Integrated Sensing and Commun...](https://arxiv.org/abs/2507.18035) | This paper explores an integrated sensing and communication (ISAC) network empow... |
| [STAR-RIS-Enabled Full-Duplex Integrated Sensing and Communication Syst...](https://arxiv.org/abs/2410.18767) | The optimization of maximizing the sensing signal-to-interference-plus-noise rat... |

#### RIS辅助感知增强 (0 篇)

（当前数据集中暂无该子方向的论文）

#### 全息RIS (0 篇)

（当前数据集中暂无该子方向的论文）

#### RIS信道估计 (0 篇)

（当前数据集中暂无该子方向的论文）

### 代表论文 (Top 3)

1. **RIS-Aided Sensing: Experimental Validation of Radar 3D Imaging in the mmWave Band** (arXiv:2604.12466)
   - 核心思想: The transition toward 6G networks demands energy-efficient hardware capable of active interaction with the environment. Reconfigurable Intelligent Sur...
   - 技术方法: However, achieving targeted 3D spatial mapping in a fully autonomous, closed-loop system remains a significant challenge...
   - 主要结果: We experimentally validate the system through three diverse scenarios, including metallic mannequins, calibration sphere...

2. **Bistatic Integrated Sensing and Communication in the Presence of a Disco Reconfigurable Intelligent Surface: Disruption, Enhancement, or Both?** (arXiv:2604.10120)
   - 核心思想: To quantify the impact of the DRIS on the bistatic ISAC system, we derive the statistical characteristics of DRIS-induced active channel aging (ACA) c...
   - 技术方法: Then, an ISAC waveform design that balances sensing and communication performance is proposed by formulating a Pareto op...
   - 主要结果: In contrast, with respect to sensing performance, the DRIS decreases the estimation accuracy of the angle of departure (...

3. **Reconfigurable Intelligent Surfaces-assisted Positioning in Integrated Sensing and Communication Systems** (arXiv:2602.14415)
   - 核心思想: This paper investigates the problem of high-precision target localization in integrated sensing and communication (ISAC) systems, where the target is ...
   - 技术方法: To solve this efficiently, we introduce a fast iterative refinement algorithm tailored for RIS-aided ISAC environments. ...
   - 主要结果: Furthermore, we propose a modified Levenberg algorithm with an approximation strategy, which enables low-cost parameter ...

---

## 定位与跟踪 (Localization_and_Tracking)

- **论文数量**: 55 篇
- **占比**: 13.4%

### 研究目标

利用ISAC系统的通信信号实现高精度目标定位与跟踪，研究感知参数估计的理论极限（CRB），设计多站/分布式协同定位方案。

### 核心技术特征

1. CRB/CRLB理论性能界分析
2. 多基站/多站协同定位
3. 近场球面波前定位
4. 基于EKF/粒子滤波的目标跟踪
5. 多目标检测与数据关联
6. UAV/移动平台辅助定位

### 代表性方法

最大似然估计(MLE)、CRB推导、EKF、粒子滤波、TDoA/DoA融合等。

### 子方向细分

#### CRB理论分析 (18 篇)

| 论文 | 创新点 |
|------|--------|
| [Fault-Aware Design for Reconfigurable Holographic Surface-Aided ISAC S...](https://arxiv.org/abs/2606.03013) | Reconfigurable holographic surface (RHS)-aided integrated sensing and communicat... |
| [Curriculum-Guided Heterogeneous Multi-Agent Intelligence for Multi-UAV...](https://arxiv.org/abs/2605.17905) | this paper proposes a multi-UAV cooperative ISAC system that enables heterogeneo... |
| [Joint Mobile User Positioning and Passive Target Sensing using Optimiz...](https://arxiv.org/abs/2605.15808) | Integrated sensing and communication (ISAC) relies on monostatic sensing (MS) an... |
| [Sensing-Assisted Secure Communication in MA-Aided ISAC: CRB Analysis a...](https://arxiv.org/abs/2604.23663) | To manage the end-to-end design, we formulate a joint optimization problem. This... |
| [CRLB Minimization for ISAC Systems with Segmented Waveguide-Enabled Pi...](https://arxiv.org/abs/2604.00572) | Pinching-antenna (PA) has recently attracted considerable research attention in ... |
| ... | 共 18 篇论文 |

#### 多站协同定位 (0 篇)

（当前数据集中暂无该子方向的论文）

#### 近场定位 (0 篇)

（当前数据集中暂无该子方向的论文）

#### 目标跟踪 (0 篇)

（当前数据集中暂无该子方向的论文）

#### UAV辅助定位 (3 篇)

| 论文 | 创新点 |
|------|--------|
| [Curriculum-Guided Heterogeneous Multi-Agent Intelligence for Multi-UAV...](https://arxiv.org/abs/2605.17905) | this paper proposes a multi-UAV cooperative ISAC system that enables heterogeneo... |
| [Clutter-Resilient ISAC for Low-Altitude Wireless Networks: A 5G Base S...](https://arxiv.org/abs/2603.14351) | Integrated sensing and communications (ISAC) has been envisioned as a promising ... |
| [Evaluation of gNB Monostatic Sensing for UAV Use Case](https://arxiv.org/abs/2604.02205) | 3GPP Release 19 has initiated the standardization of integrated sensing and comm... |

### 代表论文 (Top 3)

1. **Curriculum-Guided Heterogeneous Multi-Agent Intelligence for Multi-UAV Cooperative ISAC** (arXiv:2605.17905)
   - 核心思想: this paper proposes a multi-UAV cooperative ISAC system that enables heterogeneous-agent collaboration between multiple UAVs and a ground base station...
   - 技术方法: In contrast, this paper proposes a multi-UAV cooperative ISAC system that enables heterogeneous-agent collaboration betw...
   - 主要结果: To tackle the NP-hard nature of this problem, we design a curriculum-based heterogeneous-agent proximal policy optimizat...

2. **CRLB Minimization for ISAC Systems with Segmented Waveguide-Enabled Pinching Antenna** (arXiv:2604.00572)
   - 核心思想: Pinching-antenna (PA) has recently attracted considerable research attention in wireless systems, realized by attaching small dielectric particles alo...
   - 技术方法: In this work, SWAN-assisted integrated sensing and communication (ISAC) is investigated, where a base station (BS) equip...
   - 主要结果: A penalty method combined with Riemannian Broyden-Fletcher-Goldfarb-Shanno (RBFGS) algorithm is applied to obtain a feas...

3. **Cooperative ISAC for Joint Localization and Velocity Estimation in Cell-Free MIMO Systems** (arXiv:2602.20319)
   - 核心思想: The CPU then aggregates the information from all APs to estimate the location and velocity of the targets. We develop a distributed vector-quantized v...
   - 技术方法: It effectively reduces the amount of data transmitted from each AP to the CPU while maintaining a high sensing accuracy....
   - 主要结果: We employ a collaborative learning-assisted scheme to train D-VQVAE in an end-to-end manner. Simulation results show tha...

---

## 波束赋形与预编码 (Beamforming_and_Precoding)

- **论文数量**: 53 篇
- **占比**: 12.9%

### 研究目标

优化多天线系统的空间自由度，在保证通信速率的同时提升感知分辨率，设计统一的波束赋形/预编码方案以平衡通信容量与感知精度（如CRB最小化）。

### 核心技术特征

1. 混合数字-模拟波束赋形架构
2. 通信-感知联合波束赋形优化
3. 基于CRB/MI的感知波束设计
4. 可移动/流体天线波束管理
5. 全息MIMO/超大规模MIMO波束赋形
6. 码本设计与波束训练

### 代表性方法

混合波束赋形、全数字预编码、码本波束训练、自适应波束管理、流体天线等。

### 子方向细分

#### 混合数字-模拟波束赋形 (0 篇)

（当前数据集中暂无该子方向的论文）

#### 联合波束赋形优化 (4 篇)

| 论文 | 创新点 |
|------|--------|
| [Multi-User ISAC with Heterogeneous Unknown Parameters: Optimal Beamfor...](https://arxiv.org/abs/2604.22392) | This paper studies an integrated sensing and communication (ISAC) system where a... |
| [Optimal Transmit Beamforming for MIMO ISAC with Unknown Target and Use...](https://arxiv.org/abs/2602.08255) | This paper studies a challenging scenario in a multiple-input multiple-output (M... |
| [Pinching Antenna Systems for Integrated Sensing and Communications](https://arxiv.org/abs/2508.19540) | Recently, the pinching antenna system (PASS) has attracted considerable attentio... |
| [Integrated Sensing and Semantic Communication with Adaptive Source-Cha...](https://arxiv.org/abs/2601.12827) | However, most of the existing works mainly focus on sensing data compression to ... |

#### 可移动天线ISAC (0 篇)

（当前数据集中暂无该子方向的论文）

#### 全息MIMO波束赋形 (0 篇)

（当前数据集中暂无该子方向的论文）

#### 码本与波束训练 (0 篇)

（当前数据集中暂无该子方向的论文）

### 代表论文 (Top 3)

1. **Movable-Antenna-Enhanced ISAC: Optimal Antenna Trajectory and Beamforming Design** (arXiv:2605.23427)
   - 核心思想: To this end, this paper investigates a dynamic MA-enabled ISAC system and studies the joint design of MA trajectories and transmit beamforming. We for...
   - 技术方法: Movable antenna (MA) technology introduces additional spatial degrees of freedom through antenna mobility, yet existing ...
   - 主要结果: A branch-and-bound-based algorithm is developed to obtain the globally optimal solution. Numerical results show that the...

2. **DL-Driven Optimization for ISAC System Equipped With Pinching and Movable Antennas** (arXiv:2605.17629)
   - 核心思想: For these other variables (i.e., the positions of the transmit PAs, the positions of the users' MAs, the communication precoding matrices, and the sen...
   - 技术方法: Therefore, our goal is to study the optimization of the sum-rate for an ISAC system equipped with PAs and MAs, capable o...
   - 主要结果: To train the network in an unsupervised manner, we formulate a loss function consisting of the objective function, as we...

3. **Multi-AP Cooperative Beamforming for Cell-Free ISAC Networks: Balancing Communication SINR and Sensing SCNR** (arXiv:2605.04623)
   - 核心思想: Cell-free integrated sensing and communication (ISAC) systems are facing the resource allocation challenges due to the deployment of access points (AP...
   - 技术方法: Unlike traditional ISAC architectures, the geographic distribution of APs introduces coordination complexity and resourc...
   - 主要结果: The non-convex quadratically constrained quadratic program is transformed into a tractable convex semidefinite program v...

---

## 安全与隐私 (Security_and_Privacy)

- **论文数量**: 26 篇
- **占比**: 6.3%

### 研究目标

在ISAC系统中保障通信信息安全和感知数据隐私，防御窃听、干扰等攻击，同时避免感知功能泄露用户隐私信息。

### 核心技术特征

1. 物理层安全（保密速率最大化）
2. 隐蔽通信/感知（low probability of detection）
3. ISAC辅助的安全传输（感知辅助波束赋形防窃听）
4. 差分隐私保护感知数据
5. 抗干扰/抗欺骗攻击
6. 区块链/可信计算用于感知数据管理

### 代表性方法

人工噪声、AN辅助波束赋形、隐蔽传输、保密速率优化、博弈论等。

### 子方向细分

#### 物理层安全传输 (0 篇)

（当前数据集中暂无该子方向的论文）

#### 隐蔽ISAC (2 篇)

| 论文 | 创新点 |
|------|--------|
| [SNF-PRP: A Covert Integrating Sensing and Communications Framework](https://arxiv.org/abs/2606.03960) | Existing physical layer security approaches mitigate interception yet operate wi... |
| [Integrated Sensing and Covert Communication In Low-Altitude Networks: ...](https://arxiv.org/abs/2606.02077) | Nevertheless, the complexity and dynamics of urban environments pose critical ch... |

#### 感知辅助安全 (0 篇)

（当前数据集中暂无该子方向的论文）

#### 隐私保护 (0 篇)

（当前数据集中暂无该子方向的论文）

#### 抗干扰攻击 (0 篇)

（当前数据集中暂无该子方向的论文）

### 代表论文 (Top 3)

1. **Secure Transmission for Fluid Antenna-Aided ISAC Systems** (arXiv:2602.23241)
   - 核心思想: However, the scenario where sensing targets act as eavesdroppers in ISAC and how to maximize the sum secrecy rate has not been addressed. This letter ...
   - 技术方法: We jointly optimize antenna position vector (APV) and beamforming to maximize the multiuser sum secrecy rate, which comp...
   - 主要结果: To solve the resulting non-convex problem, we use a block successive upper-bound minimization (BSUM) algorithm, which in...

2. **Dual Security for MIMO-OFDM ISAC Systems: Artificial Ghosts or Artificial Noise** (arXiv:2602.20045)
   - 核心思想: Despite these risks, the joint protection of sensing and communication security in ISAC systems remains unexplored. To address this challenge, this pa...
   - 技术方法: Despite these risks, the joint protection of sensing and communication security in ISAC systems remains unexplored. To a...
   - 主要结果: Legitimate receivers can suppress these AGs, whereas sensing Eves cannot, thereby significantly reducing their probabili...

3. **Secure Cell-Free Massive MIMO ISAC Systems: Joint AP Selection and Power Allocation Against Eavesdropping** (arXiv:2603.18635)
   - 核心思想: This paper investigates a cell-free massive multiple-input-multiple-output (CF-mMIMO) integrated sensing and communication (ISAC) system that addresse...
   - 技术方法: Closed-form expressions for the achievable communication rate, eavesdropping rate, and mainlobe-to-average-sidelobe rati...
   - 主要结果: The proposed joint optimization framework determines the optimal AP operational modes and power allocation across commun...

---

## 资源分配 (Resource_Allocation)

- **论文数量**: 25 篇
- **占比**: 6.1%

### 研究目标

在通信与感知功能之间高效分配有限的无线资源（功率、频谱、时间、空间），实现通信吞吐量与感知精度之间的最优折衷。

### 核心技术特征

1. 功率分配优化（注水算法、凸优化）
2. 频谱共享与子载波分配
3. 时域资源划分（TDD/FDD感知通信切换）
4. 多目标/多用户资源调度
5. 能效最大化资源分配
6. 深度强化学习驱动的自适应资源管理

### 代表性方法

凸优化、博弈论、DRL资源分配、Lyapunov优化、匹配理论等。

### 子方向细分

#### 功率分配优化 (0 篇)

（当前数据集中暂无该子方向的论文）

#### 频谱共享与接入 (0 篇)

（当前数据集中暂无该子方向的论文）

#### 时域资源调度 (0 篇)

（当前数据集中暂无该子方向的论文）

#### 多目标资源管理 (0 篇)

（当前数据集中暂无该子方向的论文）

#### 能效优化 (0 篇)

（当前数据集中暂无该子方向的论文）

### 代表论文 (Top 3)

1. **Energy Efficiency Maximization for Integrated Sensing and Communications in Satellite-UAV MIMO Systems** (arXiv:2603.01717)
   - 核心思想: This paper investigates energy efficiency maximization in an integrated sensing and communication framework for satellite-UAV MIMO systems, where a LE...
   - 技术方法: We derive the achievable downlink throughput by considering that the high-altitude satellite maintains a line-of-sight (...
   - 主要结果: To tackle this challenge, we propose an efficient alternating optimization algorithm capable of handling the complex sea...

2. **Digital Twin-Assisted Task Offloading and Resource Allocation in ISAC-Enabled Internet of Vehicles** (arXiv:2511.05789)
   - 核心思想: The convergence of the Internet of vehicles (IoV) and 6G networks is driving the evolution of next-generation intelligent transportation systems. Howe...
   - 技术方法: The objective is to minimize the long-term average system cost, defined as a weighted combination of delay and energy co...
   - 主要结果: Building upon this, we propose a Lyapunov-driven DT-enhanced multi-agent proximal policy optimization (Ly-DTMPPO) algori...

---

## 信道估计与CSI获取 (Channel_Estimation_and_CSI)

- **论文数量**: 14 篇
- **占比**: 3.4%

### 研究目标

在ISAC系统中高效获取通信信道与感知目标参数，利用通信-感知互惠性降低导频开销，提升信道估计精度以支撑高可靠通信和高精度感知。

### 核心技术特征

1. 压缩感知/稀疏信道估计
2. 通信-感知信道互惠性利用
3. 基于AI的信道估计（CNN/Transformer）
4. 导频设计与优化
5. 感知辅助信道预测
6. 超分辨率参数估计

### 代表性方法

压缩感知、深度信道估计、超分辨率、贝叶斯推断、子空间方法等。

### 子方向细分

#### 压缩感知估计 (6 篇)

| 论文 | 创新点 |
|------|--------|
| [Time-Varying Parametric Channel Estimation With CP Decomposition Tenso...](https://arxiv.org/abs/2605.25593) | Integrated sensing and communications (ISAC) is a key use case for sixth-generat... |
| [Environment-Aware Near-Field Channel Estimation Leveraging CKM and ISA...](https://arxiv.org/abs/2604.04031) | This paper proposes an environment-aware near-field channel estimation framework... |
| [CSIYOLO: An Intelligent CSI-based Scatter Sensing Framework for Integr...](https://arxiv.org/abs/2509.19335) | ISAC is regarded as a promising technology for next-generation communication sys... |
| [Low-Complexity Channel Estimation in OTFS Systems with Fractional Effe...](https://arxiv.org/abs/2505.06248) | Orthogonal Time Frequency Space (OTFS) modulation exploits the sparsity of Delay... |
| [ISAC Imaging by Channel State Information using Ray Tracing for Next G...](https://arxiv.org/abs/2509.06672) | Integrated sensing and communications (ISAC) is emerging as a cornerstone techno... |
| ... | 共 6 篇论文 |

#### AI信道估计 (1 篇)

| 论文 | 创新点 |
|------|--------|
| [Conditional Denoising Diffusion for ISAC Enhanced Channel Estimation i...](https://arxiv.org/abs/2506.06942) | Channel estimation is a critical step in cell-free ISAC systems to ensure reliab... |

#### 导频优化设计 (0 篇)

（当前数据集中暂无该子方向的论文）

#### 互惠性利用 (0 篇)

（当前数据集中暂无该子方向的论文）

#### 参数化估计 (1 篇)

| 论文 | 创新点 |
|------|--------|
| [Time-Varying Parametric Channel Estimation With CP Decomposition Tenso...](https://arxiv.org/abs/2605.25593) | Integrated sensing and communications (ISAC) is a key use case for sixth-generat... |

### 代表论文 (Top 3)

1. **Conditional Denoising Diffusion for ISAC Enhanced Channel Estimation in Cell-Free 6G** (arXiv:2506.06942)
   - 核心思想: Channel estimation is a critical step in cell-free ISAC systems to ensure reliable communication, but its performance is usually limited by challenges...
   - 技术方法: Channel estimation is a critical step in cell-free ISAC systems to ensure reliable communication, but its performance is...
   - 主要结果: As compared with Least Squares (LS) and Minimum Mean Squared Error (MMSE) estimators, the proposed model achieves normal...

---

## 机器学习驱动的ISAC (Machine_Learning_for_ISAC)

- **论文数量**: 11 篇
- **占比**: 2.7%

### 研究目标

利用深度学习、强化学习等AI技术解决ISAC中的非凸优化、实时决策和复杂环境适应问题，突破传统模型驱动方法的性能瓶颈。

### 核心技术特征

1. 深度强化学习用于资源分配与波束管理
2. 图神经网络用于分布式ISAC协调
3. Transformer/扩散模型用于感知信号处理
4. 联邦学习保护感知数据隐私
5. 迁移学习提升模型泛化能力
6. 基础模型(foundation model)用于多任务ISAC

### 代表性方法

深度强化学习(DRL)、图神经网络(GNN)、Transformer、扩散模型、联邦学习等。

### 子方向细分

#### 深度强化学习ISAC (3 篇)

| 论文 | 创新点 |
|------|--------|
| [Digital Twin-assisted belief-state reinforcement learning for latency-...](https://arxiv.org/abs/2604.25967) | Integrated Sensing and Communication (ISAC) enables joint data transmission and ... |
| [Set Transformer-Based Beamforming Design for Cell-Free Integrated Sens...](https://arxiv.org/abs/2603.23618) | Existing cell-free integrated sensing and communication (CF-ISAC) beamforming al... |
| [A Survey on AI for 6G: Challenges and Opportunities](https://arxiv.org/abs/2604.02370) | As wireless communication evolves, each generation of networks brings new techno... |

#### 图神经网络 (0 篇)

（当前数据集中暂无该子方向的论文）

#### 联邦学习与隐私 (0 篇)

（当前数据集中暂无该子方向的论文）

#### Transformer/基础模型 (2 篇)

| 论文 | 创新点 |
|------|--------|
| [Set Transformer-Based Beamforming Design for Cell-Free Integrated Sens...](https://arxiv.org/abs/2603.23618) | Existing cell-free integrated sensing and communication (CF-ISAC) beamforming al... |
| [Distributed Optimization-Learning with Graph Transformers for Terahert...](https://arxiv.org/abs/2604.09981) | we propose a distributed optimization-learning framework... |

#### 扩散模型应用 (0 篇)

（当前数据集中暂无该子方向的论文）

### 代表论文 (Top 3)

1. **Diffusion Model-Enhanced Environment Reconstruction in ISAC** (arXiv:2511.19044)
   - 核心思想: Recently, environment reconstruction (ER) in integrated sensing and communication (ISAC) systems has emerged as a promising approach for achieving hig...
   - 技术方法: To address this problem, we propose a noise-sparsity-aware diffusion model (NSADM) post-processing framework. Leveraging...
   - 主要结果: Leveraging the powerful data recovery capabilities of diffusion models, the proposed scheme exploits spatial features an...

---

## 全双工与NOMA-ISAC (Full_Duplex_and_NOMA_ISAC)

- **论文数量**: 10 篇
- **占比**: 2.4%

### 研究目标

利用全双工(FD)同时收发和NOMA多用户接入技术提升ISAC系统的频谱效率和用户容量，解决自干扰消除和多用户干扰管理问题。

### 核心技术特征

1. 全双工自干扰消除（模拟/数字域）
2. NOMA功率域/码域多用户接入
3. 速率分割多址(RSMA)增强ISAC
4. 全双工感知-通信一体化
5. 多用户干扰管理与SIC

### 代表性方法

自干扰消除、SIC、功率域NOMA、RSMA、全双工波束赋形等。

### 子方向细分

#### 全双工自干扰消除 (1 篇)

| 论文 | 创新点 |
|------|--------|
| [Rate-Splitting--Inspired Uplink Near-Field ISAC](https://arxiv.org/abs/2606.07091) | This paper develops a rate-splitting (RS)-inspired framework for uplink near-fie... |

#### NOMA功率分配 (7 篇)

| 论文 | 创新点 |
|------|--------|
| [Rate-Splitting--Inspired Uplink Near-Field ISAC](https://arxiv.org/abs/2606.07091) | This paper develops a rate-splitting (RS)-inspired framework for uplink near-fie... |
| [Holographic MIMO Empowered NOMA-ISAC for 6G: Rate-Splitting Enhanced N...](https://arxiv.org/abs/2512.19699) | Holographic multiple-input multiple-output (MIMO) systems with extremely large a... |
| [Performance Analysis of NOMA-Assisted Optical OFDM ISAC Systems with C...](https://arxiv.org/abs/2511.02282) | This paper studies the performance of optical orthogonal frequency-division mult... |
| [Unveiling the Potential of NOMA: A Journey to Next Generation Multiple...](https://arxiv.org/abs/2412.17160) | Revolutionary sixth-generation wireless communications technologies and applicat... |
| [Performance Analysis of FAS-Aided NOMA-ISAC: A Backscattering Scenario](https://arxiv.org/abs/2408.04724) | This paper investigates a two-user downlink system for integrated sensing and co... |
| ... | 共 7 篇论文 |

#### RSMA-ISAC (1 篇)

| 论文 | 创新点 |
|------|--------|
| [Holographic MIMO Empowered NOMA-ISAC for 6G: Rate-Splitting Enhanced N...](https://arxiv.org/abs/2512.19699) | Holographic multiple-input multiple-output (MIMO) systems with extremely large a... |

#### 全双工波束赋形 (0 篇)

（当前数据集中暂无该子方向的论文）

### 代表论文 (Top 3)

1. **Rate-Splitting--Inspired Uplink Near-Field ISAC** (arXiv:2606.07091)
   - 核心思想: This paper develops a rate-splitting (RS)-inspired framework for uplink near-field ISAC. The...
   - 技术方法: Closed-form expressions are derived for the communication-rate (CR) and sensing-rate (SR), accounting for residual sensi...
   - 主要结果: Using an aperture-aware near-field channel model, large-array limits are derived, showing that achievable rates remain f...

2. **Holographic MIMO Empowered NOMA-ISAC for 6G: Rate-Splitting Enhanced Near-Field Modeling, Multi-Objective Optimization, and Statistical Performance Validation** (arXiv:2512.19699)
   - 核心思想: Holographic multiple-input multiple-output (MIMO) systems with extremely large apertures enable transformational capabilities for sixth-generation (6G...
   - 技术方法: This paper presents a comprehensive holographic MIMO NOMA-ISAC framework featuring: Unified near-field modeling incorpor...
   - 主要结果: Sensing CRLB improvements of \decibel are confirmed with 99\% statistical confidence. The framework establishes rigorous...

3. **Resilient Full-Duplex ISAC in the Face of Imperfect SI Cancellation: Globally Optimal Timeslot Allocation and Beam Selection** (arXiv:2510.15810)
   - 核心思想: The joint design leads to a semi-infinite, nonconvex mixed-integer nonlinear program (MINLP), which is difficult to solve. To overcome this, we develo...
   - 技术方法: Timeslot allocation governs the distribution of discrete channel uses between sensing and communication tasks, while bea...
   - 主要结果: To overcome this, we develop a tailored reformulation strategy that transforms the problem into a tractable mixed-intege...

---

## 分类合理性说明

### 分类原则

1. **研究问题驱动**: 以论文的核心研究问题作为一级分类标准，区别于纯技术堆叠
2. **技术方法辅助**: 在一级分类内按技术路线细分子方向，如优化方法 vs AI方法
3. **应用场景参考**: 结合目标部署场景（地面/空中/水下/太空）作为补充维度
4. **可扩展性**: 两级体系预留扩展空间，新技术方向可作为新子方向插入

### 分类验证

- **N=411篇论文全部分配至10个方向**, 无遗漏
- **分类互斥性**: 每篇论文按主要贡献分配至最匹配的方向
- **子方向覆盖**: 10个大方向下设共 49 个子方向
- **知识驱动**: 分类节点由ISAC领域知识定义, 非纯数据驱动聚类

---
*分类法由 ISAC 文献分析系统自动生成, 基于领域知识增强*
*生成时间: 2026-06-11T20:19:08.490898*