# 知识网 v0 · 外部来源

来源：INFERRED（人工整理；概念取自外部教材/课程，重要度、分簇及依赖边是编者判断）。获取日期均为 **2026-10-28**（运行环境 `date -I`）。本版只交付概念层；“两者”表示该来源以后也能提供情景，不表示已建情景。

## 来源清单

| 代号 / 名称 | URL | 获取日期 | 覆盖层 | 可贡献的结构 | 可信度与理由 | 本次核验 |
|---|---|---|---|---|---|---|
| DL · Goodfellow, Bengio & Courville, *Deep Learning* (2016) | https://www.deeplearningbook.org/ | 2026-10-28 | 两者 | 编号教材目录：ch.2 线代、3 概率、5 ML、6 前馈、7 正则、8 优化、9 CNN、10 序列、11 实践、15 表示学习；习题可供后续情景 | high：作者官方站、MIT Press 教材、固定章节；与 D2L 交叉覆盖，但不覆盖现代 LLM | HTTP 200，5943 bytes；页面含 Table of Contents 与章节链接；未逐章全文核验 |
| D2L · Zhang et al., *Dive into Deep Learning* 1.0.3 | https://d2l.ai/ | 2026-10-28 | 两者 | 可抓到章节/小节树：2 数学、3–5 基础、7–11 架构、12 优化、13 性能、14 视觉、15–16 NLP、17 RL、19 超参；示例与习题可供情景 | high：作者维护、Cambridge University Press 教材，结构编号细，含实现；版本变动时需复核章节号 | HTTP 200，188475 bytes；实际读取 2.1–23.8 目录，含 11.3 Attention Scoring Functions、13.7 Parameter Servers 等 |
| CS229 · Stanford Machine Learning，Summer 2026 主页 | https://cs229.stanford.edu/ | 2026-10-28 | 概念 | Course Description 的监督/无监督、学习理论、强化学习四块，以及 Prerequisites；用于主干覆盖交叉检查，当前不作为细粒度节点的主出处 | high（课程身份）；medium（当前页面粒度）：大学官方课程，但主页描述不能证明具体先修边 | HTTP 200，17701 bytes；原 https://cs229.stanford.edu/syllabus.html 返回 404，已降级到主页结构，未声称抓到详细 syllabus |
| CS224N · Stanford NLP with Deep Learning，Winter 2026 | https://web.stanford.edu/class/cs224n/#schedule | 2026-10-28 | 两者 | Schedule 的 Word Vectors、Transformers、Pretraining、Post-training (RLHF/SFT/DPO)、PEFT、Agents/Tool Use/RAG、Benchmarking、Reasoning；每讲列论文标题，作业可供后续情景 | high（官方课程）；节点 confidence=medium：能核验讲题与指定论文，不等于全文细节已经审计 | HTTP 200，63891 bytes；读到课程日程和阅读标题，包括 LoRA、Speculative Decoding、Self-Consistency |
| CS231n · Stanford Deep Learning for Computer Vision，Spring 2026 | https://cs231n.stanford.edu/schedule.html | 2026-10-28 | 两者 | Lecture 1–18：分类、CNN、注意力、检测/分割、分布式训练、自监督、VAE/GAN、Diffusion；作业入口可供情景 | high（官方课程）；节点 confidence=medium：细术语在日程条目中，但本次未读全部课件 | HTTP 200，25813 bytes；读到 Lecture 11 Utilization/Parallelism/Activation Checkpointing、12 Contrastive learning、13 VAE/GAN、14 Diffusion |
| RL · Sutton & Barto, *Reinforcement Learning: An Introduction*, 2nd edition (2018) | http://incompleteideas.net/book/the-book-2nd.html ; PDF: http://incompleteideas.net/book/RLbook2020.pdf | 2026-10-28 | 两者 | 第二版编号章节：2 bandit、3 MDP、4 DP、5 Monte Carlo、6 TD、13 policy gradient；例题可供情景 | high（作者官方书）；本版节点 confidence=medium：链接真实，但章节定位仍 verify_pending，不能把记忆当成本次实读 | 官方书页 HTTP 200，1909 bytes，含 Second Edition、Full Pdf 链接；PDF 下载超时，目录内容 verify_pending；MDP/value iteration/Q-learning 另与已抓到的 D2L ch.17 交叉覆盖 |
| SYS · Stanford CS329S Machine Learning Systems Design，公开旧版日程 | https://stanford-cs329s.github.io/syllabus.html | 2026-10-28 | 两者 | Training Data、Feature engineering、Offline evaluation、Deployment、Monitoring、Experiment tracking & versioning、ML Infrastructure；附 Booking.com、Stitch Fix 等案例链接可供后续情景 | high（课程来源）；medium（目录级节点）；low（不可达子材料的细术语）：有讲义/课件链接，但老课程并非现代 LLM serving 手册 | HTTP 200，16053 bytes；读取完整日程。Google Docs/Slides 导出不可达（Network is unreachable）；依赖这些子材料的细术语统一在节点 note 标 verify_pending、confidence=low |

