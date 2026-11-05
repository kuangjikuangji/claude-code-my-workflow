---
name: commit
description: 直接提交 main 的个人研究项目提交流程(无 PR)。质量分 ≥80 时使用。
argument-hint: "[可选:提交信息]"
allowed-tools: ["Bash", "Read", "Glob"]
---

# 提交到 main(直接提交)

暂存改动、写描述性提交信息、直接提交并推送到 main。本项目无 PR 流程。

## 步骤

1. **检查当前状态:**

```bash
git status
git diff --stat
git log --oneline -5
```

2. **质量门槛检查:** 确认本次改动内容质量分 ≥ 80(按 `.claude/rules/quality-gates.md`);< 80 先修复阻塞项。

3. **暂存文件** — 逐文件添加(绝不用 `git add -A`):

```bash
git add <file1> <file2> ...
```

不暂存 `.claude/settings.local.json`、`data/raw/`、`data/processed/`、任何含密钥的文件。

4. **提交** — 描述性信息:

`$ARGUMENTS` 提供则原样使用;否则分析暂存改动,写解释 *为什么* 而非 *做了什么* 的信息。

```bash
git commit -m "$(cat <<'EOF'
<提交信息>
EOF
)"
```

5. **推送:**

```bash
git push origin main
```

6. **提交后生成质量报告** 至 `quality_reports/merges/YYYY-MM-DD_<主题>.md`(格式见 `templates/quality-report.md`)。

7. **汇报** 提交哈希与摘要。

## 重要

- 直接提交 main——不开分支、不建 PR
- 排除 `settings.local.json`、数据目录与敏感文件
- `$ARGUMENTS` 提供的信息原样使用
- 提交信息末尾加 `Co-Authored-By: Claude Code <noreply@anthropic.com>`
