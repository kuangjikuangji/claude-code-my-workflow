---
paths:
  - "code/**/*.do"
  - "code/**/*.py"
---

# 复制优先协议(Stata 为主引擎)

**核心原则:** 复刻原论文结果到小数点,再谈扩展。

---

## 第一阶段:盘点与基线

写任何代码前:

- [ ] 读原论文的复制包 README
- [ ] 盘点复制包:语言、数据文件、脚本、输出
- [ ] 记录论文中的金标准数字:

```markdown
## 复制目标:Author (Year)

| 目标 | 表/图 | 数值 | SE/CI | 备注 |
|------|-------|------|-------|------|
| 主回归系数 | Table 2, Col 3 | -1.632 | (0.584) | 主设定 |
```

- [ ] 目标存至 `quality_reports/replication_targets_<AuthorYear>.md`

## 第二阶段:翻译与执行(Stata 为复刻语言)

- 原论文语言为 R/Python 时:**先用 Stata 逐行等价复刻**,不「顺手改进」
- 完全对齐原设定(协变量、样本、聚类、SE 计算)
- 中间结果存 `tables/` 或 `.dta`(本地,不入库 raw)
- 遵循 `stata-code-conventions.md`(路径块、version、seed、e(N) 检查)

### R → Stata 翻译陷阱

| R | Stata | 陷阱 |
|---|-------|------|
| `feols(y ~ x \| id, cluster = ~id)` | `reghdfe y x, absorb(id) cluster(id)` | 自由度调整与小样本修正不同,SE 可能微差 |
| `feols(y ~ x \| id + t)` 双向固定 | `reghdfe y x, absorb(id t)` | 需 `ftools`/`reghdfe`(ssc install) |
| `glm(family = binomial(link="logit"))` | `logit` | 默认链接、收敛准则不同 |
| bootstrap `R=999` | `bootstrap, reps(999)` | 种子、重数与类型需逐字对齐 |
| `lm()` 异方差稳健 | `reg, robust` | 稳健修正公式(HC1 vs HC3)不同 |

## 第三阶段:对账

容差(与 quality-gates.md 一致):点估计 < 0.01;SE < 0.05;样本量精确;p 值同显著性;百分比 < 0.1pp。

**不匹配时:不得进入扩展。** 定位差异来源(样本量、SE 计算、默认选项、变量定义),调查过程写入报告,即使未解决也要记录。

### 复制报告

存 `quality_reports/replication_report_<AuthorYear>.md`:

```markdown
# 复制报告:Author (Year)
**日期:** YYYY-MM-DD | **原语言:** R/Stata/... | **本项目脚本:** code/stata/...

## 摘要
- 目标数 / 通过 / 失败:N / M / K
- 总体:[REPLICATED / PARTIAL / FAILED]

## 结果对比
| 目标 | 论文 | 我们 | 差 | 状态 |

## 差异(若有)
- **目标:** X | **调查:** ... | **结论:** ...

## 环境
- Stata 版本、关键命令(ssc 包与版本)、数据来源
```

## 第四阶段:通过后才扩展

- [ ] 提交复制脚本:「Replicate [Paper] Table X — 全部目标通过」
- [ ] 再扩展(不同估计量、新图、边界设定变体)
- [ ] 每个扩展建立在已验证的基线上