## 引用与依赖边的边界

- `concepts.yaml` 的 `source.ref` 是可点击 URL + 章节/讲题/阅读标题，不用含糊的书名占位。DL/D2L 的编号以本表版本为准。课程引用中的 `reading` 是日程列出的论文，不冒充已下载论文全文。
- 来源支持“这个概念有外部锚点”；`requires` 是编者按理解机制所需知识挑选的**稀疏、非穷尽直接先修**，并非教材目录顺序的机械转抄，也不是外部来源已逐边证明。只保留机制上的依赖，不把关联、实现选型、常见搭配当成硬先修；根节点可以无前置。依赖边尚需 WP-7 抽样审计。
- 同一概念由 `anchors.yaml` 的固定 ID 连接中英文名称；锚点 `name` 保留来源通用英文规范名，概念 `name` 为中文展示名。不靠字符串相似度合并，缩写有歧义时不登记（例如 RL 不同时代表 representation learning）。
- `importance` 是 v0 诊断覆盖优先级，非来源原文评级。每簇前五个主干节点为 high，其余暂为 medium；不是说其余节点不重要。
- `source.type=model` 仅用于没有可追溯外部概念出处的模型补洞；本次为 0。外部出处有链接但材料尚未核验，保留其真实来源类型，降低 confidence 并写 verify_pending，不伪装成已核验。不要把“0 model”读成“所有细节均已外部证实”。

## 抓取失败与降级

- CS229 旧 syllabus 路径 404 → 只用官方主页可见主题，不据此编造细粒度 syllabus。
- Hugging Face LLM Course 主站网络不可达；GitHub raw `_toctree.yml` 连接重置 → 未纳入来源，也未据此登记节点；现代 NLP 改用实际可读的 CS224N 日程。
- Sutton PDF 超时 → 保留官方入口与已知第二版章节引用，逐节点标 verify_pending，不能声称已读 PDF。
- CS329S 三份材料导出（Offline evaluation / Deployment / Infrastructure）均网络不可达 → 仅目录已验证；具体材料的待核验定位见下表，节点不把它们当高置信依据。

| CS329S 目录讲题 | 日程实际链接的材料 |
|---|---|
| Offline evaluation | https://docs.google.com/document/d/1_kxf0xRAushBEepKh57mHubWCkVuS37iAqwmJcYFoJE/edit |
| Deployment | https://docs.google.com/document/d/1hNuW6bqWYZjlwpit_8W1cu7kllb-jTfy3Liof1GJWug/edit |
| ML Infrastructure and Platform | https://docs.google.com/presentation/d/1b-NLyZW2M8D7r_SXLlpLWnosgryMp7luXcn4d9KAn9M/edit |

## 最薄的三个区域（非缺口已补齐声明）

1. **inference_serving**：有部署/在线批量/监控/搜索主干，但缺 KV cache、量化、连续 batching 等现代 serving 专项来源；多个子术语仍待讲义核验。
2. **systems_harness**：有并行训练、实验版本、工具调用与推理提示主干；agent 环境隔离、工具错误恢复、轨迹评测和安全边界尚薄，不以凭空节点充数。
3. **evaluation**：有离线/在线与基础分类指标，但校准的材料定位待核验；没有完善因果评估、不确定性、污染检测、多模态评测与安全评测。基准评测节点不能替代这些缺口。
