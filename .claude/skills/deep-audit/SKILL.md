---
name: deep-audit
description: |
  对整个仓库基础设施进行深度一致性审计。
  启动 4 个并行专家代理,查找事实错误、代码缺陷、
  计数不匹配以及跨文档不一致。随后修复所有问题,
  并循环直至干净。
  使用时机:在进行广泛改动之后、发布之前,或用户说
  "audit"、"find inconsistencies"、"check everything" 时。
author: Claude Code Academic Workflow
version: 1.0.0
allowed-tools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep", "Task"]
---

# /deep-audit —— 仓库基础设施审计

对整个仓库执行全面的一致性审计,修复所有发现的问题,并循环直至干净。

## 何时使用

- 在广泛改动之后(新增技能、规则、钩子、指南编辑)
- 在发布或重要提交之前
- 当用户要求 "find inconsistencies"、"audit" 或 "check everything" 时

## 工作流

### 阶段 1:启动 4 个并行审计代理

使用 `Task` 并设置 `subagent_type=general-purpose`,同时启动以下 4 个代理:

#### 代理 1:指南内容准确性
重点关注:`guide/workflow-guide.qmd`
- 所有数值陈述与现实一致(技能数、代理数、规则数、钩子数)
- 提到的所有文件路径确实存在于磁盘上
- 所有技能/代理/规则名称与实际目录名一致
- 代码示例语法正确
- 交叉引用与锚点可解析
- 没有来自旧版本的过时计数

#### 代理 2:钩子代码质量
重点关注:`.claude/hooks/*.py` 与 `.claude/hooks/*.sh`
- 不再使用 `/tmp/`(应使用 `~/.claude/sessions/`)
- 哈希长度一致(所有钩子均为 `[:8]`)
- 正确的错误处理(fail-open 模式:顶层 `try/except` 配合 `sys.exit(0)`)
- JSON 输入/输出正确(输入用 stdin,输出用 stdout/stderr)
- 退出码正确(非阻塞用 0,仅在有意阻塞时用非零)
- 使用 `from __future__ import annotations` 以兼容 Python 3.8+
- 钩子输入 schema 的字段名正确(SessionStart 用 `source` 而非 `type`)
- PreCompact 钩子向 stderr 打印(stdout 会被忽略)

#### 代理 3:技能与规则一致性
重点关注:`.claude/skills/*/SKILL.md` 与 `.claude/rules/*.md`
- 所有文件具有有效的 YAML frontmatter
- 没有过时的 `disable-model-invocation: true`
- `allowed-tools` 取值合理
- 规则的 `paths:` 引用存在的目录
- 规则之间没有矛盾
- CLAUDE.md 中的技能表与实际技能目录一一对应
- 规则/指南中引用的所有模板都存在于 `templates/`

#### 代理 4:跨文档一致性
重点关注:`README.md`、`docs/index.html`、`docs/workflow-guide.html`
- 三份文档中的所有功能计数一致
- 所有链接指向有效目标
- 许可证部分与 LICENSE 文件一致
- 目录树与实际结构匹配
- 没有来自旧版本的过时计数

### 阶段 2:分类发现

对每个发现分类:
- **真实缺陷**:立即修复
- **误报**:丢弃(记录误报原因,供后续轮次参考)

需注意的常见误报:
- `:::` div 中的 Quarto callout `## Title` —— 这是标准语法,不是标题错误
- `allowed-tools` linter 警告 —— 已知 linter 缺陷(Claude Code issue #25380),该字段是有效的
- 旧会话日志中的计数 —— 这些是历史记录,并非面向用户的文档

### 阶段 3:修复所有问题

尽可能并行应用修复。对每项修复:
1. 先读取文件(Edit 工具要求)
2. 应用修复
3. 验证修复(用 grep 查找过时值,检查语法)

### 阶段 4:若指南有改动则重新渲染

如果 `guide/workflow-guide.qmd` 被修改:
```bash
quarto render guide/workflow-guide.qmd
cp guide/workflow-guide.html docs/workflow-guide.html
```

### 阶段 5:循环或宣布干净

修复后,启动一组全新的 4 个代理进行验证。
- 若发现新问题 → 修复并再次循环
- 若没有真实问题 → 宣布干净并汇报摘要

**最多循环:5 次**(防止无限循环)

## 以往审计的关键教训

以下是 7 轮审计中发现的真实缺陷 —— 请特别检查这些:

| 缺陷模式 | 检查位置 | 出了什么问题 |
|-------------|---------------|-----------------|
| 过时计数("19 skills" → "21") | 指南、README、落地页 | 新增了技能但未更新所有提及之处 |
| 钩子退出码 | 所有 Python 钩子 | PreCompact 中退出码 2 会静默丢弃 stdout |
| 钩子字段名 | post-compact-restore.py | SessionStart 使用 `source`,而非 `type` |
| 状态存于 /tmp/ | 所有 Python 钩子 | 应使用 `~/.claude/sessions/<hash>/` |
| 哈希长度不一致 | 所有 Python 钩子 | 有些用 `[:12]`,另一些用 `[:8]` |
| 缺少 fail-open | Python 钩子的 `__main__` | 未处理的异常 → 退出码 1 → 行为混乱 |
| Python 3.10+ 语法 | 形如 `dict | None` 的类型提示 | 需要 `from __future__ import annotations` |
| 缺少目录 | quality_reports/specs/ | 规则中被引用但从未创建 |
| 常驻规则列表 | 指南 + README | meta-governance 未列入清单 |
| 仅 macOS 命令 | 技能、规则 | 使用 `open` 而无 `xdg-open` 回退 |
| 受保护文件阻断 | settings.json 编辑 | protect-files.sh 阻止 Edit/Write |

## 输出格式

每轮结束后汇报:

```
## Round N Audit Results

### Issues Found: X genuine, Y false alarms

| # | Severity | File | Issue | Status |
|---|----------|------|-------|--------|
| 1 | Critical | file.py:42 | Description | Fixed |
| 2 | Medium | file.qmd:100 | Description | Fixed |

### Verification
- [ ] No stale counts (grep confirms)
- [ ] All hooks have fail-open + future annotations
- [ ] Guide renders successfully
- [ ] docs/ updated

### Result: [CLEAN | N issues remaining]
```
