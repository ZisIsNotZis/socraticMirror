# WP-8c 合成答案校准（部分完成，阻塞）

当前 schema 无法表示“完整正确但没划边界”，因此产品承诺的“脆弱掌握”这一类在当前实现里不存在。

来源：INFERRED（人工构造、人工判分及本次 CLI 实测）；范围收口经 supervisor 裁定：本 WP 保留失败证据，三态迁移另开 WP-8d，不在校准中修改逻辑或判分口径。

## 结论先行

- 原始 **a > b > c > d：0/10 可完整验证**，10/10 都被缺维表示与未验证尺度阻塞；这不是声称十组数值实际倒序。
- 可合法实测的 **a > c：10/10**；**c < 同节点初始先验：10/10**。证据：[运行原始输出](evidence/run.txt)、[机器可读结果](results.json)。
- a/c 共20次正式 `score` 接受；b/d 共20份只初始化、未提交。不存在补0凑四维、修改分数拟合排序或拿 d 的先验宣称掌握后验。
- **没有改任何 rubric 锚点或引擎常量**，也未改 data、真实 sessions、docs 或 gitignore。不能用查表常量修复“没有合法输入”的问题。

## 取样与来源

全新 state 执行：

```sh
python3 engine/state.py init --graph data/concepts.yaml --scenarios data/scenarios.yaml --out calibration/selection/state.json
python3 engine/state.py pick --state calibration/selection/state.json --top 1000
```

[完整候选](selection/pick.json)、[实际选中三元组与排名](selection/selected.json)、[未评分初始化状态](selection/state.json)。从候选按五类各两题作分层选择；非宣称这是全局top10。每题选中的主评分节点都是 high；S 来自 pick，实际评分仅更新原答确实谈到且因果错误可明确归属的一个主节点，不把主节点机制错平摊给同题其他节点。其余节点本轮均未测。

| 类别 | 情景 | 候选排名 / 类型 | S | 实际 --nodes（high） |
|---|---|---|---|---|
| 对齐 | scen_wp1b_preference | 25 / boundary | preference_data, reward_hacking, reward_model, rlhf | reward_model |
| 对齐 | scen_wp1b_dpo | 35 / boundary | direct_preference_optimization, kl_regularization, preference_data, reference_policy | direct_preference_optimization |
| agent | scen_wp1b_function | 79 / boundary | agent_tool_use, function_calling, structured_outputs, tool_schema | tool_schema |
| agent | scen_wp1b_loop | 91 / boundary | agent_harness, agent_loop, context_management, session_memory | agent_harness |
| 多模态 | scen_wp1b_vlm | 15 / boundary | multimodal_hallucination, vision_projector, visual_instruction_tuning, vlm | vlm |
| 多模态 | scen_wp1b_clip | 43 / boundary | clip, cross_entropy, vision_transformer, visual_grounding | clip |
| 效率 | scen_wp1b_flash | 29 / boundary | attn_scaled_dot_product, flash_attention, gpu_compute, multihead_attention | flash_attention |
| 效率 | scen_wp1b_kv | 47 / boundary | continuous_batching, gqa, kv_cache, paged_attention | kv_cache |
| 训练 | scen_wp1b_pretrain | 117 / boundary | data_deduplication, data_mixture, pretraining_contamination, quality_filtering | data_deduplication |
| 训练 | scen_wp1b_sft | 55 / boundary | continued_pretraining, instruction_tuning_data, peft, supervised_fine_tuning | supervised_fine_tuning |

### 答案构造的真实来源与限制

环境检查 `which llm pi litellm` 找到 pi 与 litellm；litellm CLI 是代理服务入口且出现远程价格表网络失败。未启动子代理、未调用 HTTP 模型端点、未使用模型判分。supervisor 明确批准本次人工构造路线。因此所有答案均为 **人工构造（作者即强模型）**，没有“便宜模型生成”证明。

c 初稿先只读 brief/required_observables 写入 [construct.py](construct.py)，然后才展开这10题的 expected_elements；复核后保留错误因果，另补一条正确边界以便合法完整评分。构造中知道题意并故意造错，并非现实廉价模型错误分布。a 的成稿在展开 expected_elements 后写入 [fixtures.py](fixtures.py)，逐条人工核查如下；**未满足“a先盲写再对照补一次”的分离流程**，这是来源偏差，不包装成已完成的盲生成。

b 先删掉 a 的第三段，再机械删除前两段里的边界/失败处理片段；全部删除串保存在 `fixtures.py:DELETE_B`，不改其他字符。[工件测试](test_calibration.py)逐字验证。删后个别逗号/分号悬空故意不润色，防止把机械消融变成重写。d 全部为一句“我不知道。”。

