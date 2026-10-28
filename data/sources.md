# 现代大模型知识网 · 外部来源与 WP-1b 验收

来源：INFERRED（来源选取、依赖与分簇为编者判断）；范围按用户追加裁决落实。获取日期 **2026-10-28**（运行环境日期）。当前含概念、锚点与情景；情景是来源任务/机制的教学改写，数字与脏约束均为出题设定，不冒充生产事故、原题数字或benchmark实测。下列原有教材来源仍用于最少机制前置；现代扩域来源与运行证据见后文。

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
- `importance` 是面向用户现代大模型领域的诊断优先级，不是来源评级或每簇配额；对齐、agent、安全、多模态、效率优先。
- `source.type=model, confidence=low` 表示无已核验直接外部命名/机制出处的编者补洞。已有真实链接但本次不可达则保留来源类型、降为 low、写 verify_pending。model 数量与名单以本页验收输出为准；不是所有非model细节都已得到逐项外部证明。

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

## WP-1b 实际抓取与真伪审查

本轮没有 `web_search` / `web_fetch` 工具，实际通过 `curl -L --max-time 18 -sS -w '\n%{http_code}' URL` 并发抓取。先验URL不能算证据：逐一核对HTTP、标题、目录/摘要、版本；HTTP200而标题是不可用页面的也判失败。以下是抓取当时提取的状态、字节与章节/任务结构记录。arXiv `/abs/` **只读摘要与版本元数据**，不是全文；其概念 confidence 至多 medium，不能虚构章节。官方滚动文档无冻结release，版本以抓取日快照标识，未来需复核。

