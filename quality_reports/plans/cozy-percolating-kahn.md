# 计划:工作流配置适配——「公共数据开放对边界地区环境污染治理的影响」研究项目启动

**Date:** 2026-11-05
**Status:** COMPLETED(2026-11-05 批准并实施;第三批 MAY 项留待后续会话)

---

## Context(为什么做这件事)

本仓库 fork 自 `pedrohcgs/claude-code-my-workflow`,是一个以**讲课幻灯片(Beamer/Quarto)+ R**为中心的学术工作流模板(刚做过 template-cleanup,占位符全部未填)。用户要在此启动新研究项目:**公共数据开放对跨省/跨市边界地区环境污染治理的影响**(边界 DID 类设计:单边/双边开放异质性 × 距离带梯度 × 企业迁移),需要把所有配置适配到本项目,然后长期以「先计划后执行 → 承包商模式」协作。

**已确认决策**(用户拍板,写入了会话日志 `quality_reports/session_logs/2026-11-05_workflow-config-adaptation.md`):

| # | 决策 | 选择 |
|---|------|------|
| 1 | 工具链 | **Python + Stata 混合**(本机均有:Anaconda python3;StataNow/StataMP 全路径 `/Applications/StataNow/StataMP.app/Contents/MacOS/StataMP`,不在 PATH) |
| 2 | 产出物 | **英文期刊(SSCI/SCI)论文优先**;无汇报幻灯片需求 |
| 3 | 论文排版 | **Overleaf 编译,仓库为主**:`paper/main.tex` 存仓库为唯一事实来源,Overleaf Git 集成同步(Overleaf 侧需一次性手动设置 Main document = `paper/main.tex`) |
| 4 | 文档语言 | **配置与过程文档全中文**;代码注释与变量名英文 |
| 5 | Git | **直接提交 main**(无 PR 流程) |
| 6 | 元模板 | `meta-governance.md`、`skill-template.md`、`constitutional-governance.md` **保留英文**(面向 fork 者) |
| 7 | 机构 | **南通大学商学院**(Nantong University Business School) |
| 8 | 本机无 R/TeX/Quarto;pandoc 可用 | 本地只做结构检查与运行验证,TeX 编译在 Overleaf |

## 设计总纲

**停用 = 保留文件 + 移除触发目录**:幻灯片类规则/代理/技能文件留在 `.claude/` 内(模板资产,符合 meta-governance 双重身份),但因触发目录(`Slides/`、`Quarto/` 等)被删除而永不触发,CLAUDE.md 不再引用。**改写 = 面向项目重写内容,保留框架形态**。

### SSOT 链(替代「Beamer 权威」)

```
data/raw/                      ← 原始数据,只读权威(永不编辑,gitignore)
  └─ code/python/00_clean*.py  → data/processed/   (派生,可重建)
       └─ code/stata/*.do      → tables/*.tex|.csv + code/stata/*.log(结果权威)
       └─ code/python/*plot*.py + processed → Figures/*.png|.pdf(派生)
paper/main.tex                 ← 论文文本/设定/结论表述权威(每个数字可在 .log/.csv 定位)
```

三条铁律:(1) 每个数字/表/图有唯一产生脚本,论文数字提交前与 log 对账;(2) 派生文件(`tables/`、`Figures/`、`data/processed/`)不手改;(3) 原始数据不入库,处理脚本 + `data/documentation/` 数据字典入库。

### 目录手术

- **新增**:`data/{raw,processed,documentation}`、`code/{python,stata}`、`paper/`、`tables/`(raw/processed 入 gitignore;documentation、code、paper、tables、Figures 提交)
- **删除**(git rm,均为空 .gitkeep 占位):`Slides/`、`Quarto/`、`Preambles/`、`scripts/R/`、`master_supporting_docs/supporting_slides/`
- **保留不动**:`docs/`、`guide/`(模板 GitHub Pages 资产)、`master_supporting_docs/supporting_papers/`(lit-review 依赖)、`explorations/`(子目录约定改为 `code/{python,do}`)

## 实施步骤

### 第一批(MUST,一次提交)