## a 的 expected_elements 人工逐条检查

以下是覆盖检查，不是用要点自动判分；原文均在 `answers/<id>/a.md`。

| id后缀 | 机制要点 | 应用要点 | 边界要点 |
|---|---|---|---|
| preference | 奖励拟合比较标签，长度捷径 | 长度/类型分层审计、盲测、奖励与解决率并看 | 奖励非意图，偏标签不会自愈 |
| dpo | 固定参考相对概率、β权衡 | 快照、chosen方向、长度处理、β/轮数留出分析与一次重跑 | 新分布覆盖不足，无RM不等于无偏差 |
| function | 类型/结构不保证金额语义 | 单位声明、执行层权限校验、生成执行分离 | 合法JSON非正确付款，不盲重试 |
| loop | harness预算/终止/状态，压缩可能失约束 | 权限与事实分离、历史、失败出口 | 扩窗非保证，摘要有损 |
| vlm | 编码器—连接器—语言生成，细字缩小 | 本地裁剪/OCR对照、错误分解 | 流畅非证据、丢失像素不能提示恢复 |
| clip | 全局对齐非坐标监督 | 检索/IoU分开、区域监督、留出域差检查 | 相似类别/细瑕疵、域迁移不保证 |
| flash | 分块在线softmax/重算、精确目标 | mask/dtype/梯度、内核兼容、显存测量 | 浮点误差非近似，算术仍二次 |
| kv | KV线性容量、GQA头数、分页碎片 | 390.625GiB估算、准入、连续批处理、公平性 | 分页不减实容量、尾延迟 |
| pretrain | 重复改变有效分布、污染虚高 | 文档/近重复、基准隔离、分域消融与配比 | 模板误删，重叠不能独证记忆 |
| sft | SFT/域预训练/PEFT区分 | 角色模板mask、隐私留出、短程域训练对照 | PEFT非安全，低loss非遵循/不遗忘 |

## 人工判分与证据定位

每份 `sessions/<id>-<a|b|c|d>/judgment.json` 保存四维分或 unverified、逐字引文与状态。a/c另保存正向锚点框架A、因果/约束反向框架B；本轮逐维一致，无≥2分未解冲突。A/B是同一作者的两种检查，不宣称独立评审。`accepted.json` 为真实 CLI 接受输出；`state.json` 为实际落盘状态；`report-data.json` 为对应命令原始JSON。引用可由工件测试逐字定位；c引文保留整段以免切掉错误断言的上下文。

a：辨识3（明确排近邻、改变决策），机制3（完整因果及条件变化），应用3（执行/验证/故障调整），边界3（失效机制与退路）。b仍可辨识/机制3，但删除了回滚/故障处理，应用只支持2；边界遗漏无反证，为unverified。**因此“删边界不动其他维”的要求并非独立维度消融：应用3本来就包含故障识别与调整路径。** 本次不能声称落差仅集中边界维。

c：辨识2、机制0；应用按实际方案逐题给0/1/2而非固定套分；补写边界支持2。明确错误的反证如下，均否定回答所断言的一般机制，不靠从多因症状猜唯一根因。

| id后缀 | c的错误机制（引文见judgment） | 可复核反证 / 应用分理由 |
|---|---|---|
| preference | token数直接变softmax温度 | 奖励比较目标没有这种必然温度公式；分层复审和解决率验收可执行，应用2 |
| dpo | 偏好标签覆盖JSON token标签 | DPO比较相对logprob，不生成此种token监督标签；冻结/合规复测可执行，应用2 |
| function | UTF-8姓名重置货币指数 | JSON整数没有该隐含指数；拆姓名金额不能修复单位契约，应用0 |
| loop | 注意力负权重反转禁止登录 | 注意力权重不是授权逻辑，标准softmax权重也非负；复制约束不能可靠执行硬权限，应用1 |
| vlm | 固定药名词表槽位被物体抢走 | 投影器没有这种药名专属槽位分配机制；本地裁剪和留出可执行，应用2 |
| clip | 全局向量可逆恢复唯一瑕疵框 | 全局压缩无唯一可逆坐标映射；逆归一化不能完成框任务，应用0 |
| flash | 秩一近似删奇异值 | FlashAttention不采用此低秩算法；QKV/padding/梯度验证相关且可执行，应用2 |
| kv | 每token重存全部历史QKV，平方增长 | 持久KV每步追加K/V而非所有QKV，容量按长度线性；排队/分页/压测可执行，应用2 |
| pretrain | 镜像梯度自动抵消 | 同目标重复通常重加权，不会自动变成相反梯度；去重/隔离/域检查可执行，应用2 |
| sft | 用户梯度强制广播助理目标 | 交叉熵逐位置监督不存在这种目标广播；mask与合成号码测试可执行，应用2 |