| 来源 | URL | 抓取日期 / 版本 | 本次读到的结构与贡献（两者=概念+情景） | 抓取证据 |
|---|---|---|---|---|
| mcp | https://modelcontextprotocol.io/specification/2025-06-18 | 2026-10-28 / 规范 2025-06-18 | 两者；实际标题：Documentation Index → Base Protocol → Client Features → Server Features → On this page → Specification → Overview → Key Details → Base Protocol → Features → Additional Utilities → Security and Trust  Safety | HTTP 200；313867 bytes |
| openai_agents | https://openai.github.io/openai-agents-python/ | 2026-10-28 / 滚动官方文档；抓取日快照 | 两者；实际标题：OpenAI Agents SDK → Why use the Agents SDK → Agents SDK or Responses API? → Installation → Hello world example → Start here → Choose your path | HTTP 200；76561 bytes |
| openai_tools | https://openai.github.io/openai-agents-python/tools/ | 2026-10-28 / 滚动官方文档；抓取日快照 | 两者；实际标题：Tools → Choosing a tool type → Hosted tools → Hosted tool search → Programmatic Tool Calling → Hosted container shell + skills → Local runtime tools → Approval for local shell and file edits → ComputerTool and the Responses computer tool → Pending computer safety checks → Function tools → Returning images or files from function tools | HTTP 200；253759 bytes |
| google_adk | https://google.github.io/adk-docs/ | 2026-10-28 / 滚动官方文档；抓取日快照 | 两者；实际标题：Build production agents, not prototypes. → Build agents with agents. → Reliable logic. Intelligent reasoning. → Powerful simplicity. Built for scale. → Open ecosystem. Connect everything. → Ready to build agents? → Developer Community → Community call → Developer resources → Frequently Asked Questions → Cookie consent | HTTP 200；130520 bytes |
| google_safety | https://google.github.io/adk-docs/safety/ | 2026-10-28 / 滚动官方文档；抓取日快照 | 两者；实际标题：Safety and Security for AI Agents → Safety and Security Risks → Best practices → Identity and Authorization → Agent-Auth → User Auth → Guardrails to screen inputs and outputs → In-tool guardrails → Built-in Gemini Safety Features → Callbacks and Plugins for Security Guardrails → Sandboxed Code Execution → Evaluations | HTTP 200；251384 bytes |
| guardrails_sdk | https://openai.github.io/openai-agents-python/guardrails/ | 2026-10-28 / 滚动官方文档；抓取日快照 | 两者；实际标题：Guardrails → Workflow boundaries → Input guardrails → Execution modes → Output guardrails → Tool guardrails → Tripwires → Implementing a guardrail | HTTP 200；119635 bytes |
| context_sdk | https://openai.github.io/openai-agents-python/context/ | 2026-10-28 / 滚动官方文档；抓取日快照 | 两者；实际标题：Context management → Local context → Use local context for capability visibility → What RunContextWrapper exposes → Advanced: ToolContext → Agent/LLM context | HTTP 200；96319 bytes |
| running_sdk | https://openai.github.io/openai-agents-python/running_agents/ | 2026-10-28 / 滚动官方文档；抓取日快照 | 两者；实际标题：Running agents → Runner lifecycle and configuration → The agent loop → Streaming → Responses WebSocket transport (optional helper) → Run config → Common run config categories → Run config details → State and conversation management → Choose a memory strategy → Conversations/chat threads → Manual conversation management | HTTP 200；189837 bytes |
| sessions_sdk | https://openai.github.io/openai-agents-python/sessions/ | 2026-10-28 / 滚动官方文档；抓取日快照 | 两者；实际标题：Sessions → Quick start → Resuming interrupted runs with the same session → Core session behavior → Control how history and new input merge → Limiting retrieved history → Memory operations → Basic operations → Using pop_item for corrections → Built-in session implementations → Choose a built-in session implementation → OpenAI Conversations API sessions | HTTP 200；204015 bytes |
| mcp_sdk | https://openai.github.io/openai-agents-python/mcp/ | 2026-10-28 / 滚动官方文档；抓取日快照 | 两者；实际标题：Model context protocol (MCP) → Choosing an MCP integration → MCP Python SDK v1 and v2 → Agent-level MCP configuration → Shared patterns across transports → 1. Hosted MCP server tools → Basic hosted MCP tool → Streaming hosted MCP results → Optional approval flows → Connector-backed hosted servers → 2. Streamable HTTP MCP servers → Approval policies for local MCP servers | HTTP 200；170810 bytes |
| owasp | https://genai.owasp.org/llm-top-10/ | 2026-10-28 / 滚动官方文档；抓取日快照 | 两者；实际标题：Join us in Orlando, FL 10/11  10/15 @ InfoSec World 2026 → | → 2025 Top 10 Risk  Mitigations for LLMs and Gen AI Apps → LLM01:2025 Prompt Injection → LLM02:2025 Sensitive Information Disclosure → LLM03:2025 Supply Chain → LLM04:2025 Data and Model Poisoning → LLM05:2025 Improper Output Handling → LLM06:2025 Excessive Agency → LLM07:2025 System Prompt Leakage → LLM08:2025 Vector and Embedding Weaknesses → LLM09:2025 Misinformation | HTTP 200；924580 bytes |
| rlhf | https://arxiv.org/abs/2203.02155 | 2026-10-28 / 2203.02155v1 | 两者；摘要：人类示范SFT → 偏好排序奖励模型 → RLHF；不冒充全文章节。 | HTTP 200；45449 bytes |
| dpo | https://arxiv.org/abs/2305.18290 | 2026-10-28 / 2305.18290v3 | 两者；摘要：从偏好直接优化策略，避免显式奖励模型训练；仅摘要。 | HTTP 200；45199 bytes |
| ppo | https://arxiv.org/abs/1707.06347 | 2026-10-28 / 1707.06347v2 | 两者；摘要：替代目标、采样与多轮小批量更新；仅摘要。 | HTTP 200；43075 bytes |
| constitutional | https://arxiv.org/abs/2212.08073 | 2026-10-28 / 2212.08073v1 | 两者；摘要：原则、自我批评修订、AI比较反馈与RL；仅摘要。 | HTTP 200；50267 bytes |
| alignment_survey | https://arxiv.org/abs/2309.15025 | 2026-10-28 / 2309.15025v1 | 概念交叉核验；摘要结构：outer/inner alignment → 解释性/对抗漏洞 → benchmarks → 未来方向；全文目录未读。 | HTTP 200；43300 bytes |
| llama | https://arxiv.org/html/2407.21783v3 | 2026-10-28 / 2407.21783v3 | 两者；3 Pre-Training（data/mix/architecture/parallelism）→ 4 Post-Training（RM/SFT/DPO/Iterative Rounds）→ 5.4 Safety/Red Teaming → 6 Inference/FP8 → 7 Vision；正文含References。 | HTTP 200；1072480 bytes |
| qwen | https://arxiv.org/html/2412.15115v1 | 2026-10-28 / 2412.15115v1 | 两者；2 Architecture & Tokenizer → 3 Pre-training（data/scaling/long context）→ 4 Post-training（SFT/offline RL/online RL/long context）→ 5 Evaluation；正文含References。 | HTTP 200；416465 bytes |
| gpt4 | https://arxiv.org/abs/2303.08774 | 2026-10-28 / 2303.08774v6 | 概念交叉核验；技术报告摘要：多模态输入、能力评测、可靠性与局限；全文章节未读，不能推断未公开架构。 | HTTP 200；89000 bytes |
| diffusion_survey | https://arxiv.org/html/2209.00796v15 | 2026-10-28 / 2209.00796v15 | 两者；1 Introduction → 2 Foundations（DDPM/SGM/SDE）→ 3 Efficient Sampling → 后续训练/应用分类；可读全文与参考文献。 | HTTP 200；799357 bytes |
| vlm_survey | https://arxiv.org/abs/2306.13549 | 2026-10-28 / 2306.13549v4 | 两者；摘要结构：架构 → 训练策略与数据 → 评测 → 更细粒度/模态 → 幻觉、M-ICL/M-CoT；全文目录未读。 | HTTP 200；45824 bytes |
| agentbench | https://arxiv.org/abs/2308.03688 | 2026-10-28 / 2308.03688v3 | 两者；任务：8类交互环境中的推理、决策与指令遵循；仅摘要。 | HTTP 200；45318 bytes |
| webarena | https://arxiv.org/abs/2307.13854 | 2026-10-28 / 2307.13854v4 | 两者；真实网页环境、长程任务、功能性终态评测；仅摘要。 | HTTP 200；44637 bytes |
| osworld | https://arxiv.org/abs/2404.07972 | 2026-10-28 / 2404.07972v2 | 两者；真实桌面环境、跨应用和文件任务、执行式评估；仅摘要。 | HTTP 200；46703 bytes |
| mmmu | https://arxiv.org/abs/2311.16502 | 2026-10-28 / 2311.16502v4 | 两者；多学科专家级多模态理解推理；仅摘要。 | HTTP 200；45752 bytes |
| helm | https://arxiv.org/abs/2211.09110 | 2026-10-28 / 2211.09110v2 | 两者；多场景多指标的holistic evaluation、准确/鲁棒/校准/效率；仅摘要。 | HTTP 200；52588 bytes |
| flash | https://arxiv.org/abs/2205.14135 | 2026-10-28 / 2205.14135v2 | 两者；IO-aware exact attention，减少HBM访问；只核验摘要，不宣称读内核。 | HTTP 200；44575 bytes |
| vllm | https://arxiv.org/abs/2309.06180 | 2026-10-28 / 2309.06180v1 | 两者；KV缓存内存浪费、PagedAttention与共享；只核验摘要。 | HTTP 200；44011 bytes |
| dit | https://arxiv.org/abs/2212.09748 | 2026-10-28 / 2212.09748v2 | 两者；latent diffusion以Transformer替代U-Net、规模与图像token；只核验摘要。 | HTTP 200；40844 bytes |
| rt2 | https://arxiv.org/abs/2307.15818 | 2026-10-28 / 2307.15818v1 | 两者；VLA、动作token、网络知识向机器人控制迁移；只核验摘要。 | HTTP 200；52582 bytes |
| drive | https://arxiv.org/abs/2212.10156 | 2026-10-28 / 2212.10156v2 | 两者；统一感知/预测/规划的自动驾驶框架；只核验摘要。 | HTTP 200；44524 bytes |
| grpo | https://arxiv.org/abs/2402.03300 | 2026-10-28 / 2402.03300v3 | 两者；DeepSeekMath，GRPO无需同规模critic，数学推理RL；只核验摘要。 | HTTP 200；43051 bytes |
| quant | https://arxiv.org/abs/2306.00978 | 2026-10-28 / 2306.00978v6 | 两者；AWQ保护重要权重、激活感知缩放与低比特部署；只核验摘要。 | HTTP 200；45552 bytes |
| retrieval | https://arxiv.org/abs/2004.04906 | 2026-10-28 / 2004.04906v3 | 两者；双编码稠密段落检索与开放域问答；只核验摘要，混合检索细节需另审。 | HTTP 200；42561 bytes |
| longcontext | https://arxiv.org/abs/2306.15595 | 2026-10-28 / 2306.15595v2 | 两者；位置插值扩展RoPE模型上下文；只核验摘要。 | HTTP 200；42661 bytes |
| moe | https://arxiv.org/abs/2401.04088 | 2026-10-28 / 2401.04088v1 | 两者；Mixtral稀疏专家、每token选择专家；只核验摘要。 | HTTP 200；46189 bytes |
| clip | https://arxiv.org/abs/2103.00020 | 2026-10-28 / 2103.00020v1 | 两者；图文对比预训练与零样本迁移；只核验摘要。 | HTTP 200；45425 bytes |
| vllm_quant | https://docs.vllm.ai/en/latest/features/quantization/ | 2026-10-28 / 滚动官方文档；抓取日快照 | 两者；实际标题：Quantization¶ → Selecting Linear Backends per Quantization¶ → Supported Hardware¶ → Out-of-Tree Quantization Plugins¶ → Registering a Custom Quantization Method¶ → Required QuantizationConfig Methods¶ → Implementing a Quantized Linear Method¶ → Implementing a Quantized MoE Method¶ → Using the Plugin¶ | HTTP 200；223749 bytes |
| vllm_prefix | https://docs.vllm.ai/en/latest/features/automatic_prefix_caching/ | 2026-10-28 / 滚动官方文档；抓取日快照 | 两者；实际标题：Automatic Prefix Caching¶ → Introduction¶ → Enabling APC in vLLM¶ → Hybrid Mamba models¶ → Example workloads¶ → Limits¶ | HTTP 200；194017 bytes |
| vllm_parallel | https://docs.vllm.ai/en/latest/serving/parallelism_scaling/ | 2026-10-28 / 滚动官方文档；抓取日快照 | 两者；实际标题：Parallelism and Scaling¶ → Distributed inference strategies for a single-model replica¶ → Distributed serving of Mixture of Experts (MoE) models¶ → Single-node deployment¶ → Multi-node deployment¶ → What is Ray?¶ → Ray cluster setup with containers¶ → Running vLLM on a Ray cluster¶ → Running vLLM with MultiProcessing¶ → Optimizing network communication for tensor parallelism¶ → Enabling GPUDirect RDMA¶ → Troubleshooting distributed deployments¶ | HTTP 200；226033 bytes |

