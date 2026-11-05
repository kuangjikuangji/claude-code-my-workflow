---
name: proofread
description: 对论文 .tex 运行校对协议。检查语法、拼写、布局风险、一致性、学术写作质量。只出报告不改文件。
argument-hint: "[文件名或 'all']"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Task"]
---

# 论文校对

对论文文件运行必执行的校对协议(`.claude/rules/proofreading-protocol.md`)。**只出报告,不编辑任何源文件。** 修复在用户批准后另行应用。

## 步骤

1. **确定校对对象:**
   - `$ARGUMENTS` 为具体文件名:只校对该文件
   - `$ARGUMENTS` 为 "all":校对 `paper/` 下所有 `.tex`

2. **对每个文件启动 proofreader 代理**,检查:

   **语法:** 主谓一致、冠词、介词、时态
   **拼写:** 错拼、替换损坏、重复词
   **布局风险:** 表格超宽、长公式拆分建议(本机无编译,最终以 Overleaf 为准)
   **一致性:** 引用格式、符号、术语、数字格式
   **学术质量:** 非正式缩写、缺词、拗口表达、无引用的论断
   **数字对账:** 正文数字可溯源到 `code/stata/*.log` 或 `tables/`

3. **逐文件产出详细报告**,每处发现包含:
   - 位置(行号或小节)
   - 原文(哪里错)
   - 建议(应改成什么)
   - 类别与严重度

4. **保存报告**至 `quality_reports/`:
   - `quality_reports/paper_proofread_report.md`

5. **重要:不编辑任何源文件。**
   只出报告;用户审阅批准后再应用。

6. **向用户呈交摘要:**
   - 每文件问题总数
   - 按类别分布
   - 突出最严重问题