**1. 核心层**
- `CLAUDE.md` 全改(中文):项目名中英双写、Institution 占位;Core Principles 改为 ①先计划(落盘 `quality_reports/plans/`)②事后验证(无 TeX:Python 运行 / Stata `-b` 日志 / .tex 结构检查)③SSOT=新链 ④质量门槛 80 ⑤[LEARN];Folder Structure 换新结构;Commands 换为 python3 全路径、`cd code/stata && /Applications/StataNow/StataMP.app/Contents/MacOS/StataMP -b do xxx.do`(日志落 code/stata/)、quality_score;删 Beamer/Quarto 两表,换「论文 LaTeX 约定」(booktabs、label 前缀 fig:/tab:/eq:/sec:、Overleaf Main document 设置说明);Current Project State 换**研究状态表**(研究问题/识别策略/数据获取状态/论文章节状态/里程碑);技能表只列启用集并注明其余为模板遗留
- `WORKFLOW_QUICK_REF.md` 中文化 + 非谈判项填充:路径约定、`SEED=20251105`(Python `np.random.default_rng` / Stata `set seed`)、图标准(PNG 300 DPI + PDF 双输出、Okabe-Ito/viridis、英文标签)、容差阈值(点估计<0.01、SE<0.05、N 精确、p 同显著性)、Stata 版本声明、直接提交 main
- `.gitignore`:加 `data/raw/`、`data/processed/`、`*.dta`、`*.smcl`、`*.stpr`;**移除通用 `*.log` 行**并注释「Stata 批处理日志有意提交」
- `.claude/settings.json` 的 `permissions.allow` 新增:`Bash(/opt/anaconda3/bin/python3 *)`、`Bash(/Applications/StataNow/StataMP.app/Contents/MacOS/StataMP *)`、`Bash(pandoc *)`、`Bash(grep *)`、`Bash(find *)`、`Bash(head *)`、`Bash(tail *)`、`Bash(cd *)`;保留既有条目;钩子与 plansDirectory 不动
- `.claude/hooks/verify-reminder.py`:VERIFY_EXTENSIONS 加 `.py`→「运行验证」、`.do`→「Stata -b 运行并检查 log」;`.tex` 文案改「结构检查(本机无 TeX,编译在 Overleaf)」

**2. 目录手术**(如上,建新删旧)

