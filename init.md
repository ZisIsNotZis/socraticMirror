下面这份可以直接丢给 Agent 当实现规格。核心已经按你的意思定死：**只有一个模式**，不做 Gentle / No Offense 模式切换；`No offense` 只作为语气和 tagline，不作为模式。

---

# Socratic Mirror — 实现规格说明书

## 0. 给 Agent 的一句话

实现一个可被 Agent 加载的 skill：**通过苏格拉底式开放问答，基于显式知识体系和 rubric 动态出题，诊断用户“自以为懂”和“实际懂”之间的偏差，输出知识地图、强项、盲区、虚假掌握、脆弱掌握、学习路径和证据链。**

不是题库，不做选择题，不搞多模式。

---

## 1. 项目标识

- **项目名**：Socratic Mirror
- **repo**：`socratic-mirror`
- **主 tagline**：  
  **You think you know. Let the questions find out.**
- **副 tagline**：  
  **No offense — but your self-assessment is probably wrong.**
- **一句话定位**：  
  **AI interviews you until your real knowledge map appears.**
- **语气设定**：  
  单一模式。坦率、直接、不奉承、不模糊安慰；会毫不客气地指出“你这里其实是虚假掌握”，但不人身攻击、不辱骂。`No offense` 是气质，不是模式。

---

## 2. 核心理念

学习之前，先知道自己会什么、不会什么。  
学校里有老师告诉你，自学时没有。碎片化知识不负责给你系统化诊断。Socratic Mirror 就是那个负责追问、校准、照镜子的 AI。

它要回答的不是“你能打几分”，而是：

- 你以为自己懂什么？
- 你实际懂什么？
- 哪些是**强项**？
- 哪些是**脆弱掌握**：能说一点，但一追问就塌？
- 哪些是**虚假掌握**：自评很高，实际证据很弱？
- 哪些是**盲区**：你不知道自己不知道？
- 哪些是**被低估的强项**：你以为不会，其实会？
- 这个领域的知识体系是什么？依赖关系是什么？
- 下一步该补哪里？

分数只是副产物。核心输出是**知识地图 + 证据链 + rubric 细项 + 学习路径**。

---

## 3. 非目标

MVP 不做：

- 不做固定题库。
- 不做 ABCD 选择题。
- 不做单一总分排行榜。
- 不做多模式切换。
- 不做完整课程教学系统。
- 不做“陪你聊天式学习搭子”。
- 不假装自己绝对正确；所有判断必须带证据和不确定性。

以后可以扩展“教用户”，但 MVP 只做**诊断与梳理**。

---

## 4. 用户流程

### Step 1：Intake

AI 先问清楚：

1. 你想诊断哪个领域/主题？
2. 你的目标是什么？面试、项目、考试、自学、写作、转行？
3. 你有没有大纲、课程目录、文档、笔记、书目录、岗位要求？可选。
4. 你自认为最懂什么？最不懂什么？哪些地方“不确定自己懂不懂”？
5. 你希望诊断深度：快速扫描 / 标准诊断 / 深度追问。

输出：`session.yaml`

### Step 2：Knowledge Architect 构建知识体系

AI 先构建候选知识地图，不要直接开问。

要求：

- 每个概念节点必须有：`id`、名称、依赖、重要性、来源、rubric。
- 来源优先级：用户提供材料 > 权威大纲/公开课程目录/标准知识体系 > 模型知识。
- 如果使用模型知识，必须标注 `source_confidence: medium/low`，并请用户确认或修正。
- 不允许 Examiner 随意瞎编概念；问题必须挂在地图节点上。
- 用户确认地图后，才进入测试。

输出：`knowledge_map.yaml`

### Step 3：Examiner 动态追问

AI 主动一条条问，每次只问一个主问题，最多 2 个追问。

问题不是选择题，而是：

- “你会怎么解释这个？”
- “如果条件变成 X，你会怎么做？”
- “你怎么判断这里是否成立？”
- “你觉得这个方案哪里会坏？”
- “给我一个反例。”
- “你如何验证你的答案？”
- “你为什么这么想？”

用户自由回答。AI 根据回答继续追问或切换节点。

### Step 4：Judge 评分与证据记录

每轮回答后，Judge 根据该节点的 rubric 打分，并记录：

