# bots-sandbox

一个很小的任务看板服务，用来验证 bots 的自进化闭环：从报警或反馈出发，由 agent 写复现测试、修复、候选部署、入口实测、独立审核，再经人确认后发布。

- `sandbox/stats.py`：统计（每日任务数、失败率、分页）。
- `sandbox/build.py`：把 `data/tasks.json` 生成静态站点和 JSON 接口（`site/`）。
- 测试环境：GitHub Pages，<https://unfoldx-ai.github.io/bots-sandbox/>，只由 `deploy-test` workflow 写入。
- `checks/health.py`：测试环境的入口检查，由人维护；失败时 `health` workflow 开 `alarm` 标签的 issue。

本地跑测试：`python -m unittest discover -s tests -v`；本地构建：`python -m sandbox.build --sha <提交号> --ref <分支>`。

`.github/`、`checks/`、`CODEOWNERS` 由仓库负责人维护，agent 的改动不能碰这些路径；新增测试请放新文件。
