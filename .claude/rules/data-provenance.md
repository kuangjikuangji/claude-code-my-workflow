---
paths:
  - "data/**"
  - "code/**"
---

# 数据溯源与完整性规则

**原则:** 任何加工数据与结果数字,都必须能沿脚本链回溯到原始数据与数据字典。

---

## 1. 原始数据(raw)铁律

- `data/raw/` 只读、gitignore;**绝不直接修改** raw 内任何文件
- 每个 raw 数据集在 `data/documentation/data_dictionary.md` 有登记行:文件名、来源、获取日期、许可证、关键字段
- 数据更新(拿到新一期监测数据等)= 放入 raw 新文件/覆盖旧文件 + 更新字典,然后**重跑清洗链**,不手改 processed

## 2. 加工数据(processed)

- 由 `code/python/00_clean_*.py` 生成,gitignore;可随时删除重建
- 命名:`<主题>_<颗粒度>_<版本>.dta|csv`(如 `pollution_cityday_v1.dta`)
- 每个 processed 文件在字典中登记:产生脚本、输入、关键变换(窗口、筛选、合并键)

## 3. 数据字典(提交)

`data/documentation/data_dictionary.md` 结构:

```markdown
| 数据集 | 来源 | 位置 | 产生脚本 | 关键字段 | 更新日期 |
|--------|------|------|----------|----------|----------|
| pollution_cityday_v1 | 国家空气质量监测 | data/processed/ | 00_clean_pollution.py | city, date, pm25, aqi | YYYY-MM-DD |
```

变量级定义(处理/结果变量的精确口径——论文与代码必须一致):

```markdown
### 变量:pm25
- 定义:城市日度 PM2.5 均值(监测站算术平均,剔除 <20 天观测的城市-月)
- 单位:μg/m³ | 缺失处理:... | 对应论文符号:Y_it
```

## 4. 脚本幂等与可重建

- 清洗脚本重复运行结果一致(排序、抽样设 seed;避免依赖运行次数)
- 结果表/图一律脚本重建;`tables/`、`Figures/` 内文件不手改

## 5. 数字对账(提交前必做)

论文中每个数字必须能定位到:
1. 唯一产生脚本(`code/stata/*.do` 或 `code/python/*.py`)
2. 输出物(`code/stata/*.log` 或 `tables/*.csv|tex`)
3. 数据字典中的变量口径

对账不上的数字 = 质量门槛 -20(见 quality-gates.md)。

## 6. 合并/空间匹配特别纪律(本项目核心风险)

- 每次 `merge` 后检查 `_merge` 分布并 `assert` 预期命中率
- 距离带计算(边界距离)用整数米;带边界用 `>=` / `<` 明确定义并写入字典
- 行政区划代码跨年份变更:建立代码对照表存 `data/documentation/`,不散落各脚本