### 抓取失败不能包装成外部证明

- Anthropic旧文档 https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview 和新入口 https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview，以及 https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks ：均返回 HTTP200 / 306195 bytes，但实际正文标题 **App unavailable**，故 **verify_pending / low**，没有据此为节点标已核验；工具/安全改以OpenAI、Google、MCP规范与Llama报告相互校对。Constitutional AI论文是本轮可读的Anthropic一手研究摘要，不是上述官方文档的替代全文。
- VLM综述试取 https://arxiv.org/html/2306.13549v5 、对齐综述试取 https://arxiv.org/html/2309.15025v3 均HTTP404；改读上表真实 `/abs/` 链接。不存在的版本不进入节点ref。
- https://huggingface.co/docs/peft/index 本轮curl超时（000，18秒）；`qlora`、`peft` 保留真实官方路径但 **verify_pending / low**，尚未声称已读该页。
- https://openai.github.io/openai-agents-python/safety/ 与 https://rlhfbook.com/book-toc 返回404，未作节点出处；改读上表SDK guardrails与Google safety。https://docs.vllm.ai/en/latest/features/spec_decode/ 虽HTTP200但只有816 bytes、无机制正文，未作新来源；已有speculative_decoding仍用原课程reading锚点，不能当内核级已核验。

### 真伪 rubric 与两独立来源交叉核验的实际边界

