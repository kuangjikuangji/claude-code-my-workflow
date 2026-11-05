---
name: context-status
description: |
  显示当前上下文状态与会话健康度。
  用于检查已使用多少上下文、自动压缩是否临近,以及哪些状态会被保留。
author: Claude Code Academic Workflow
version: 1.0.0
allowed-tools: ["Read", "Bash", "Glob"]
---

# /context-status —— 检查会话健康度

显示当前会话状态,包括上下文使用估计、活动计划与保留状态。

## 本技能显示的内容

1. **上下文使用估计** —— 上下文窗口已用百分比的大致估计
2. **活动计划** —— 当前计划文件及状态
3. **会话日志** —— 最近的会话日志
4. **保留状态** —— 压缩后仍会保留的内容

## 工作流

### 步骤 1:检查上下文监视器缓存

读取上下文监视器缓存以获得当前估计:

```bash
cat ~/.claude/sessions/*/context-monitor-cache.json 2>/dev/null | head -20
```

### 步骤 2:查找活动计划

```bash
ls -lt quality_reports/plans/*.md 2>/dev/null | head -3
```

### 步骤 3:查找会话日志

```bash
ls -lt quality_reports/session_logs/*.md 2>/dev/null | head -1
```

### 步骤 4:报告状态

格式化输出:

```
📊 Session Status
─────────────────────────────────
Context Usage:  ~XX% (estimated)
Auto-compact:   [approaching | not imminent]

📋 Active Plan
File:   quality_reports/plans/YYYY-MM-DD_description.md
Status: [draft | approved | in_progress | completed]
Task:   [current unchecked task or "none"]

📝 Session Log
File:   quality_reports/session_logs/YYYY-MM-DD_description.md

✓ Preservation Check
  • Pre-compact hook: [configured | missing]
  • Post-compact restore: [configured | missing]
  • Session state will be saved before compaction
```

## 说明

- 上下文百分比是基于工具调用次数的估计
- 实际压缩由 Claude Code 自动触发
- 所有重要状态都会保存到磁盘(计划、日志、MEMORY.md)
