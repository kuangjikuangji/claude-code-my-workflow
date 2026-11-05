---
name: data-analysis
description: Python + Stata 端到端数据分析流程:清洗 → EDA → Stata 主回归 → 出版级表格与图
argument-hint: "[数据路径或分析目标描述]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash", "Task"]
---

# 数据分析工作流(Python + Stata)

端到端分析:Python 清洗与探索 → Stata 主回归 → 出版级输出。

**输入:** `$ARGUMENTS` — 数据路径(如 `data/raw/pollution.csv`)或分析目标描述(如「城市日度污染面板对公共数据开放上线的 DID」)。

---

## 约束

- **先读** `.claude/rules/data-provenance.md` 与知识库 `.claude/rules/knowledge-base-template.md`(变量口径、识别设定)
- 清洗脚本存 `code/python/00_clean_*.py`,遵循 `.claude/rules/python-code-conventions.md`
- 回归脚本存 `code/stata/*.do`,遵循 `.claude/rules/stata-code-conventions.md`
- 输出:表 → `tables/`;图 → `Figures/`;加工数据 → `data/processed/`
- **raw 只读**;结果数字可溯源(SSOT 铁律)
- 完成后跑 code-reviewer 评审生成的脚本

---

## 工作流阶段

### 阶段 1:设定与数据加载(Python)

1. 读知识库确认变量口径与识别设定
2. 写清洗脚本:`data/raw/*` → `data/processed/*.dta`,文件头 docstring 齐全
3. 幂等;每次 merge 后检查 `_merge`/命中率
4. 更新 `data/documentation/data_dictionary.md`

### 阶段 2:探索性分析(Python,图输出)

- **描述统计:** 缺失率、变量类型、分布
- **趋势:** 面板数据画时间趋势
- **组间对比:** 处理/对照的处理前均值
- **平衡性:** 处理前组间协变量差异
- 图存 `Figures/`(PNG+PDF 双输出)

### 阶段 3:主回归(Stata)

- do 文件头部完整(version 19.5、路径块、seed 如需)
- 基准 DID → 加控制 → 异质性(四分组 × 距离带)
- 标准误:城市层级聚类(默认,与识别层级一致);变更须注明
- 事件研究/平行趋势必做
- 关键回归后 `e(N)`/`assert` 检查
- 运行:`cd code/stata && /Applications/StataNow/StataMP.app/Contents/MacOS/StataMP -b do <file>.do`

### 阶段 4:出版级输出(Stata)

**表:** `esttab` 导出 `tables/*.tex`(booktabs、系数/SE/星号/N、notes 注明 SE 与聚类)
**图:** Python 按图标准产出(PNG 300 DPI + PDF、Okabe-Ito/viridis、英文标签)

### 阶段 5:保存与评审

1. 验证:`code/stata/*.log` 无 `r(` 错误;`e(N)` 正确(见 verification-protocol)
2. 跑 code-reviewer 评审生成的脚本:

```
委派 code-reviewer 代理:
"评审 code/python/[script].py 与 code/stata/[script].do"
```

3. 修复 CRITICAL/MAJOR 问题后复评

---

## 脚本结构模板

```python
# ============================================================
# 00_clean_pollution.py
# Purpose: raw pollution CSV -> processed city-day panel (dta)
# Inputs:  data/raw/<file>.csv
# Outputs: data/processed/pollution_cityday_v1.dta
# ============================================================
```

```stata
* ============================================================
* 01_main_did.do
* Inputs: $root/data/processed/*.dta
* Outputs: $root/tables/main_did.tex
* ============================================================
version 19.5
clear all
cd "/Users/zhoujingjing/my-project/code/stata"
global root "/Users/zhoujingjing/my-project"
```

---

## 重要

- **先复制,后扩展。** 复刻目标数字有复制协议(`replication-protocol.md`)
- **展示过程。** 回归前先出描述统计
- **查问题。** 共线性、异常值、完美预测、静默丢样本
- **相对路径。** 经 `$root` / ROOT 解析;绝对路径仅限头部块
- **无魔数。** 样本限制、窗口、距离带切点用头部宏/常量