- 版本/日期：论文用arXiv提交版本，MCP用固定2025-06-18，滚动官方文档只能以获取日标识；不能假装其内容有固定release。引用：论文保留References/版本元数据；SDK文档有规范/实现链接，MCP有协议/安全子页。排除营销排行榜、纯模型生成榜单；Google ADK主页只作入口，机制尽量落到可读子页。
- 对齐/RLHF：OpenAI InstructGPT摘要与Meta Llama §4、Qwen §4相互独立；DPO原论文和Meta/Qwen实施报告不冲突。安全：OWASP 2025风险分类、Google ADK safety执行边界、Meta Llama §5.4提供独立分类与系统安全角度。
- Agent/harness：OpenAI SDK工具/上下文/运行循环与Google ADK安全/工作流相互独立，MCP固定规范约束外部工具边界；AgentBench/WebArena/OSWorld是第三方评测任务而非厂商宣传。
- 多模态：MLLM综述摘要、OpenAI GPT-4摘要与Meta Llama §7交叉；扩散综述正文与DiT论文摘要交叉；效率：FlashAttention论文、vLLM论文/文档与Meta Llama §3/§6交叉。
- **两独立来源不冲突只在上述主干/机制层满足，不等于每个细叶子已获两份直接证明。** SDK精细能力、量化后端等可能只有一个实现来源，统一medium；模型推导切面标model/low；不可达低置信项标pending。`requires`仍是编者选的最少机制先修，不是文献逐边证明。此限制是残余审计风险，不能以0冲突或低model占比掩盖。

