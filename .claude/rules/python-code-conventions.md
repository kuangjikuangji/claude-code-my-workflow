---
paths:
  - "code/**/*.py"
  - "explorations/**/*.py"
  - "scripts/**/*.py"
---

# Python 代码规范

**标准:** 资深数据工程师 + 博士研究者水准

---

## 1. 可复现性

- 文件头 docstring:标题、用途、输入文件、输出文件
- 随机数:`SEED = 20251105` 常量在顶部定义一次,用 `np.random.default_rng(SEED)`;禁用全局 `np.random.seed()`
- 所有路径相对仓库根:用 `ROOT = Path(__file__).resolve().parents[2]`(code/python/ 下脚本;若脚本在 explorations/ 内则相应调整,以实际到根层级为准)
- 输出目录用 `(ROOT / "...").mkdir(parents=True, exist_ok=True)`

## 2. 数据流纪律(SSOT 铁律)

- **绝不直接修改 `data/raw/` 中的文件**;raw 只读
- 清洗脚本:读 raw → 写 processed;幂等(重复运行结果一致)
- 派生文件由脚本重建,不手改
- 每个加工数据文件在 `data/documentation/` 有对应条目(见 `data-provenance.md`)

## 3. 函数设计

- `snake_case` 命名,动词-名词模式(`clean_pollution_data`, `plot_distance_bands`)
- docstring 说明参数与返回;默认参数,无魔法数字
- 一个脚本一个职责:清洗(前缀 `00_clean_`)、制图(前缀 `plot_`)、工具(可被导入,`if __name__ == "__main__"` 守卫)

## 4. 可视化标准(见 WORKFLOW_QUICK_REF 非谈判项)

- PNG 300 DPI + PDF 双输出;Okabe-Ito / viridis 色板;英文标签;默认 6.5×4 英寸
- 图例在底部;标题简洁;所有图注明数据窗口与单位

```python
import matplotlib.pyplot as plt

# Okabe-Ito palette (colorblind-safe)
OKABE_ITO = ["#E69F00", "#56B4E9", "#009E73", "#F0E442",
             "#0072B2", "#D55E00", "#CC79A7", "#000000"]

def save_figure(fig, out_stem: Path) -> None:
    fig.savefig(f"{out_stem}.png", dpi=300, bbox_inches="tight")
    fig.savefig(f"{out_stem}.pdf", bbox_inches="tight")
```

## 5. 常见陷阱

| 陷阱 | 影响 | 预防 |
|------|------|------|
| `pd.read_stata` 版本兼容(新版 dta 需 `convert_categoricals=False` 或更新 pandas) | 读入失败/类型漂移 | 读入后打印 dtypes 并抽查 |
| 中文列名/值编码(GBK vs UTF-8) | 乱码 | 统一 UTF-8 读入;`encoding="utf-8"` |
| 浮点比较(距离带边界) | 边界样本归类错误 | 用 `np.isclose` 或整数米单位 |
| 直接改 raw | 毁掉唯一原始副本 | raw 目录只读纪律;脚本只写 processed |
| 未设 seed | 抽样/补全不可复现 | `np.random.default_rng(SEED)` |

## 6. 行宽与数学例外

- 标准:行 ≤ 100 字符
- **例外:数学公式行**——拆分损害可读性时允许超长,但必须:(1) 行尾注释说明数学含义(如 `# DID: Y_it = alpha_i + lambda_t + tau * (post x treated) + e_it`);(2) 出现在数值密集段
- 非数学超长行:轻微扣分(-1 ~ -2/行)

## 7. 代码质量清单

```
[ ] 文件头 docstring(标题/输入/输出)
[ ] SEED 常量 + default_rng
[ ] 路径经 ROOT 相对解析
[ ] raw 只读、processed 由脚本重建
[ ] 图:PNG+PDF 双输出、Okabe-Ito/viridis、英文标签
[ ] 注释解释 WHY 而非 WHAT
[ ] 行宽 ≤100(数学例外除外)
```