## 10×4 结果表

四维次序：辨识/机制/应用/边界，U=unverified。`p 主节点`只对应本轮实际 --nodes；`S均值`按pick的全S读取 report-data（含未评分节点先验，**不是全S均已测**）。每份独立从同一初始化起点开始。b/d 的破折号表示未提交，无后验值可比较；原始 report-data 仍含先验占位数，不将它填进此后验列。

| 情景 | 答案 | 四维分 | p 主节点 | S均值 | 状态 |
|---|---|---|---:|---:|---|
| scen_wp1b_preference | a | 3/3/3/3 | 0.822018 | 0.516971 | scored |
| scen_wp1b_preference | b | 3/3/2/U | — | — | 暂缓 / unverified |
| scen_wp1b_preference | c | 2/0/2/2 | 0.000000 | 0.311466 | scored |
| scen_wp1b_preference | d | U/U/U/U | — | — | 暂缓 / unverified |
| scen_wp1b_dpo | a | 3/3/3/3 | 0.852415 | 0.511076 | scored |
| scen_wp1b_dpo | b | 3/3/2/U | — | — | 暂缓 / unverified |
| scen_wp1b_dpo | c | 2/0/2/2 | 0.000000 | 0.297972 | scored |
| scen_wp1b_dpo | d | U/U/U/U | — | — | 暂缓 / unverified |
| scen_wp1b_function | a | 3/3/3/3 | 0.822047 | 0.504299 | scored |
| scen_wp1b_function | b | 3/3/2/U | — | — | 暂缓 / unverified |
| scen_wp1b_function | c | 2/0/0/2 | 0.000000 | 0.298787 | scored |
| scen_wp1b_function | d | U/U/U/U | — | — | 暂缓 / unverified |
| scen_wp1b_loop | a | 3/3/3/3 | 0.822047 | 0.502888 | scored |
| scen_wp1b_loop | b | 3/3/2/U | — | — | 暂缓 / unverified |
| scen_wp1b_loop | c | 2/0/1/2 | 0.000000 | 0.297376 | scored |
| scen_wp1b_loop | d | U/U/U/U | — | — | 暂缓 / unverified |
| scen_wp1b_vlm | a | 3/3/3/3 | 0.839083 | 0.516873 | scored |
| scen_wp1b_vlm | b | 3/3/2/U | — | — | 暂缓 / unverified |
| scen_wp1b_vlm | c | 2/0/2/2 | 0.000000 | 0.307103 | scored |
| scen_wp1b_vlm | d | U/U/U/U | — | — | 暂缓 / unverified |
| scen_wp1b_clip | a | 3/3/3/3 | 0.822023 | 0.517746 | scored |
| scen_wp1b_clip | b | 3/3/2/U | — | — | 暂缓 / unverified |
| scen_wp1b_clip | c | 2/0/0/2 | 0.000000 | 0.312240 | scored |
| scen_wp1b_clip | d | U/U/U/U | — | — | 暂缓 / unverified |
| scen_wp1b_flash | a | 3/3/3/3 | 0.838991 | 0.514569 | scored |
| scen_wp1b_flash | b | 3/3/2/U | — | — | 暂缓 / unverified |
| scen_wp1b_flash | c | 2/0/2/2 | 0.000000 | 0.304821 | scored |
| scen_wp1b_flash | d | U/U/U/U | — | — | 暂缓 / unverified |
| scen_wp1b_kv | a | 3/3/3/3 | 0.838192 | 0.507839 | scored |
| scen_wp1b_kv | b | 3/3/2/U | — | — | 暂缓 / unverified |
| scen_wp1b_kv | c | 2/0/2/2 | 0.000000 | 0.298291 | scored |
| scen_wp1b_kv | d | U/U/U/U | — | — | 暂缓 / unverified |
| scen_wp1b_pretrain | a | 3/3/3/3 | 0.818758 | 0.501307 | scored |
| scen_wp1b_pretrain | b | 3/3/2/U | — | — | 暂缓 / unverified |
| scen_wp1b_pretrain | c | 2/0/2/2 | 0.000000 | 0.296618 | scored |
| scen_wp1b_pretrain | d | U/U/U/U | — | — | 暂缓 / unverified |
| scen_wp1b_sft | a | 3/3/3/3 | 0.839983 | 0.509160 | scored |
| scen_wp1b_sft | b | 3/3/2/U | — | — | 暂缓 / unverified |
| scen_wp1b_sft | c | 2/0/2/2 | 0.000000 | 0.299164 | scored |
| scen_wp1b_sft | d | U/U/U/U | — | — | 暂缓 / unverified |