## WP-1b 范围裁决与入口结构

采用用户后续裁决而非最初“全部旧ID不动”：保留节点不改ID，但删除不再诊断的旧节点。`classical_ml` **整簇删除**；SVM、决策树、PCA三个候选本轮未进入最终树。保留最少矩阵乘/SVD、梯度/链式法则、概率/期望/熵/KL/softmax/交叉熵是解释低秩、注意力与训练损失所必需；CNN只留卷积、池化、步幅、残差/BN等骨干原语，RNN与word2vec各留一个作路线分叉对照，不展开传统任务流水线。

面向人的入口为 `language_model` / `transformer`，横向连预训练→SFT/RLHF/DPO→推理RL→安全→agent/harness+MCP→检索搜索→应用；另一轴从ViT/VLM通往图像/视频理解、VLA/具身与自动驾驶，从diffusion/latent diffusion/DiT通往生成。效率/并行节点解释模型如何训练与服务，不收运维流程。自动驾驶/具身只作 `multimodal_vision` 的应用分支，不另开行业簇。`requires`读法是“本节点需要列出的先修”，所以数学根仍可无前置；这些根不是面向用户的首轮入口。只改data，没有强迫引擎改变选题顺序。

- 相对接单时155节点：新增172、保留110、删除45；保留节点中降级39（high→medium；不是删除数）：`accuracy`, `activation`, `adam`, `backpropagation`, `batch_norm`, `beam_search`, `bellman_equation`, `bert`, `calculus`, `cnn`, `convolution`, `data_parallelism`, `data_preprocessing`, `distribution_shift`, `experiment_tracking`, `gpu_compute`, `gradient_descent`, `learning_rate_schedule`, `linear_algebra`, `matrix_multiplication`, `mdp`, `minibatch_sgd`, `mlp`, `model_calibration`, `model_compression`, `model_deployment`, `model_versioning`, `object_detection`, `padding_stride`, `perplexity`, `pooling`, `precision_recall`, `rnn`, `sgd`, `svd`, `train_test_split`, `validation_split`, `word2vec`, `word_embedding`。
- 删除旧节点：`ab_testing`, `anchor_boxes`, `asynchronous_computation`, `batch_prediction`, `bias_variance`, `canary_release`, `categorical_encoding`, `concept_shift`, `confusion_matrix`, `continual_learning`, `convexity`, `covariate_shift`, `cross_validation`, `early_stopping`, `eigendecomposition`, `fcn`, `feature_engineering`, `feature_store`, `gru`, `hyperparameter_optimization`, `image_classification`, `importance_weighting`, `instance_segmentation`, `iou`, `label_shift`, `linear_regression`, `logistic_regression`, `lstm`, `missing_values`, `ml_pipeline`, `model_monitoring`, `negative_sampling`, `nonmaximum_suppression`, `online_experiment`, `online_prediction`, `parameter_server`, `policy_iteration`, `q_learning`, `rcnn`, `roc_auc`, `sarsa`, `semantic_segmentation`, `shadow_deployment`, `universal_approximation`, `value_iteration`。
- 被判据剔除的候选：SVM/决策树/PCA独立诊断、CRF/HMM/词性标注、任务特化小检测器、通用运维/canary/shadow/feature store手册；流匹配等仍属大模型生成技术，但未找到直接已读专项材料故model/low。
- 原35情景ID全部保留；其中经典任务逐条改成低秩嵌入、LLM损失、视觉预训练、代理轨迹等现代语境，新增40条。保留ID不表示保留原题语义，旧会话不可直接按新语义回放。
- 模型补洞（均low）：`blue_team_defense`, `tool_error_recovery`, `agent_plugins`, `persistent_knowledge`, `flow_matching`, `llm_as_judge`, `guardrail_race`, `prefix_cache_key`, `preference_annealing`, `reward_ensemble`。

