---
paths:
  - "code/**/*.py"
  - "code/**/*.do"
  - "paper/**/*.tex"
  - "Figures/**"
  - "tables/**"
---

# 质量门槛与评分规则

## 阈值

- **80/100 = 提交 main** — 可保存
- **90/100 = 投稿候选** — 对外发布/投稿候选
- **95/100 = 卓越** — 追求目标

## Python 脚本(.py)

| 严重度 | 问题 | 扣分 |
|--------|------|------|
| Critical | 语法错误 / ImportError(运行失败) | -100 |
| Critical | 直接修改 `data/raw/` | -30 |
| Critical | 硬编码绝对路径(ROOT 解析块除外) | -20 |
| Major | 随机成分缺 `np.random.default_rng(SEED)` | -10 |
| Major | 缺文件头 docstring(标题/输入/输出) | -5 |
| Major | 图未双输出(PNG+PDF)或非规范色板 | -5 |
| Minor | 行 > 100 字符(非数学例外) | -1/行 |

## Stata do 文件(.do)

| 严重度 | 问题 | 扣分 |
|--------|------|------|
| Critical | log 中出现 `r(` 错误码 | -100 |
| Critical | 裸 `capture` 包裹关键回归(无 `_rc` 检查) | -30 |
| Critical | 硬编码绝对路径(头部路径块除外) | -20 |
| Major | 缺 `version` 声明 / `clear all` | -10 |
| Major | 缺头部路径块(cd + global root) | -10 |
| Major | 关键回归后无 `e(N)`/`assert` 检查 | -10 |
| Major | 未导出 `tables/`(需要表格时) | -5 |
| Minor | 中文注释(编码风险) | -1/处 |

## 论文 .tex

| 严重度 | 问题 | 扣分 |
|--------|------|------|
| Critical | 结构错误(未闭合环境、未定义引用、cite 键不在 bib) | -100 |
| Critical | 数字无法在 `code/stata/*.log` 或 `tables/` 定位(违反 SSOT) | -20 |
| Major | 表格无 notes(SE 说明、星号约定) | -5 |
| Major | 符号/术语不一致 | -3 |
| Minor | 行 > 100 字符(数学公式除外) | -1/行 |

## 执行

- **< 80:** 阻止提交,列出阻塞问题
- **< 90:** 允许提交并警告,列出建议
- 用户可说明理由后豁免

## 质量报告

**仅提交 main 时生成**(本项目无分支,提交即合并)。格式见 `templates/quality-report.md`,保存至 `quality_reports/merges/YYYY-MM-DD_<主题>.md`。

## 容差阈值(复制对账)

| 量 | 容差 | 理由 |
|----|------|------|
| 点估计 | < 0.01 | 论文显示舍入 |
| 标准误 | < 0.05 | 聚类/自助法差异 |
| 样本量 | 精确一致 | 无理由有差异 |
| p 值 | 同显著性水平 | 精确 p 可微差 |
| 百分比 | < 0.1pp | 显示舍入 |
