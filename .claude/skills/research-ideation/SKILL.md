---
name: research-ideation
description: 从主题或数据集出发,生成结构化的研究问题、可检验假设与实证策略
argument-hint: "[主题、现象或数据集描述]"
allowed-tools: ["Read", "Grep", "Glob", "Write"]
---

# 研究构思

从主题、现象或数据集出发,生成结构化的研究问题、可检验假设与实证策略。

**输入:** `$ARGUMENTS` —— 一个主题(例如"最低工资对就业的影响")、一个现象(例如"企业为何在地理上集聚?"),或一段数据集描述(例如"2000-2020 年美国县级面板数据,包含污染与健康结果")。

---

## 步骤

1. **理解输入。** 阅读 `$ARGUMENTS` 及任何被引用的文件。检查 `master_supporting_docs/` 中的相关论文。检查 `.claude/rules/` 中的领域惯例。

2. **生成 3-5 个研究问题**,按从描述性到因果性的顺序排列:
   - **描述性:** 有哪些模式?(例如"X 随时间如何演变?")
   - **相关性:** 哪些因素与之相关?(例如"控制 Z 后,X 与 Y 是否相关?")
   - **因果性:** 效应是什么?(例如"X 对 Y 的因果效应是什么?")
   - **机制:** 效应为何存在?(例如"X 通过什么渠道影响 Y?")
   - **政策:** 有何含义?(例如"政策 X 是否会改善结果 Y?")

3. **为每个研究问题展开:**
   - **假设:** 带有预期符号/量级的可检验预测
   - **识别策略:** 如何建立因果性(DiD、IV、RDD、合成控制等)
   - **数据要求:** 需要哪些数据?是否可得?
   - **关键假设:** 策略有效必须满足什么条件?
   - **潜在陷阱:** 常见的识别威胁
   - **相关文献:** 2-3 篇采用类似方法的论文

4. **对问题排序**,依据可行性与贡献度。

5. **保存输出**至 `quality_reports/research_ideation_[sanitized_topic].md`

---

## 输出格式

```markdown
# Research Ideation: [Topic]

**Date:** [YYYY-MM-DD]
**Input:** [Original input]

## Overview

[1-2 paragraphs situating the topic and why it matters]

## Research Questions

### RQ1: [Question] (Feasibility: High/Medium/Low)

**Type:** Descriptive / Correlational / Causal / Mechanism / Policy

**Hypothesis:** [Testable prediction]

**Identification Strategy:**
- **Method:** [e.g., Difference-in-Differences]
- **Treatment:** [What varies and when]
- **Control group:** [Comparison units]
- **Key assumption:** [e.g., Parallel trends]

**Data Requirements:**
- [Dataset 1 — what it provides]
- [Dataset 2 — what it provides]

**Potential Pitfalls:**
1. [Threat 1 and possible mitigation]
2. [Threat 2 and possible mitigation]

**Related Work:** [Author (Year)], [Author (Year)]

---

[Repeat for RQ2-RQ5]

## Ranking

| RQ | Feasibility | Contribution | Priority |
|----|-------------|-------------|----------|
| 1  | High        | Medium      | ...      |
| 2  | Medium      | High        | ...      |

## Suggested Next Steps

1. [Most promising direction and immediate action]
2. [Data to obtain]
3. [Literature to review deeper]
```

---

## 原则

- **要有创造力但立足现实。** 超越显而易见的问题,但每条建议都必须实证可行。
- **像审稿人一样思考。** 对每个因果问题,立即识别其识别挑战。
- **考虑数据可得性。** 没有可用数据的绝妙问题无法付诸行动。
- **尽可能建议具体数据集**(FRED、Census、PSID、行政数据等)。