### 仍最薄的三块

1. **后训练的细粒度算法比较**：SFT/RM/DPO/PPO/GRPO有一手论文与报告，但过程奖励、偏好噪声/奖励集成等直接来源仍不齐；QLoRA/PEFT官方页不可达。不能把“已覆盖名字”当成可校准深机制判断。
2. **持久知识与agent可靠执行**：MCP/工具/权限/运行恢复有官方契约，LLM Wiki、插件、错误恢复等跨系统抽象仍含model/low；重放、并发副作用和外部状态一致性还缺故障复盘，Anthropic工具文档未读成。
3. **具身/驾驶与生成媒体交叉**：VLA、动作token、BEV、闭环仅有摘要锚定，sim2real/占用表示/安全控制未深入；视频生成与flow matching薄，不应解释为具身专家级覆盖。

### 最可能仍不精确的三条 requires

方向以下均为“左节点 requires 右节点”，不是知识分类边：

- `vlm → vision_transformer`：现代主流可行，但VLM也能采用CNN等视觉编码器；这更像当前路线的先修而非所有实现必要条件。
- `closed_loop_control → mdp`：有助于判断代理/机器人回报，但传统反馈控制并不要求MDP形式；可能应改成局部内联假设而非硬先修。
- `vision_projector → vlm`：以整机VLM做模块理解入口自然，但投影机制只依赖视觉/语言表示与矩阵映射；可能倒置了组件与整机的教学依赖。

已修正的反例：`verifiable_reward → reward_model` 会错误暗示规则验证奖励必须有学习式RM；改为回报机制，并在下面验收检查中禁止此边。另一个机械风险是跨轮补充重复ID（`rejection_sampling`曾重复），验收首先断言ID唯一，避免dict静默覆盖。

## WP-1b 硬校验：可复跑检查与当次输出

依赖：仓库现有运行环境Python3 + PyYAML（仅审计脚本，engine仍为stdlib）。以下代码直接读真实data，不修改任何文件；保留/新增统计以初始提交 `b1a1ed7` 的155节点为基线，避免工作期间父会话提交中间态而改变分母。

