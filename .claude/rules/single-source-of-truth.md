---
paths:
  - "paper/**"
  - "code/**"
  - "data/**"
  - "Figures/**"
  - "tables/**"
---

# 唯一事实来源(SSOT):执行协议

**论文 `paper/main.tex` 是文本/设定/结论表述的权威;每一个数字的权威在产生它的脚本日志中。** 其余一切派生。

## SSOT 链

```
data/raw/                      ← 原始数据,只读权威(永不编辑,gitignore)
  └─ code/python/00_clean*.py  → data/processed/        (派生,可重建)
       └─ code/stata/*.do      → tables/*.tex|.csv + code/stata/*.log(结果权威)
       └─ code/python/*plot*.py + processed → Figures/*.png|.pdf(派生)
paper/main.tex                 ← 论文文本/设定/结论表述权威(每个数字可在 .log/.csv 定位)
```

## 三条铁律

1. **每个数字/表/图有唯一产生脚本**;论文数字在提交前必须与 `code/stata/*.log` 或 `tables/` 导出对账
2. **派生文件不手改**:`tables/`、`Figures/`、`data/processed/` 一律由脚本重建
3. **原始数据不入库**:处理脚本 + `data/documentation/` 数据字典入库(见 `data-provenance.md`)

## 数字对账清单(提交前)

```
[ ] 论文正文/表/图中的每个数字 → 定位到唯一 do/py 脚本
[ ] 该数字在 .log 或导出 .csv 中找到,数值一致
[ ] 变量口径与 data/documentation 数据字典一致
[ ] 表格来自 esttab 导出,未手改
[ ] 图来自脚本,未手改
```

对账不上的数字:quality-gates 扣 20 分,修正后再提交。

## 变更传播顺序

1. 原始数据变更 → 更新数据字典 → 重跑清洗链(`00_clean_*`)
2. 加工数据/设定变更 → 改 do/py 脚本 → 重跑 → 重新导出 tables/Figures
3. 脚本产出变更 → 更新论文对应数字(与 log 对账)
4. 永不:手改派生物后反向推断源

## Overleaf 同步注意

- 仓库 `paper/` 为权威;Overleaf 是编译/协作端
- Overleaf 新建项目时手动设置 Main document = `paper/main.tex`(该设置不随 git 同步)
- 从 Overleaf 拉回的改动视为对权威的修改,按正常流程评审后提交
