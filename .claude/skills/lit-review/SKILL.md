---
name: lit-review
description: 结构化文献检索与综合,包含引文提取与研究空白识别
argument-hint: "[主题、论文标题或研究问题]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "WebSearch", "WebFetch"]
---

# 文献综述

针对给定主题开展结构化的文献检索与综合。

**输入:** `$ARGUMENTS` —— 要考察的主题、论文标题、研究问题或现象。

---

## 步骤

1. **解析主题**:从 `$ARGUMENTS` 中解析主题。如指定了具体论文,则以该论文为锚点。

2. **检索相关工作**:使用可用工具:
   - 检查 `master_supporting_docs/supporting_papers/` 中已上传的论文
   - 使用 `WebSearch` 查找近期发表成果(如可用)
   - 使用 `WebFetch` 访问工作论文库(如可用)
   - 阅读项目中已有的 `.bib` 文件,查看已收录的论文

3. **归类发现**:归入以下类别:
   - **理论贡献** —— 模型、框架、机制
   - **实证发现** —— 关键结果、效应量、数据来源
   - **方法创新** —— 新的估计量、识别策略、推断方法
   - **未决争论** —— 文献中尚未解决的分歧

4. **识别空白与机会:**
   - 哪些问题仍未得到解答?
   - 哪些数据或方法可以回应这些问题?
   - 哪些发现相互冲突?

5. **提取引文**:以 BibTeX 格式提取所有讨论论文的引文。

6. **保存报告**至 `quality_reports/lit_review_[sanitized_topic].md`

---

## 输出格式

```markdown
# Literature Review: [Topic]

**Date:** [YYYY-MM-DD]
**Query:** [Original query from user]

## Summary

[2-3 paragraph overview of the state of the literature]

## Key Papers

### [Author (Year)] — [Short Title]
- **Main contribution:** [1-2 sentences]
- **Method:** [Identification strategy / data]
- **Key finding:** [Result with effect size if available]
- **Relevance:** [Why it matters for our research]

[Repeat for 5-15 papers, ordered by relevance]

## Thematic Organization

### Theoretical Contributions
[Grouped discussion]

### Empirical Findings
[Grouped discussion with comparison across studies]

### Methodological Innovations
[Methods relevant to the topic]

## Gaps and Opportunities

1. [Gap 1 — what's missing and why it matters]
2. [Gap 2]
3. [Gap 3]

## Suggested Next Steps

- [Concrete actions: papers to read, data to obtain, methods to consider]

## BibTeX Entries

```bibtex
@article{...}
```
```

---

## 重要事项

- **坦诚面对不确定性。** 如果无法核实某条引文,请如实说明。
- **优先关注近期工作**(过去 5-10 年),除非经典论文年代更早。
- **注明工作论文与已发表论文的区别** —— 工作论文可能发生变化。
- **不要编造引文。** 如果对某篇论文的细节不确定,请标记出来供用户核实。
