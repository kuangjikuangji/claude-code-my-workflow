---
paths:
  - "code/**"
  - "paper/**"
  - "Figures/**"
  - "tables/**"
---

# 任务完成验证协议(无本地编译版)

**每个任务结束时,必须验证输出正确。** 本机无 TeX/Quarto——验证 = 运行验证 + 日志检查 + 结构检查;TeX 编译在 Overleaf。

## 对 Python 脚本

1. `cd` 到仓库根,运行 `/opt/anaconda3/bin/python3 code/python/<file>.py`
2. 无 traceback;退出码 0
3. 输出文件存在且非零字节(`data/processed/*.dta|csv`、`Figures/*.png|pdf`)
4. 抽查 2-3 个数值量级是否合理(如 PM2.5 均值在 5-200 μg/m³ 区间)

## 对 Stata do 文件

1. `cd code/stata && /Applications/StataNow/StataMP.app/Contents/MacOS/StataMP -b do <file>.do`
2. 检查 `<file>.log`:`grep -E "r\([1-9]"` 必须为空(无错误码)
3. 检查 `assert` 失败与关键回归的 `e(N)` 与预期一致
4. 输出表 `tables/*.tex|csv` 存在且包含期望的系数符号/量级
5. log 中的关键系数与论文/汇报数字一致

## 对论文 .tex(结构检查,无编译)

1. 环境闭合:`\begin{...}` 与 `\end{...}` 配对(pandoc 或正则辅助解析)
2. `\label{...}` 均有对应 `\ref{...}`(或标注为待引用);无重复 label
3. 每个 `\cite{key}` 的 key 存在于 `Bibliography_base.bib`
4. `\includegraphics` 引用的文件存在于 `Figures/`
5. 数字抽查:正文数字与 `code/stata/*.log` / `tables/` 对账
6. 最终编译在 Overleaf 完成(本地不做)

## 对图表

1. `Figures/*.png`(300 DPI)与 `*.pdf` 双格式存在
2. 读取 PNG 确认非空白/非损坏
3. 图由脚本生成(SSOT 铁律),未手改

## 常见陷阱

- **Stata cwd 错位**:必须从 `code/stata/` 调用且 do 内有路径块(见 `stata-code-conventions.md`)
- **`capture` 吞错**:log 无 r(错误)不代表回归成功——检查 `e(N)` 与表格
- **假设成功**:输出文件存在 ≠ 内容正确,必须抽查数值
- **Overleaf 漂移**:本地 .tex 与 Overleaf 版本不一致——以仓库为准,同步后核对

## 验证清单

```
[ ] Python:退出码 0、输出文件非零字节、数值量级合理
[ ] Stata:log 无 r(错误)、e(N) 正确、表格导出
[ ] .tex:环境闭合、label/ref 配对、cite 键在 bib、图表路径存在
[ ] 数字对账:论文数字可定位到 log/csv
[ ] 结果已向用户汇报
```
