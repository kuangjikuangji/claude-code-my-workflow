# 会话日志

**位置:** `quality_reports/session_logs/YYYY-MM-DD_描述.md`
**模板:** `templates/session-log.md`

## 三个触发点(全部主动执行)

### 1. 计划后日志

计划批准后,立即记录:目标、方案、理由、关键上下文。

### 2. 增量日志

出现以下情况时追加 1-3 行:做出设计决策、解决问题、用户纠正某事、方案变更。不要攒批。

### 3. 会话结束日志

收尾时:高层摘要、质量分数、开放问题、阻塞项。

## 质量报告

**仅在提交 main 时生成**(本项目无分支,提交即合并)——不是每次 commit 或 PR。
用 `templates/quality-report.md` 存至 `quality_reports/merges/YYYY-MM-DD_<主题>.md`。
