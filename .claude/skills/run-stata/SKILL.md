---
name: run-stata
description: 用 StataMP 批量模式运行 do 文件并检查日志(r(错误码)、assert 失败、关键系数)。高频操作封装。
argument-hint: "[do 文件名,如 01_main_did.do;可省略 .do 后缀]"
allowed-tools: ["Read", "Bash", "Grep", "Glob"]
---

# 运行 Stata do 文件

以 `-b` 批量模式运行 `code/stata/` 下的 do 文件,检查日志,汇报结果。

## 步骤

1. **定位 do 文件:** `$ARGUMENTS` 给出的文件名(自动补 `.do`);缺省列出 `code/stata/*.do` 供选择

2. **运行**(必须从 `code/stata/` 调用——`-b` 日志写入调用时 cwd):

```bash
cd /Users/zhoujingjing/my-project/code/stata && /Applications/StataNow/StataMP.app/Contents/MacOS/StataMP -b do <file>.do
```

   长任务加大 timeout(回归量大的 do 可能超 2 分钟)。

3. **检查日志**(`code/stata/<file>.log`):

```bash
grep -E "r\([1-9]" <file>.log || echo "LOG CLEAN"
grep -iE "assert|conformability" <file>.log
grep -E "^end of do-file" <file>.log
```

   - `r(` 出现 → 定位错误行与原因,报告给用户
   - assert 失败 → 样本量/假设违背,报告
   - 无 `end of do-file` → do 未跑完

4. **汇报关键输出:**
   - 主回归系数与 SE(从 log 中提取)
   - `e(N)` 样本量
   - 导出的表格文件(`tables/*.tex|csv`)是否生成

## 重要

- do 文件需符合 `stata-code-conventions.md`(头部路径块 + version 19.5),否则先修复再运行
- `.log` 与 `.do` 一同提交入库(审计痕迹)
- 若 do 依赖 ssc 包(如 reghdfe),缺包时报错并提示安装:`ssc install reghdfe`
