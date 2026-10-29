四级单调性通过 **10/10**（严格限定为本次指定标签下的 `a>b>c`、d未验证且null、`c<初始先验`；不是 `a>b>c>d` 的四数值排序）。

# WP-8c2 三态重跑校准

来源：INFERRED（既有人工答案/判分复核、真实CLI重放、诊断计算）。**数值契约通过，但“四维独立、只删边界”的语义校准不通过。** b正文仍有范围限制的残留，指定 `absent_asked` 标签有判分歧义，不能把10/10解释为rubric已获独立验证。

## 方法与证据

- 直接读取[上一轮报告](report.md)、[既有答案](answers/)、[原判分与session](sessions/)、[三态契约](../references/judge.md)及引擎顶部常量。40份答案未重写，旧session未覆盖；节点与10题选择沿用[原选题](selection/selected.json)。每题只评原先选定主节点，不把错误平摊给融合题其他节点。
- [replay.py](rerun/replay.py) 每份均真实执行 `init --graph data/concepts.yaml --scenarios data/scenarios.yaml`、`score --scenario … --nodes <主节点> --question-type boundary --probe direct`、`report-data`，共120次CLI、40次接受。[commands.jsonl](rerun/commands.jsonl)是运行当场捕获的完整命令、返回码、stdout/stderr，不是事后重建。每个新 `rerun/<情景>-<变体>/` 保存 judgment、accepted、state、report-data。
- **先核对asks再提交**：[eligibility.json](rerun/eligibility.json)记录10题实际初始化后的asks，全部含boundary；无排除情景。并非只依赖question-type绕过准入。
- a保留四维3和逐字引文；b维持原辨识3/机制3/应用2，仅按任务指定将边界由U改为absent_asked；c保留原辨识2、机制0、应用逐题0/1/2、边界2，c确实都有边界段，无需改成遗漏。d四维U正式提交，不以先验冒充p_mastery。没有为排序改分或更换常量。
- scored引文逐字核对；a边界均引用主动划失效范围的第三段；两框架保留在judgment中，是同一评审的正向锚点/反向机制检查，不是独立评审。c因果错误的逐题反证沿用[原报告](report.md#人工判分与证据定位)。没有≥2整数分差；b的**状态语义争议**另见下文，不能由框架复制消除。
- [results.json](rerun/results.json)为真实report-data提取值，[checks.json](rerun/checks.json)为逐情景断言结果。[protected-hashes.json](rerun/protected-hashes.json)及[只读验证输出](rerun/validation.txt)证明受保护文件逐字未变（排除Python缓存）。未改engine/references/data/docs、真实sessions、答案、旧会话或选题文件。

## 10×4结果

S3=`scored 3`，A=`absent_asked`（没有整数分），U=`unverified`（没有整数分）。次序：辨识 / 机制 / 应用 / 边界。下表短名均指 `scen_wp1b_<短名>`；p仅主节点；精确值及节点名见results。d的null不是0，不能与c比较大小。

| 情景 | 答案 | 辨识 | 机制 | 应用 | 边界 | p_mastery | status |
|---|---|---|---|---|---|---:|---|
| preference | a | S3 | S3 | S3 | S3 | 0.822018 | scored |
| preference | b | S3 | S3 | S2 | A | 0.459172 | scored |
| preference | c | S2 | S0 | S2 | S2 | 0.000000 | scored |
| preference | d | U | U | U | U | null | unverified |
| dpo | a | S3 | S3 | S3 | S3 | 0.852415 | scored |
| dpo | b | S3 | S3 | S2 | A | 0.515984 | scored |
| dpo | c | S2 | S0 | S2 | S2 | 0.000000 | scored |
| dpo | d | U | U | U | U | null | unverified |
| function | a | S3 | S3 | S3 | S3 | 0.822047 | scored |
| function | b | S3 | S3 | S2 | A | 0.459221 | scored |
| function | c | S2 | S0 | S0 | S2 | 0.000000 | scored |
| function | d | U | U | U | U | null | unverified |
| loop | a | S3 | S3 | S3 | S3 | 0.822047 | scored |
| loop | b | S3 | S3 | S2 | A | 0.459221 | scored |
| loop | c | S2 | S0 | S1 | S2 | 0.000000 | scored |
| loop | d | U | U | U | U | null | unverified |
| vlm | a | S3 | S3 | S3 | S3 | 0.839083 | scored |
| vlm | b | S3 | S3 | S2 | A | 0.489994 | scored |
| vlm | c | S2 | S0 | S2 | S2 | 0.000000 | scored |
| vlm | d | U | U | U | U | null | unverified |
| clip | a | S3 | S3 | S3 | S3 | 0.822023 | scored |
| clip | b | S3 | S3 | S2 | A | 0.459180 | scored |
| clip | c | S2 | S0 | S0 | S2 | 0.000000 | scored |
| clip | d | U | U | U | U | null | unverified |
| flash | a | S3 | S3 | S3 | S3 | 0.838991 | scored |
| flash | b | S3 | S3 | S2 | A | 0.489822 | scored |
| flash | c | S2 | S0 | S2 | S2 | 0.000000 | scored |
| flash | d | U | U | U | U | null | unverified |
| kv | a | S3 | S3 | S3 | S3 | 0.838192 | scored |
| kv | b | S3 | S3 | S2 | A | 0.488320 | scored |
| kv | c | S2 | S0 | S2 | S2 | 0.000000 | scored |
| kv | d | U | U | U | U | null | unverified |
| pretrain | a | S3 | S3 | S3 | S3 | 0.818758 | scored |
| pretrain | b | S3 | S3 | S2 | A | 0.453571 | scored |
| pretrain | c | S2 | S0 | S2 | S2 | 0.000000 | scored |
| pretrain | d | U | U | U | U | null | unverified |
| sft | a | S3 | S3 | S3 | S3 | 0.839983 | scored |
| sft | b | S3 | S3 | S2 | A | 0.491694 | scored |
| sft | c | S2 | S0 | S2 | S2 | 0.000000 | scored |
| sft | d | U | U | U | U | null | unverified |

## 断言与不通过项诊断/处置

数值断言没有不通过项：a>b>c的非null比较10/10，d的null且unverified为10/10，c低于同节点初始化先验10/10（[逐题检查](rerun/checks.json)）。每份只有一条历史；d提交前后潜在分布不变。

但以下质量项**不通过**，不能用数值通过掩盖：

| 项目 / 涉及情景 | 诊断类别 | 证据与处置 |
|---|---|---|
| 独立边界消融：全部10题 | 情景/答案构造缺陷（非原题必然有错） | b应用均由3降2；删掉了故障识别/调整，与边界重叠。保留原分，不抬回3；见分解表。|
| b边界确实“没谈”：至少clip、loop、kv、vlm | 判分有分歧 / 消融不彻底 | clip仍说“因此无法从一个类别分唯一反推位置”；loop仍说“可使扩窗与否不再决定授权是否生效”；kv仍说“远超80GiB减14GiB权重后的66GiB”；vlm仍说“整图一味改措辞不会增加像素”。这些可被另一评审视作失效范围/原因证据。按任务强制b标签执行，但不声称它是无争议的合法语义判分；未重写答案、未改整数分、未把残留另行算分。未来需独立评审确认“缺的是专门边界段”还是“整维缺失”。|
| c的细分排序：全部10题 | 闸门 | 机制0将operable/deep质量截断为0，应用0/1/2与边界2的不同均被遮蔽。符合本轮c<prior，不证明能区分不同程度的错误。保留闸门；不靠改参数制造分辨率。|

**ABSENT_ZERO_WEIGHT保持0.5，不建议新值。** 本轮没有反转可归因于遗漏倍率；b均仍高于初始先验，遗漏不等于判错。没有额外做参数搜索，也没有证据支持“最优倍率”。这里的0.5是独立遗漏核与0分核的混合权重，不是把后验乘0.5。数值通过受机制0硬闸门帮助，不能拿十个零点反推倍率合理性或普适性。

## b相对a落差分解：不独立

缺失态没有rubric整数，不能写成“边界3→0、总分差4”。可直接确认的观测变化是：辨识3→3、机制3→3、应用3→2（十题合计少10分），边界S3→A（十次状态变化）。

为给出p_mastery落差各维占比，采用两因素Shapley：令f00为a、f10仅应用3→2、f01仅边界S3→A、f11为b。应用贡献=[(f00−f10)+(f01−f11)]/2；边界贡献=[(f00−f01)+(f10−f11)]/2。平均两种顺序，避免把非线性交互全算给最后一维。辨识/机制未变所以归因0。诊断使用当前未改引擎 `score` 在初始化state的内存副本上计算，不向正式session提交反事实、不声称混合向量对应真实新答案。[decomposition.json](rerun/decomposition.json)保存四个f值与分解；逐行验证和实际a−b相等。

| 情景 | 总落差 Δp | 辨识贡献/占比 | 机制贡献/占比 | 应用贡献/占比 | 边界贡献/占比 |
|---|---:|---:|---:|---:|---:|
| preference | 0.362846 | 0 / 0% | 0 / 0% | 0.105542 / 29.09% | 0.257304 / 70.91% |
| dpo | 0.336431 | 0 / 0% | 0 / 0% | 0.098178 / 29.18% | 0.238253 / 70.82% |
| function | 0.362825 | 0 / 0% | 0 / 0% | 0.105536 / 29.09% | 0.257289 / 70.91% |
| loop | 0.362825 | 0 / 0% | 0 / 0% | 0.105536 / 29.09% | 0.257289 / 70.91% |
| vlm | 0.349088 | 0 / 0% | 0 / 0% | 0.101701 / 29.13% | 0.247388 / 70.87% |
| clip | 0.362843 | 0 / 0% | 0 / 0% | 0.105541 / 29.09% | 0.257301 / 70.91% |
| flash | 0.349169 | 0 / 0% | 0 / 0% | 0.101723 / 29.13% | 0.247446 / 70.87% |
| kv | 0.349872 | 0 / 0% | 0 / 0% | 0.101919 / 29.13% | 0.247953 / 70.87% |
| pretrain | 0.365187 | 0 / 0% | 0 / 0% | 0.106199 / 29.08% | 0.258989 / 70.92% |
| sft | 0.348289 | 0 / 0% | 0 / 0% | 0.101478 / 29.14% | 0.246811 / 70.86% |
| 合计 | 3.549376 | 0 / 0% | 0 / 0% | 1.033354 / 29.11% | 2.516022 / 70.89% |

**约29%的后验落差不在边界维，而在应用维。** 边界是多数贡献，但并非单维集中/正交干预；按本轮校准目的，“四维不独立”的旧问题仍存在，不能报告为已解决。此为给定标签的引擎归因，不是现实认知能力的统计因果独立性检验。

## 必然失效类型与反例

1. **若要求把不知道排成更低的第四个数，当前链必然做不到**：本轮preference-c机制错误，p=0；同题d只有“我不知道”，p=null。null不能小于0，也不能偷偷用约0.396的潜在先验替代。三态解决了表示问题，正确做法是保持偏序，不是宣称四个后验严格递减。
2. **只给症状却要求唯一错因时不能可靠评分机制**：例如只说“注意力近似one-hot”，答“温度很低”与答“遗漏缩放”都可能解释，题面没给温度/缩放实值就无法排除其一。若评分链强迫对照唯一expected_element判另一答案机制0，将产生假阴性。正确契约应unverified或按列出候选辨识判分，不调常量。本轮c不是这种情况，c包含显式错误的一般因果断言。
3. **机制0闸门不保留错误答案的掌握细分**：function-c应用0与flash-c应用2，均p=0，即使应用方案可执行程度不同，也无法用这个单一p比较。若产品要求此类细粒度排序，现有输出指标必然失效；本轮只要求c低于先验，无需绕过。

## 复核、运行与残余风险

本次运行：`python3 calibration/rerun/replay.py`（40份独立初始化，40次接受，完整契约10/10）。首次运行后脚本拒绝覆盖已有commands日志；不要直接再次运行覆盖工件。当前工件只读验收：

```sh
python3 calibration/rerun/validate.py
```

[捕获输出](rerun/validation.txt)：40个单观察session、120次成功CLI、逐字引文、10/10各项断言、保护文件哈希不变、d潜在分布不变、分解加和一致。无需安装新依赖，本轮未改构建或运行环境。只运行校准与工件验收，未重跑全引擎测试（无引擎改动）。

限制：既有答案来源偏差保留，人工构造/同作者评分/知道要点，非盲测、非真实模型错误分布；不能给出准确率或总体校准率。只测单节点、单次直接证据与极端a/c向量，不涵盖补答、机制1、边界临界分、多轮恢复。b的边界状态服从指定实验操作但文本残留使其语义有效性存疑；独立评审前只能交付**条件性的数值通过**，不是完整评分链的外部效度认证。无常量/rubric/data改动，也不请求用调参修复这些构造/归因问题。