- 用户原话摘录
- 命中了哪些 rubric 维度
- 缺失了什么
- 是“会”、”半懂“、”虚假掌握“、”盲区“还是”被低估“
- 置信度
- 需要追问的点

输出：`evidence.jsonl`

### Step 5：Cartographer 生成报告

最终输出 `report.md`：

- 总体知识地图
- 强项
- 脆弱掌握
- 虚假掌握
- 盲区
- 被低估的强项
- 概念依赖路径
- 推荐学习顺序
- 每个节点的 rubric 细项和证据
- 下一次诊断建议

不要用一个大总分掩盖细节。总分最多作为附注。

---

## 5. 系统模块

### 5.1 Orchestrator

负责状态机：

`intake -> map_draft -> map_confirmed -> probing -> reporting -> done`

职责：

- 控制流程
- 保证一次只问一个主问题
- 控制问题数量、覆盖率和停止条件
- 防止 Examiner 偏离知识地图
- 保存 session 状态

### 5.2 Knowledge Architect

职责：

- 把领域拆成概念图
- 标注依赖关系
- 生成每个节点的 rubric
- 标注来源和置信度
- 生成初始自评表
- 给用户确认

### 5.3 Examiner

职责：

- 根据优先级选择下一个概念节点
- 动态生成开放问题
- 根据回答追问
- 不引用地图外概念出题
- 每个问题必须带：`concept_id`、`rubric_dimension`、`question_intent`

### 5.4 Judge

职责：

- 对照 rubric 评分
- 引用用户原话作为证据
- 判断掌握类型
- 给出置信度
- 指出缺失维度
- 不因为表达啰嗦就误判懂/不懂

### 5.5 Cartographer

职责：

- 汇总证据
- 生成知识地图报告
- 计算 perceived vs actual 偏差
- 生成学习路径
- 输出下一步建议

---

## 6. 知识体系与 Rubric 设计

每个概念节点建议结构：

```yaml
concept:
  id: "c_probability_bayes"
  name: "贝叶斯推断"
  dependencies: ["c_probability_basic", "c_conditional_probability"]
  importance: high
  source:
    type: "user_material | authoritative_outline | model_knowledge"
    reference: "..."
    confidence: high
  user_self_rating: "know | half_know | dont_know | unsure"
  rubric:
    - dimension: "concept_accuracy"
      levels:
        0: "无法解释或核心错误"
        1: "记住术语，但机制错误"
        2: "基本正确，但边界模糊"
        3: "准确、完整、能举例"
    - dimension: "mechanism"
    - dimension: "application"
    - dimension: "boundary_and_counterexample"
    - dimension: "transfer"
    - dimension: "metacognitive_calibration"
  evidence_required:
    - "能用自己的话解释"
    - "能处理条件变化"
    - "能给出反例或边界"
```

掌握分类：

- `solid`：自评会，证据也强
- `fragile`：自评会/半会，证据中等，一追问就塌
- `false_mastery`：自评会，证据弱
- `blindspot`：自评不会/不确定，证据也弱
- `underestimated_strength`：自评不会/不确定，证据强
- `unknown_unknown`：地图中重要但用户完全没提到的节点
- `unverified`：还没测到

---

## 7. 动态出题策略

Examiner 选下一个节点时，按优先级：

1. 前置依赖未验证的核心节点
2. 用户自评“很懂”但证据少的节点
3. 用户自评“不确定”的节点
4. 高重要性节点
5. 能暴露边界条件的概念
6. 能测试迁移的节点
7. 尚未覆盖的依赖分支

问题类型：

- 解释型：用自己的话解释
- 机制型：为什么是这样
- 应用型：这个场景你会怎么做
- 诊断型：这个方案哪里错了
- 边界型：什么时候不成立
- 反例型：给我一个反例
- 验证型：你怎么验证
- 比较型：A 和 B 何时选哪个

追问规则：

- 每个主问题最多 2 个追问
- 追问优先问“为什么”“如果条件变了”“你怎么验证”“反例是什么”
- 如果用户回答空洞，不要立刻判 0，先追问一次
- 如果用户回答很好，也不要立刻判 3，问一次边界或迁移

停止条件：

- 覆盖所有高重要性节点，或
- 达到用户选择的深度对应的问题上限，或
- 新问题不再改变知识地图判断

---

## 8. 评分原则

