# WP-9 dry run — false-negative control + two-session stability (subagent as examinee)

<!-- 来源：INFERRED（校准工件，不是产品会话）。考生为子代理模型，非用户本人。 -->

状态：**通过**（0 假阴性、7 个节点两次测量、等级差全为 0）。真实用户的复测仍待做，见文末。

## 方法

- 考生：`deepseek-v4-pro`（无工具、禁读文件、cwd=/tmp）；题面体检：`deepseek/deepseek-flash`、`glm-5.3-flash`，只回裁决，不回答案内容。
- 题面：6 + 5 道，目标节点是任何合格工程师都铁定掌握的核心概念（注意力缩放、FlashAttention、数据并行、困惑度、beam、CLIP、ViT、因果 mask、交叉熵数值）。每道都按 examiner 契约给可观测事实与承重约束。
- 评分：逐节点调用 `engine/state.py score --node`，只评回答实际谈到的节点；没谈到的记 unverified（修 M1 的 D13）。
- 判定：两次会话共用 7 个节点；节点级等级差 ≥2 视为不稳定；任何 fixture 节点落到 `unknown` 视为假阴性。
- 复跑：`python3 calibration/m2_falseneg/run_checks.py`（从 `data/` 重建两个 state，再套用 `judgments.json`，确定性）。

## 结果

| 节点 | 会话 A | 会话 B | 差 |
|---|---|---|---|
| attn_scaled_dot_product | deep (0.978) | deep (0.913) | 0 |
| softmax | deep (0.903) | deep (0.903) | 0 |
| allreduce | deep (0.892) | deep (0.824) | 0 |
| data_parallelism | deep (0.857) | deep (0.857) | 0 |
| cross_entropy | deep (0.856) | deep (0.901) | 0 |
| beam_search | deep (0.822) | deep (0.822) | 0 |
| autoregressive_decoding | deep (0.824) | deep (0.824) | 0 |

- 假阴性：**0 / 13 个被评分节点**。
- 单次覆盖（未参与稳定性）：flash_attention、perplexity、clip、visual_grounding、multihead_attention（B 会话）、language_model（未真正讨论，按契约 unverified）。
- 回答全部接近专家级；四个场景的数值推导与参考值一致（交叉熵 1.313、梯度 400MB/40ms、ViT 4×/16×、beam 每 token −0.8 vs −0.3）。

## 这次干跑真正证明了什么

**证明**：从题面 → 作答 → 逐节点判分 → 引擎后验这条链，对"强回答"不会系统性判成"不会"；同一节点换题面、换题型后等级不漂。

**没证明**：它不能证明用户本人的假阴性率。考生是一个知识均匀的强模型，题面难度对它偏低；用户的强项不均匀，且 M1 已暴露过"题面靠猜"的缺陷。真正的闸门是用用户的铁定掌握节点复测。

## 干跑发现并已修的缺陷

1. **D13（此前已记）**：M1 把整组四维同分记到 S 的全部节点。本次改用 `--node` 逐节点，回答没谈到的节点不随之升级（A1 的 multihead_attention、A5 的 language_model 都留在 unverified）。
2. **D14 新增：把现状写成禁令**。`scen_ddp_small_batch` 的 boundary 问法"只能加梯度累积或异步独立更新"把两个都会改变全局目标的选项当成唯一选择；考生据此排除了压缩与重叠，给出次优解。改写为"压缩/重叠/bucket 化都允许"，重问后回答回到正确路径。修复：该情景的 boundary ask 待改（WP-8b 数据），本条先记为 D14。
3. **工件层**：子代理偶尔把正文只放在 transcript、最终消息返回空（A1、A3、B4 各一次）。判分从 transcript 取最长 assistant 文本，不从最终消息取；这只影响校准工件，不影响产品。

## 限制

- 单模型、单温度、无追问；没有覆盖补漏与二分。
- 题面预检用的是便宜模型，一次返回空裁决（B3 初版）；改用第二个便宜模型复检。
- 7 个节点的稳定性样本仍小；用户复测时以 M1 的旧结论作第三点，但 M1 是整组同分（D13），只作粗对照。
