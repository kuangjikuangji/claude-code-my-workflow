---
name: validate-bib
description: 校验参考文献与论文引用的一致性(扫描 paper/)。找缺失条目与未用文献。
allowed-tools: ["Read", "Grep", "Glob"]
---

# 校验参考文献

交叉核对论文引用与参考文献条目。

## 步骤

1. **读参考文献文件**,提取全部引用键

2. **扫描论文文件的引用键:**
   - `.tex` 文件:找 `\cite{`、`\citet{`、`\citep{`、`\citeauthor{`、`\citeyear{`
   - 提取全部唯一引用键

3. **交叉核对:**
   - **缺失条目:** 论文引用了但 bib 中没有
   - **未用条目:** bib 中有但任何地方都没引用
   - **疑似笔误:** 相似但不匹配的键

4. **检查每个 bib 条目质量:**
   - 必需字段齐全(author、title、year、journal/booktitle)
   - author 字段格式正确
   - year 合理
   - 无乱码或编码问题

5. **报告发现:**
   - 缺失条目清单(CRITICAL)
   - 未用条目清单(信息性)
   - 疑似键笔误清单
   - 质量问题清单

## 扫描文件:
```
paper/*.tex
paper/**/*.tex
```

## 参考文献位置:
```
Bibliography_base.bib(仓库根;受 protect-files 钩子保护,本技能只读)
```
