# code/stata/ — Stata do 文件与批处理日志

- 规范:`.claude/rules/stata-code-conventions.md`
- 运行:从本目录调用 `cd code/stata && /Applications/StataNow/StataMP.app/Contents/MacOS/StataMP -b do <file>.do`(或 `/run-stata`)
- do 文件头部必须带路径块(cd + global root)——macOS 下 Stata 不继承 shell cwd
- `.log` 与 `.do` 一同提交(审计痕迹)
- 输出表:`../tables/`(esttab,booktabs + notes)