- rubric 维度建议 0–3 分。
- 分数只用于汇总，不是主产品。
- 每个分数必须附证据摘录。
- 不允许无证据给高分。
- 不允许因为用户自信就给高分。
- 不允许因为用户自卑就给低分。
- 表达差但理解对，应该判懂。
- 术语多但机制错，应该判虚假掌握。
- 报告里必须区分“不会”和“没测到”。

---

## 9. 输出文件

```text
sessions/<session_id>/
  session.yaml
  knowledge_map.yaml
  evidence.jsonl
  report.md
```

`session.yaml` 包含：领域、目标、材料、自评、深度、状态。  
`knowledge_map.yaml` 包含：概念图、依赖、rubric、来源。  
`evidence.jsonl` 每行一轮问答与判断。  
`report.md` 是最终人类可读报告。

---

## 10. Skill 目录建议

```text
socratic-mirror/
  README.md
  SKILL.md
  agents/
    orchestrator.md
    knowledge-architect.md
    examiner.md
    judge.md
    cartographer.md
  schemas/
    session.schema.json
    knowledge_map.schema.json
    evidence.schema.json
  templates/
    intake.md
    report.md
  examples/
    example-session/
  tests/
    acceptance.md
```

`SKILL.md` 必须写清楚：

- 何时触发
- 如何开始 intake
- 如何构建知识地图
- 如何提问
- 如何评分
- 如何输出报告
- 禁止事项

---

## 11. MVP 范围

第一版只做：

- 单领域诊断
- 用户输入领域 + 可选材料
- AI 生成知识地图草稿并让用户确认
- 开放问答式动态追问
- 每节点 rubric 评分
- 最终 `report.md`
- 保存 session，可恢复

第一版不做：

- 多领域长期画像
- 教学对话
- 社区题库
- 花哨 UI
- 多模式
- 自动爬取资料

---

## 12. 验收标准

Agent 实现完后，必须通过：

1. 输入“我想诊断概率论基础”，能生成知识地图草稿并请求确认。
2. 不会一上来就问选择题。
3. 每次只问一个主问题。
4. 问题能追溯到 `concept_id` 和 rubric 维度。
5. 用户回答后，能记录证据并追问。
6. 最终报告能区分 `solid`、`fragile`、`false_mastery`、`blindspot`、`underestimated_strength`。
7. 报告包含概念依赖路径和学习顺序。
8. 报告不突出单一总分。
9. 没有知识地图来源的概念，不能硬出题。
10. 用户说“我不知道”时，Judge 不能编造证据。
11. 整个流程只有一个语气模式。
12. README 第一屏能让人看懂：这是 AI 追问式知识盲区诊断，不是题库。

---

## 13. README 草稿

```markdown
# Socratic Mirror

**You think you know. Let the questions find out.**

No offense — but your self-assessment is probably wrong.

Socratic Mirror is an AI skill that interviews you until your real knowledge map appears. It does not give you multiple-choice quizzes. It asks you to explain, reason, apply, and defend. Then it maps what you actually know, what you only think you know, what you don’t know you don’t know, and what you underestimated in yourself.

## What it does

- Builds an explicit concept map for your target domain
- Asks open-ended questions, one at a time
- Dynamically probes your reasoning based on a rubric
- Records evidence for every judgment
- Produces a knowledge-gap report with:
  - strengths
  - fragile knowledge
  - false mastery
  - blind spots
  - underestimated strengths
  - dependency-aware learning path

## What it is not

- Not a quiz bank
- Not a multiple-choice tester
- Not a single-score ranking
- Not a chatbot that flatters you

## Core idea

Before you learn, you should know what you know and what you don’t.
In school, a teacher tells you. When you self-learn, who tells you?
Fragmented online content won’t. Socratic Mirror will.

## Status

MVP: single-domain, interview-driven knowledge diagnosis.
```

---

## 14. 给 Agent 的最终实现指令

> 请实现 `socratic-mirror` skill。只有一个模式。用 `SKILL.md` 定义触发条件、intake、知识地图构建、动态追问、rubric 评分、证据记录和报告生成。禁止选择题和固定题库。所有问题必须挂到知识地图节点和 rubric 维度。最终输出 `knowledge_map.yaml`、`evidence.jsonl`、`report.md`。语气直接、坦率、略带冒犯感但不辱骂。分数是副产物，知识地图和证据链才是主产品。