## 阻塞诊断：不是调查表就能修复

1. **遗漏不是错误。** `references/judge.md`：“0 是有证据的错误，不是‘没说’”；“无法判断的维度写 unverified，不提交伪造整数”；“若 score 只接收完整四维，则暂缓该条提交，不用 0 填空”。这些规则彼此一致，但与“四类答案全部要完整向量并排序”的工作包要求、以及当前仅接收四整数的接口不兼容。b没有边界引文，不满足边界0“明确宣称失效条件下仍无条件有效”，所以必须暂缓。这是**表示/接口缺口**，不是通过修改锚点把没说等同错来修。
2. **部分维度路径仍不解决。** 引擎 `--only` 虽只累计选中维度，入口仍要求四整数/四引文，闸门仍读取整个 scores。不能用伪造占位整数和引文让b钻过去。本次未做这种调用。
3. **未答与答错不能同尺度排序。** d只有“我不知道”，没有辨识错误或机制错误证据。保持 evidence.count=0，仅有先验。c明确机制0，硬闸门使 operable/deep 质量为0，所以 p_mastery=0。初始化先验约0.40，拿 d 的这个占位数排序会得到 c<d，但这不是同尺度的后验比较，更不能为了反过来排序削弱闸门。改12行常量无法跨越机制0闸门，也无法把unverified变成合法整数。
4. **应用与边界锚点交叉。** 应用3明确包含“故障识别与调整路径”；机械删除全部失效处理，自然可能同时降低应用。不能维持b应用3来伪造正交性。本次全部b可执行主体保留，但故障调整被消融，人工按应用2记录，未向引擎提交。

上述10个情景均为相同结构阻塞，非某几行查表反转。没有原始完整四点序列可据以定位或重调指数斜率、offset等常量，故本次常量与锚点改动均为**无**。后续三态表示（有证据分数 / 被要求却遗漏 / 未验证）及report-data未测值显式null由supervisor拆为WP-8d，不在此越界实现。还应先定义“边界是否被要求”的判断依据，不能把任何自然回答遗漏都当弱负证据。

## 验证与复跑

```sh
python3 calibration/run.py
python3 calibration/test_calibration.py
python3 engine/test_state.py
```

- [run输出](evidence/run.txt)：40答案/40独立session，20提交，a>c及c<prior均10/10。
- [工件检查输出](evidence/calibration-tests.txt)：4/4通过，覆盖机械删除、逐字引用、未提交不更新、实际节点子集、部分排序及真实pick来源。
- [原引擎测试输出](evidence/engine-tests.txt)：28/28通过，包括 `test_determinism_byte_for_byte_all_commands` 与 `test_rows_monotone`。引擎代码未改。

`construct.py`保存只见brief时的c初稿；`fixtures.py`保存人工a及分数/删除串；`run.py`只复放这些人工标签调用CLI，**不做模型或自动语义判分**；`test_calibration.py`是工件一致性检查。所有答案与session留在本目录，不增加ignore规则。`selection/`与`results.json`支撑选题及数值表，非孤立日志。

## 剩余风险与 rubric 天生困难的问题

- 完整WP-8c目标未达成；不可把10/10 a>c写成“四级单调通过”。b/d需接口迁移后复测。
- 人工a有expected_elements暴露，c是刻意造错并补过边界，不代表强/便宜模型或真人的现实答题分布；不能估计真阳性率、假阳性率或总体准确率。
- 同一作者构造和评分，双框架不是独立复核；12行查表仅覆盖少量向量、每题单次直接证据，未检验边界临界分、补答、多轮累积与节点间异质性。
- 原题多因且缺可区分观测时，无法从症状唯一判机制；正确备选机制应免责，不能强贴私有要点。
- 自由回答未主动说边界、术语省略或回答简短时，不能从缺失推导“不懂”；工程上默认约束也可能不被逐句复述。
- 融合题主节点的错因不能平摊给同题节点；本次只提交主节点，不能据此宣称整簇/全S掌握已被校准。
- “应用故障处理”与“边界退路”在文本上重叠，机械删减不是统计独立干预；跨维可辨识性尚未解决。
- p_mastery是operable+deep的内部质量，不是答题正确率；先验占位与已评分后验若都显示一个浮点数，很容易被下游错误排序，当前输出本身没有结构性阻止这一误用。