**3. 规则**(`.claude/rules/`)
- 改写(paths 与内容同步换到新目录):`single-source-of-truth.md`(新 SSOT 链 + 数字对账清单,删 TikZ/环境奇偶校验段)、`verification-protocol.md`(Python/Stata log/.tex 结构检查/图表四节,无编译版)、`quality-gates.md`(.py/.do/.tex 三张评分表:语法/ImportError -100、log 中 r(错误) -100、`capture` 无检查包关键回归 -30、缺 version 声明 -10、硬编码绝对路径 -20、缺 seed -10、读 raw 直改 raw -30、.tex 结构错误 -100、论文数字无法在 log 定位 -20;90 分改义「投稿候选」)、`replication-protocol.md`(主语言反转:原论文 R/Python → Stata 逐行复刻;R→Stata 翻译陷阱表)、`knowledge-base-template.md`(填成项目知识库:符号表、数据源清单、处理/结果变量定义、距离带定义、DID 四分组设定、论文结构-结果映射表)、`orchestrator-research.md`(paths 换 code/**;验证改为 Python 运行 + Stata log 检查)、`exploration-folder-protocol.md` + `exploration-fast-track.md`(子目录 `R/` → `code/{python,do}`)、`proofreading-protocol.md`(对象换论文 .tex;overflow 检查改为「表格超宽/长公式拆分,凭结构判断,最终编译看 Overleaf」)
- 新增:`python-code-conventions.md`(docstring 头、`Path(__file__).resolve().parents[2]` 求 repo root、seed 常量、PNG+PDF 双输出、陷阱表)、`stata-code-conventions.md`(首行 `version X` + `clear all`、UTF-8 无 BOM/LF、英文注释、全局路径宏、`-b` 从 code/stata/ 调用、关键回归后 `e(N)`/`assert`、`esttab` 导 tables/、陷阱表)、`data-provenance.md`(raw 只读、脚本幂等、数据字典随数据更新)
- 中文化(4 条常驻):`plan-first-workflow.md`、`orchestrator-protocol.md`、`session-logging.md`(quality report 改「提交 main 时生成」);`meta-governance.md` **保留英文不动**
- 停用(文件不动,路径失效):`r-code-conventions.md`、`beamer-quarto-sync.md`、`no-pause-beamer.md`、`tikz-visual-quality.md`

**4. 代理**(`.claude/agents/`)
- `domain-reviewer.md` 改写=环境经济学评审(中文):5 镜头 → ①识别假设(平行趋势、SUTVA/边界溢出、政策边界内生性、平台上线时间外生性)②DID/空间 DID 设定与距离梯度 ③引用保真 ④代码-理论对齐(.do/.py ↔ 论文)⑤反向逻辑;新增领域陷阱(监测站搬迁、企业注册地≠经营地、距离带内生性、污染测量误差、平台「试运行」日期错定)
- 新增 `code-reviewer.md`(通用 Python+Stata 评审,指令引用两条代码规范;Stata 特有项:log 检查、capture 审计、esttab 质量)
- `verifier.md` 改写(无编译版:Python 运行、Stata log 检查、.tex 结构检查、图表存在性、数字抽查对账)、`proofreader.md` 改写(对象=论文 .tex)
- 停用(文件不动):`r-reviewer.md`、`slide-auditor.md`、`pedagogy-reviewer.md`、`tikz-reviewer.md`、`beamer-translator.md`、`quarto-critic.md`、`quarto-fixer.md`

**5. 技能**(`.claude/skills/`)
- 改写:`commit`(直接提交 main:status/diff → 质量≥80 → add → commit → push origin main;删 PR 步骤)、`data-analysis`(Python 清洗→EDA→Stata -b 主回归→esttab 导 tables/→code-reviewer 评审)、`proofread`(对象=论文 .tex)、`validate-bib`(扫描范围 → `paper/**`)、`review-paper`(指令中文化)
- 中文化:`lit-review`、`research-ideation`、`interview-me`、`learn`、`context-status`、`deep-audit`
- 新增:`run-stata/SKILL.md`(参数=do 文件名;cd code/stata → StataMP 全路径 -b → grep log 中 r(/assert 失败 → 汇报关键系数)
- 停用(文件保留,CLAUDE.md 不引用):`compile-latex`、`deploy`、`extract-tikz`、`translate-to-quarto`、`qa-quarto`、`slide-excellence`、`create-lecture`、`visual-audit`、`pedagogy-review`、`devils-advocate`、`review-r`

**6. 模板与记忆**
- 中文化:`templates/session-log.md`、`requirements-spec.md`、`quality-report.md`、`exploration-readme.md`、`archive-readme.md`;`skill-template.md`、`constitutional-governance.md` 保留英文
- 新建 `.claude/state/personal-memory.md`(gitignored):机器特定事实(Stata 全路径、无 TeX/Quarto、python3 路径、Overleaf 同步约定)
- `MEMORY.md`:保留现有通用条目;加一条 `[LEARN:meta]`「路径作用域规则可通过移除触发目录停用,同时保留文件以维持模板身份」;项目状态不入 MEMORY.md(住 CLAUDE.md)

### 第二批(SHOULD)

- `scripts/quality_score.py` 扩展 PYTHON/STATA_DO/PAPER_TEX rubric(与 quality-gates.md 同步;.py 用 py_compile、.do 查 version/绝对路径/seed、.tex 正则结构检查);保留旧 rubric
- `README.md` 顶部加 3-5 行中文「本项目」区块(项目名、研究题、工具链、与模板差异),模板正文保留并注明
- `paper/main.tex` 最小骨架(Overleaf 兼容 preamble、booktabs、label 前缀)
- Stata 版本实测:用最小 do 文件 `-b` 跑 `display c(version)`,把实际版本写入 stata-code-conventions 与 CLAUDE.md

### 第三批(MAY,后续)

- `data/documentation/` 首版数据字典;lit-review 起步与 Bibliography 填充(注意 Bibliography_base.bib 受 protect-files 钩子保护,需手动编辑或临时解除);deep-audit 全量跑通

## 验证(实施后逐项执行)

1. **settings.json**:`python3 -c "import json;json.load(open('.claude/settings.json'))"` 语法校验;新增权限路径与 StataMP 实际路径逐字核对
2. **钩子冒烟**:对每个 .py 钩子喂样例 JSON stdin 验证 exit 0;protect-files.sh 喂 settings.json 编辑事件确认 exit 2;verify-reminder.py 喂 `code/stata/x.do` 确认触发
3. **Stata 冒烟**:最小 do(`version X; clear all; display "ok"`)经 `-b` 运行,确认 .log 落 code/stata/ 且无 r(错误);顺带取 `c(version)` 实测版本
4. **规则作用域自检**:grep 全部规则 frontmatter,确认停用规则 paths 无匹配文件、新规则 paths 与实际目录一致
5. **CLAUDE.md 自洽**:技能表所列技能均存在;命令中每个路径本机存在;全文 grep `[YOUR`、`Lecture` 无残留(停用资产与模板说明除外)
6. **gitignore**:`git check-ignore data/raw/x.csv` 命中;`git check-ignore code/stata/x.log` 不命中
7. 按新流程创建 `quality_reports/merges/` 质量报告并直接提交 main

## 风险与注意点

- **settings.json 语法错误**会使全部权限/钩子失效:先校验再保存,保存后新会话验证
- **Stata `-b` 的 .log 写调用时 cwd**:固化「从 code/stata/ 调用」约定(已写入 CLAUDE.md 与代码规范);do 内相对路径以 code/stata/ 为基准
- **`capture` 滥用静默吞错**:评分表与 code-reviewer 设专项检查
- **行尾/编码**:do 文件 UTF-8 无 BOM + LF;中文注释在 Stata locale 下可能乱码——代码注释保持英文(与决策一致)
- **Overleaf**:Main document 设置不随 git 同步,每次新建 Overleaf 项目需重设一次(写入 CLAUDE.md 说明)
- **`*.log` 移出 gitignore 后** pandoc 等工具产生的 log 也会入库——提交时留意
- **Bibliography_base.bib 受钩子保护**:填充文献需手动编辑或临时调整 PROTECTED_PATTERNS

## 待用户提供

- ~~机构名称~~ → 已确认:**南通大学商学院**(2026-11-05)
