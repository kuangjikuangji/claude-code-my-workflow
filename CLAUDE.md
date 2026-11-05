# CLAUDE.MD — 学术研究项目:公共数据开放与边界地区环境治理

**项目:** 公共数据开放对边界地区环境污染治理的影响(The Impact of Public Data Openness on Environmental Pollution Governance in Border Regions)
**机构:** 南通大学商学院(Nantong University Business School)
**分支:** main(直接提交,无 PR 流程)

> 本机环境事实:Python(Anaconda)与 StataNow/StataMP 已装;**无 R、无 TeX、无 Quarto**。
> 论文 LaTeX 编译在 **Overleaf** 完成(仓库为主:源文件在 `paper/`,经 Overleaf Git 集成同步;Overleaf 侧需一次性设置 Main document = `paper/main.tex`)。本地只做结构检查与代码运行验证。

---

## 核心原则

- **先计划** — 非平凡任务先进入计划模式;计划落盘 `quality_reports/plans/`
- **事后验证** — 任务结束必须验证:Python 运行通过 / Stata `-b` 日志无错误 / .tex 结构检查;编译验证在 Overleaf
- **唯一事实来源(SSOT)** — 见下方链;派生文件绝不手改
- **质量门槛** — 低于 80/100 不提交
- **[LEARN] 标签** — 被纠正时,将 `[LEARN:类别] 错误 → 正确` 记入 MEMORY.md

---

## 唯一事实来源链

```
data/raw/                      ← 原始数据,只读权威(永不编辑,gitignore)
  └─ code/python/00_clean*.py  → data/processed/        (派生,可重建)
       └─ code/stata/*.do      → tables/*.tex|.csv + code/stata/*.log(结果权威)
       └─ code/python/*plot*.py + processed → Figures/*.png|.pdf(派生)
paper/main.tex                 ← 论文文本/设定/结论表述权威(每个数字可在 .log/.csv 定位)
```

三条铁律:
1. 每个数字/表/图有唯一产生脚本;论文数字在提交前必须与 Stata .log 或导出 .csv 对账
2. 派生文件(`tables/`、`Figures/`、`data/processed/`)不手改,一律由脚本重建
3. 原始数据不入库;处理脚本 + `data/documentation/` 数据字典入库

---

## 目录结构

```
my-project/
├── CLAUDE.MD                    # 本文件
├── .claude/                     # 规则、技能、代理、钩子(中文)
├── Bibliography_base.bib        # 集中参考文献(受钩子保护,手动编辑)
├── data/                        # 研究数据
│   ├── raw/                     # 原始数据(gitignore,只读)
│   ├── processed/               # 加工数据(gitignore,脚本重建)
│   └── documentation/           # 数据字典、来源清单(提交)
├── code/                        # 分析代码(提交)
│   ├── python/                  # 数据清洗 + 制图
│   └── stata/                   # do 文件 + 批处理 .log(提交,审计痕迹)
├── paper/                       # 论文 main.tex(Overleaf Git 集成同步)
├── Figures/                     # 论文图表输出(提交)
├── tables/                      # Stata esttab 导出表(提交)
├── explorations/                # 研究沙箱(见规则)
├── scripts/                     # 工具脚本
├── quality_reports/             # 计划、规格书、会话日志、质量报告
├── templates/                   # 中文模板
├── docs/ + guide/               # 上游模板的 GitHub Pages 资产(保留,本项目不使用)
└── master_supporting_docs/      # 论文 PDF 等支撑材料
```

---

## 常用命令

```bash
# Python(数据清洗/制图;脚本须从仓库根运行)
/opt/anaconda3/bin/python3 code/python/script.py

# Stata(必须从 code/stata/ 目录调用,-b 的 .log 写入调用时 cwd)
cd code/stata && /Applications/StataNow/StataMP.app/Contents/MacOS/StataMP -b do analysis.do

# 质量评分
python3 scripts/quality_score.py <file>

# 格式转换(仅辅助)
pandoc input.md -o output.docx
```

**验证约定:** 本机不可编译 TeX——`.tex` 改动只做结构检查(环境闭合、`\label`/`\ref` 配对、`\cite` 键在 bib 中),最终编译在 Overleaf 完成。

---

## 质量门槛

| 分数 | 门槛 | 含义 |
|------|------|------|
| 80 | 提交 | 可提交 main |
| 90 | 投稿候选 | 对外发布/投稿的候选状态 |
| 95 | 卓越 | 追求目标 |

---

## 技能速查(本项目启用集)

| 命令 | 作用 |
|------|------|
| `/commit [msg]` | 直接提交 main(≥80 分) |
| `/run-stata [file]` | StataMP `-b` 运行 do 文件并检查日志 |
| `/data-analysis [task]` | Python 清洗 → EDA → Stata 主回归端到端流程 |
| `/review-paper [file]` | 论文综合评审 |
| `/proofread [file]` | 论文校对(提议→批准→应用) |
| `/validate-bib` | 引用与参考文献交叉校验(扫描 `paper/**`) |
| `/lit-review [topic]` | 文献检索与综述 |
| `/research-ideation [topic]` | 研究问题与实证策略生成 |
| `/interview-me [topic]` | 交互式研究访谈 |
| `/learn [skill-name]` | 提取经验为持久技能 |
| `/context-status` | 会话健康与上下文用量 |
| `/deep-audit` | 仓库级一致性审计 |

其余技能为上游模板遗留(幻灯片/Quarto/R 相关),本项目不使用。

---

## 论文 LaTeX 约定

| 约定 | 说明 |
|------|------|
| 主文档 | `paper/main.tex`;Overleaf 新建项目时手动设置 Main document 指向它(该设置不随 git 同步) |
| 表格 | 一律 `booktabs`;每个表必须有 notes(SE 括号、星号显著性约定) |
| label 前缀 | `fig:` / `tab:` / `eq:` / `sec:` |
| 图表引用 | `Figures/` 相对路径,由脚本生成后引用 |
| 数值 | 论文正文数字必须来自 `code/stata/*.log` 或 `tables/`,禁止手打 |

---

## 研究状态表

| 模块 | 状态 | 关键内容 |
|------|------|----------|
| 研究问题 | 已定 | 边界地区(跨省/跨市)公共数据开放对生态环境治理的影响:污染缓解还是恶化? |
| 识别策略 | 设计阶段 | 边界 DID / 空间 DID;异质性:单边开放(上游开下游不开、反之)、双边开放、均不开放;距离带梯度;企业迁移维度(新增企业是否污染、污染企业退出与再落户、落户地数据开放与环境规制强度) |
| 数据 | 待获取 | 污染监测/卫星数据、企业注册与迁移数据、公共数据开放平台上线时间目录、行政区划与边界地理数据 |
| 论文 | 未动笔 | `paper/main.tex` 骨架;英文投稿(SSCI/SCI) |
| 当前里程碑 | 工作流配置适配(本会话) | 详见 `quality_reports/plans/` |
