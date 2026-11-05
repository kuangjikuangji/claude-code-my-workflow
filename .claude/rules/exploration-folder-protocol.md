---
paths:
  - "explorations/**"
---

# 探索目录协议

**所有实验性工作先进 `explorations/`。** 绝不直接进生产目录。

## 目录结构

```
explorations/
├── ACTIVE_PROJECTS.md
├── [project]/
│   ├── README.md          # 目标、状态、发现
│   ├── code/              # 代码(迭代用 _v1、_v2)
│   │   ├── python/        # 实验性 Python 脚本
│   │   └── do/            # 实验性 Stata do 文件
│   ├── output/            # 结果
│   └── SESSION_LOG.md     # 进度笔记
└── ARCHIVE/
    ├── completed_[project]/
    └── abandoned_[project]/
```

## 生命周期

1. **创建** — `mkdir -p explorations/[name]/code/{python,do} explorations/[name]/output` + README(用 `templates/exploration-readme.md`)
2. **开发** — 完全在探索目录内工作
3. **决策:**
   - **毕业进生产** — 复制到 `code/python/` 与 `code/stata/`;要求质量 ≥ 80、脚本跑通、代码清晰。移入 `ARCHIVE/completed_[project]/`
   - **继续探索** — README 记录下一步
   - **放弃** — 移入 `ARCHIVE/abandoned_[project]/` 并说明(用 `templates/archive-readme.md`)

## 毕业清单

- [ ] 质量分 ≥ 80
- [ ] 脚本运行通过(遵循 python/stata-code-conventions)
- [ ] 结果在容差内可复制
- [ ] 代码无需深层上下文即可读懂
- [ ] README 说明方法思路与发现
