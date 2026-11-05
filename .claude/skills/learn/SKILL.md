---
name: learn
description: |
  从当前会话中提取可复用的知识,形成持久化技能。
  适用于:当发现非显而易见的问题、创建变通方案,或开发出未来会话可受益的
  多步骤工作流时。
author: Claude Code Academic Workflow
version: 1.0.0
argument-hint: "[技能名称(kebab-case)]"
allowed-tools: ["Read", "Write", "Bash", "Glob", "Grep"]
---

# /learn —— 技能提取工作流

将非显而易见的发现提取为可跨会话持久复用的技能。

## 何时使用本技能

遇到以下情况时调用 `/learn`:

- **非显而易见的调试** —— 花费大量精力的调查,文档中并无记载
- **误导性错误** —— 错误信息有误,最终找到了真正原因
- **变通方案** —— 发现限制并以创造性方案解决
- **工具集成** —— 未记录的 API 用法或配置
- **试错过程** —— 多次尝试后才成功
- **可重复工作流** —— 你会再次执行的多步骤任务
- **面向用户的自动化** —— 用户会请求的报告、检查或流程

## 工作流阶段

### 阶段 1:评估(自我评估)

创建技能之前,先回答这些问题:

1. "我刚刚学到了什么在开始前并不显而易见的东西?"
2. "未来的我会因这些内容被记录而受益吗?"
3. "仅凭文档能否得出这个非显而易见的解决方案?"
4. "这是我愿意重复执行的多步骤工作流吗?"

**至少一个问题回答"是"才继续。**

### 阶段 2:检查已有技能

搜索相关技能以避免重复:

```bash
# Check project skills
ls .claude/skills/ 2>/dev/null

# Search for keywords
grep -r -i "KEYWORD" .claude/skills/ 2>/dev/null
```

**结果:**
- 无相关内容 → 创建新技能(继续阶段 3)
- 相同触发条件与方案 → 更新已有技能(提升版本号)
- 部分重叠 → 作为新变体更新

### 阶段 3:创建技能

在 `.claude/skills/[skill-name]/SKILL.md` 创建技能文件:

```yaml
---
name: descriptive-kebab-case-name
description: |
  [CRITICAL: Include specific triggers in the description]
  - What the skill does
  - Specific trigger conditions (exact error messages, symptoms)
  - When to use it (contexts, scenarios)
author: Claude Code Academic Workflow
version: 1.0.0
argument-hint: "[expected arguments]"  # Optional
---

# Skill Name

## Problem
[Clear problem description — what situation triggers this skill]

## Context / Trigger Conditions
[When to use — exact error messages, symptoms, scenarios]
[Be specific enough that you'd recognize it again]

## Solution
[Step-by-step solution]
[Include commands, code snippets, or workflows]

## Verification
[How to verify it worked]
[Expected output or state]

## Example
[Concrete example of the skill in action]

## References
[Documentation links, related files, or prior discussions]
```

### 阶段 4:质量门禁

定稿前,核实:

- [ ] 描述包含具体触发条件(而非含糊表述)
- [ ] 解决方案已验证可用(经过测试)
- [ ] 内容足够具体,可据以行动
- [ ] 内容足够通用,可复用
- [ ] 不含敏感信息(凭据、个人数据)
- [ ] 技能名称具有描述性,使用 kebab-case

## 输出

创建技能后,报告:

```
✓ Skill created: .claude/skills/[name]/SKILL.md
  Trigger: [when to use]
  Problem: [what it solves]
```

## 示例:创建技能

用户发现某个 R 包会静默丢弃观测值:

```markdown
---
name: fixest-missing-covariate-handling
description: |
  Handle silent observation dropping in fixest when covariates have missing values.
  Use when: estimates seem wrong, sample size unexpectedly small, or comparing
  results between packages.
author: Claude Code Academic Workflow
version: 1.0.0
---

# fixest Missing Covariate Handling

## Problem
The fixest package silently drops observations when covariates have NA values,
which can produce unexpected results when comparing to other packages.

## Context / Trigger Conditions
- Sample size in fixest is smaller than expected
- Results differ from Stata or other R packages
- Model has covariates with potential missing values

## Solution
1. Check for NA patterns before regression:
   ```r
   summary(complete.cases(data[, covariates]))
   ```
2. Explicitly handle NA values or use `na.action` parameter
3. Document the expected sample size in comments

## Verification
Compare `nobs(model)` with `nrow(data)` — difference indicates dropped obs.

## References
- fixest documentation on missing values
- [LEARN:r-code] entry in MEMORY.md
```
