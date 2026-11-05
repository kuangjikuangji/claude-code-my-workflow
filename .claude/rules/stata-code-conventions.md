---
paths:
  - "code/**/*.do"
  - "explorations/**/*.do"
---

# Stata do 文件规范

**标准:** 可复现、可审计;每张论文表可追溯到唯一 do 文件与日志

---

## 1. 文件头(每个 do 文件必须)

```stata
* ============================================================
* Title: <do 文件用途>
* Inputs: $root/data/processed/<file>.dta
* Outputs: $root/tables/<table>.tex | $root/Figures/...
* Author: <name> | Date: YYYY-MM-DD
* ============================================================
version 19.5          // 本机 StataNow 19.5(实测)
clear all
set more off
set seed 20251105     // 仅含随机成分时必需
set maxvar 10000      // 如需

* --- 路径块(机器特定绝对路径仅允许出现在此块,见 personal-memory.md) ---
cd "/Users/zhoujingjing/my-project/code/stata"        // 修正 Stata 不继承 shell cwd 的问题
global root "/Users/zhoujingjing/my-project"          // 仓库根
* -----------------------------------------------------------------
```

**为什么有路径块:** macOS 下 Stata 内部工作目录不继承 shell cwd(`c(pwd)` 会指向 `/Applications/StataNow/ado/personal`),do 内相对路径会解析错位。此块保证 do 文件从任何位置调用都行为一致。`-b` 日志写入 OS cwd,故调用时仍需 `cd code/stata`(见 /run-stata 技能)。

## 2. 调用与日志

- 调用方式:`cd code/stata && /Applications/StataNow/StataMP.app/Contents/MacOS/StataMP -b do <name>.do`
- **不再写 `log using`**:`-b` 已生成同名 .log(在 OS cwd = code/stata/)
- .log **提交入库**(审计痕迹);检查 log 中 `r(` 错误码与 `assert` 失败

## 3. 编码与行尾

- UTF-8 无 BOM、LF 行尾(Windows 复制来的 do 文件先查 CRLF)
- **注释保持英文**(中文注释在本机 locale 下可能乱码)

## 4. 稳健性

- 关键回归后必须检查:`assert e(N) == 期望样本量`(或 `di e(N)`)——静默丢样本是头号杀手
- **`capture` 不得无检查地包裹关键回归**;若必须用 capture,随后 `if _rc != 0` 显式报错
- 循环用整数步长:`forvalues` 勿用浮点步长(0.1 累加误差)
- 导出表:`esttab` → `$root/tables/*.tex`(booktabs、`star(* 0.10 ** 0.05 *** 0.01)`、notes 注明 SE 括号与聚类层级)

## 5. 聚类与推断约定(研究默认)

- 标准误默认在**城市层级**聚类(与识别层级一致);变更须在 do 注释说明理由
- 事件时间/窗口、距离带切点等关键参数定义为局部宏,集中在文件头部,禁止散落魔数

## 6. 常见陷阱

| 陷阱 | 影响 | 预防 |
|------|------|------|
| `capture` 吞掉回归失败,log 无 r(错误) | 拿到空表当结果 | 关键回归不用 capture;code-reviewer 专项审计 |
| cwd 错位(见第 1 节) | `file not found r(601)` | 头部路径块 |
| CRLF 行尾 | 神秘语法错误 | `file code/stata/x.do` 查行尾;统一 LF |
| 中文变量标签在非 UTF-8 locale | 乱码/截断 | 标签用英文 |
| `merge` 后不检查 `_merge` 分布 | 静默丢/错并 | 每次 merge 后 `tab _merge` 并 assert |
| 浮点距离带边界 | 样本归带错误 | 距离用整数米;切点用 `>=`/`<` 明确定义 |

## 7. 质量清单

```
[ ] 文件头注释块完整
[ ] version 19.5 + clear all
[ ] 路径块(cd + global root)
[ ] 随机成分含 set seed
[ ] 关键回归后 e(N)/assert 检查
[ ] 无裸 capture 包关键回归
[ ] esttab 导出 tables/(booktabs + notes)
[ ] 注释英文、UTF-8 无 BOM、LF
[ ] .log 提交且无 r(错误)
```