```sh
python3 - <<'PY'
import yaml, collections, re, subprocess
c=yaml.safe_load(open('data/concepts.yaml')); a=yaml.safe_load(open('data/anchors.yaml')); ss=yaml.safe_load(open('data/scenarios.yaml'))
ids={n['id'] for n in c}; by={n['id']:n for n in c}
assert len(ids)==len(c)==len(a)==len({n['id'] for n in a}) and ids=={n['id'] for n in a}
assert 260<=len(c)<=340 and len(a)>=280 and 55<=len(ss)<=75
assert 'reward_model' not in by['verifiable_reward']['requires']
seen=set(); active=set()
def visit(i):
    assert i in ids and i not in active
    if i in seen: return
    active.add(i)
    for r in by[i]['requires']: visit(r)
    active.remove(i); seen.add(i)
for i in ids: visit(i)
names={}
for n in a:
    for term in [n['name']]+n['aliases']:
        k=re.sub(r'\s+',' ',term.strip().casefold())
        assert k not in names or names[k]==n['id'], (k,n['id'])
        names[k]=n['id']
coverage={i for s in ss for i in s['instantiates']}
for s in ss:
    assert 2<=len(s['instantiates'])<=5 and set(s['instantiates'])<=ids
    assert len(s['expected_elements'])>=3 and any('边界' in str(x) for x in s['expected_elements'])
    assert re.search(r'\d',s['brief'])
high={n['id'] for n in c if n['importance']=='high'}
old={n['id'] for n in yaml.safe_load(subprocess.check_output(['git','show','b1a1ed7:data/concepts.yaml']))}
newhigh=high-old
assert len(newhigh&coverage)/len(newhigh)>=.9
assert .30<=len(high)/len(c)<=.40
assert sum(n['source']['type']=='model' for n in c)/len(c)<.20
assert all(n['source']['confidence']=='low' for n in c if n['source']['type']=='model')
adj={i:set() for i in ids}
for n in c:
    for r in n['requires']: adj[n['id']].add(r); adj[r].add(n['id'])
reached=set(); todo=[next(iter(ids))]
while todo:
    i=todo.pop()
    if i not in reached: reached.add(i); todo.extend(adj[i]-reached)
assert reached==ids
print('nodes',len(c),'anchors',len(a),'scenarios',len(ss))
print('clusters',dict(sorted(collections.Counter(n['cluster'] for n in c).items())))
print('DAG acyclic; dangling 0; alias conflicts 0; weak components 1; scenario contracts PASS')
print('high',len(high),f'{len(high)/len(c):.2%}', 'covered',len(high&coverage),'uncovered',sorted(high-coverage))
print('new high',len(newhigh),'covered',len(newhigh&coverage),'model',sum(n['source']['type']=='model' for n in c))
print('retained',len(old&ids),'added',len(ids-old),'deleted',len(old-ids))
PY
python3 engine/state.py init --graph data/concepts.yaml --scenarios data/scenarios.yaml --out /tmp/x/state.json
python3 engine/state.py pick --state /tmp/x/state.json --top 5
python3 engine/test_state.py
```

图/覆盖检查当次终端输出（额外统计含单连通与新增high覆盖）：

```text
nodes 282 anchors 282 scenarios 75
clusters {'agent_harness': 36, 'architecture': 22, 'efficiency_serving': 26, 'evaluation': 14, 'generative_media': 12, 'llm_foundation': 37, 'multimodal_vision': 19, 'posttraining_alignment': 22, 'pretraining': 28, 'retrieval_search': 10, 'rl_reasoning': 16, 'safety_redteam': 23, 'systems_infra': 17}
DAG acyclic; dangling 0
alias conflicts 0 []
high 104 36.88% covered 104 100.00% uncovered []
new high 84 covered 84 100.00% uncovered []
model source 10 3.55%
weak components 1 [282]
isolated []
scenario contracts: PASS
retained old 110 added 172 removed 45
```

init 当次输出：
```json
{
  "nodes": 282,
  "out": "/tmp/x/state.json",
  "scenarios": 75
}
```

