---
name: interview-me
description: 交互式访谈,将研究想法正式化为包含假设与实证策略的结构化研究方案
argument-hint: "[简要主题或 'start fresh']"
allowed-tools: ["Read", "Write"]
---

# 研究访谈

通过结构化访谈,帮助研究者将研究想法正式化为具体方案。

**输入:** `$ARGUMENTS` —— 简要的主题描述,或输入 "start fresh" 进行开放式探索。

---

## 运作方式

这是一项**对话式**技能。它不立即生成报告,而是通过一次一个问题的方式开展访谈,根据回答深入追问,逐步形成结构化的研究方案。

**不要使用 AskUserQuestion。** 直接在文本回复中提问,每次一到两个问题。等待用户回答后再继续。

---

## 访谈结构

### 阶段 1:全局图景(1-2 个问题)
- "你想理解的是什么现象或谜题?"
- "为什么这很重要?谁会在意答案?"

### 阶段 2:理论动机(1-2 个问题)
- "你对 X 为何发生 / 什么驱动 Y 的直觉是什么?"
- "标准理论会如何预测?你预期会有所不同吗?"

### 阶段 3:数据与情境(1-2 个问题)
- "你能获取哪些数据,或理想情况下希望获得哪些数据?"
- "你关注的是特定背景、时间段还是制度环境?"

### 阶段 4:识别(1-2 个问题)
- "是否存在可利用的自然实验、政策变化或变异来源?"
- "对因果解释的最大威胁是什么?"

### 阶段 5:预期结果(1-2 个问题)
- "你预期会发现什么?什么结果会让你意外?"
- "这些结果对政策或理论意味着什么?"

### 阶段 6:贡献(1 个问题)
- "这与已有研究有何不同?你要填补的空白是什么?"

---

## 访谈之后

一旦获得足够信息(通常 5-8 轮交流),生成一份 **研究方案文档**:

```markdown
# Research Specification: [Title]

**Date:** [YYYY-MM-DD]
**Researcher:** [from conversation context]

## Research Question

[Clear, specific question in one sentence]

## Motivation

[2-3 paragraphs: why this matters, theoretical context, policy relevance]

## Hypothesis

[Testable prediction with expected direction]

## Empirical Strategy

- **Method:** [e.g., Difference-in-Differences with staggered adoption]
- **Treatment:** [What varies]
- **Control:** [Comparison group]
- **Key identifying assumption:** [What must hold]
- **Robustness checks:** [Pre-trends, placebo tests, etc.]

## Data

- **Primary dataset:** [Name, source, coverage]
- **Key variables:** [Treatment, outcome, controls]
- **Sample:** [Unit of observation, time period, N]

## Expected Results

[What the researcher expects to find and why]

## Contribution

[How this advances the literature — 2-3 sentences]

## Open Questions

[Issues raised during the interview that need further thought]
```

**保存至:** `quality_reports/research_spec_[sanitized_topic].md`

---

## 访谈风格

- **保持好奇,而非说教。** 你的职责是引出研究者的思考,而不是强加自己的想法。
- **温和地探询薄弱点。** 如果识别策略听起来脆弱,问 "持怀疑态度的人会如何评价……?",而不是 "这行不通,因为……"。
- **基于回答推进。** 每个问题都应承接上一个回答。
- **知道何时停止。** 如果研究者在 4-5 轮交流后已有清晰构想,就转入方案撰写。不要过度访谈。