pick 当次输出（5候选，原样）：
```json
[
  {
    "S": [
      "autoregressive_decoding",
      "beam_search",
      "language_model"
    ],
    "cost": 3.0216164395818303,
    "gain": 0.09864114694920367,
    "question_type": "application",
    "reason": "Importance-weighted expected entropy reduction over 3 nodes per unit cost.",
    "scenario": "scen_beam_translation",
    "utility": 0.03264515828582627
  },
  {
    "S": [
      "autoregressive_decoding",
      "beam_search",
      "language_model"
    ],
    "cost": 3.0216164395818303,
    "gain": 0.09864114694920367,
    "question_type": "boundary",
    "reason": "Importance-weighted expected entropy reduction over 3 nodes per unit cost.",
    "scenario": "scen_beam_translation",
    "utility": 0.03264515828582627
  },
  {
    "S": [
      "dit",
      "latent_diffusion",
      "transformer",
      "vae"
    ],
    "cost": 3.754887721613817,
    "gain": 0.05423237736853537,
    "question_type": "boundary",
    "reason": "Importance-weighted expected entropy reduction over 4 nodes per unit cost.",
    "scenario": "scen_wp1b_dit",
    "utility": 0.014443142216041224
  },
  {
    "S": [
      "dit",
      "latent_diffusion",
      "transformer",
      "vae"
    ],
    "cost": 3.754887721613817,
    "gain": 0.05423237736853537,
    "question_type": "diagnosis",
    "reason": "Importance-weighted expected entropy reduction over 4 nodes per unit cost.",
    "scenario": "scen_wp1b_dit",
    "utility": 0.014443142216041224
  },
  {
    "S": [
      "direct_preference_optimization",
      "iterative_posttraining",
      "rejection_sampling",
      "sft_loss_mask"
    ],
    "cost": 3.752689015510092,
    "gain": 0.04854821017830235,
    "question_type": "boundary",
    "reason": "Importance-weighted expected entropy reduction over 4 nodes per unit cost.",
    "scenario": "scen_wp1b_iteration",
    "utility": 0.012936912698507563
  }
]
```

test_state 当次输出（包含真实数据 RealDataTests）：
```text
test_pick_on_shipped_data (__main__.RealDataTests.test_pick_on_shipped_data) ... ok
test_bisect_partitions_original (__main__.StateTests.test_bisect_partitions_original) ... ok
test_boundary_gate (__main__.StateTests.test_boundary_gate) ... ok
test_boundary_zero_quote_exception_and_other_zero_rejection (__main__.StateTests.test_boundary_zero_quote_exception_and_other_zero_rejection) ... warning: boundary=0 without quotation
ok
test_correct_fusion_raises_every_node (__main__.StateTests.test_correct_fusion_raises_every_node) ... ok
test_cycle_rejected (__main__.StateTests.test_cycle_rejected) ... ok
test_determinism_byte_for_byte_all_commands (__main__.StateTests.test_determinism_byte_for_byte_all_commands) ... ok
test_difficulty_offsets_and_clamp (__main__.StateTests.test_difficulty_offsets_and_clamp) ... ok
test_evidence_and_single_hop_propagation (__main__.StateTests.test_evidence_and_single_hop_propagation) ... ok
test_failed_fusion_entropy_almost_unchanged (__main__.StateTests.test_failed_fusion_entropy_almost_unchanged) ... ok
test_gate_does_not_permanently_prevent_learning (__main__.StateTests.test_gate_does_not_permanently_prevent_learning) ... ok
test_invalid_scores (__main__.StateTests.test_invalid_scores) ... ok
test_mechanism_gate_overrides_even_strong_prior (__main__.StateTests.test_mechanism_gate_overrides_even_strong_prior) ... ok
test_missing_quote_rejected_cli_no_write (__main__.StateTests.test_missing_quote_rejected_cli_no_write) ... ok
test_no_scenarios_fallback (__main__.StateTests.test_no_scenarios_fallback) ... ok
test_noisy_and_expectation_and_cost (__main__.StateTests.test_noisy_and_expectation_and_cost) ... ok
test_prompted_negative_stronger (__main__.StateTests.test_prompted_negative_stronger) ... ok
test_report_and_topology (__main__.StateTests.test_report_and_topology) ... ok
test_rows_monotone (__main__.StateTests.test_rows_monotone) ... ok
test_tested_low_entropy_nodes_not_selected (__main__.StateTests.test_tested_low_entropy_nodes_not_selected) ... ok
test_yaml_real_format_and_folded_source (__main__.StateTests.test_yaml_real_format_and_folded_source) ... ok

----------------------------------------------------------------------
Ran 21 tests in 0.786s

OK
```

新增high未覆盖：无；全部high覆盖100%，但覆盖并非题目质量或判定校准已完成。以上输出只证明结构、运行与契约，不证明每条依赖语义正确。
