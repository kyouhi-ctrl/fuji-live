# 给 Claude 的说明

这是制作人的「富士山登山立体图」项目。先读 `README.md` 了解全貌，再读本文件的「交接状态」。

## 和制作人沟通

- 一律用简体中文；少用术语，必须用时顺手解释一句。每一步说清楚在做什么、为什么。
- **在意额度**：能不花 Claude 额度的做法优先（例如更新数据用 GitHub Actions，不用 Claude 定时任务）。会持续消耗额度的事（定时任务、频繁运行）先问。
- 页面上**不写资料来源**（2026-11-24 定下：观众不关心），只在「显示」页底部留一行小字署名（OpenStreetMap、国土地理院的使用条款要求），不要删。
- 云端会话不能新建 GitHub 仓库、不能改仓库设置（公开/私有、Pages 开关），这类事情给制作人写清楚手机上怎么点。

## 交接状态（2026-11-27，制作人改用另一个 Claude 账号）

- **公开网址 https://kyouhi-ctrl.github.io/fuji-live/ 正常**：任何人不用登录就能看。由本仓库的 GitHub Actions 每天发布，和 Claude 账号无关，换账号不用做任何事。
- **自动更新**：每天一次，`update.yml` 里 `47 2 * * *`（日本时间 11:47）。GitHub 的定时任务会排队延后：2026-11-24～26 用整点 `0 3` 时实际在日本时间 20:35–21:58 才跑，11-27 改成非整点。改完后如仍明显偏晚，可再加一个备用时间（例如 `47 2,8 * * *`）。制作人说过“以后频繁使用时再提高频率”；仓库是公开的，提高频率不花钱。
- **Claude 里的网页** https://claude.ai/artifact/1a8byBBTmg3gyfZyqZcbPj 属于旧 Claude 账号，新账号打不开也改不了。新账号如需要一个带「立即更新」按钮的版本，按下面「在 Claude 里发布网页」重新发布（会是新网址），并把新网址写进 `README.md`。
- **没验证过的一处**：Claude 版网页通过 claude.ai 的 GitHub 连接器读数据、触发更新（「开启自动更新」按钮），代码里假设连接器名叫 `GitHub` 或 `github`，从没在真实页面上点过。如果制作人点了报错，用 mcp 的 `listTools()` 看真实名字，改 `site/index.html` 的 `GH_NAMES` 和发布时的 `capabilities`。公开网址不依赖这一步。
- **以后要做的**：2027 年登山季规则公布后（通常 4–6 月），更新 `site/index.html` 里的 `ROUTES`（开山日期）、「整体」页的规则框、`seasonInfo()`、山小屋名单（官方页 `https://www.fujisan-climb.jp/mountainhut_yoshida/` 等四个）。
- 富士見予報（fuji-san.info，応用気象エンジニアリング）的看山指数在公开网址上照样显示，是制作人 2026-11-24 的决定；如果要用到视频里，建议先征得对方同意。

## 改网页的流程

1. 改 `site/index.html`（或 `site/data.json` 等）。
2. 本地预览：`python3 build/make_public.py /tmp/_site <某个 live.json>`，再在 `/tmp/_site` 起一个 `python3 -m http.server`，用 Playwright 截图看一眼（手机宽度 390）。没有 live.json 时先跑 `python3 fetch.py /tmp/live.json`。
3. 提交并推到 `main`。改了 `site/`、`build/make_public.py` 或工作流文件会自动重新发布公开网址（约 1 分钟）；也可以用 GitHub 工具 `actions_run_trigger`（`run_workflow`、`update.yml`、ref `main`）手动跑。
4. 不要往 `data` 分支手动提交：每次运行都会强推覆盖。

## 在 Claude 里发布网页（可选）

用 Artifact 工具发布 `site/index.html`，同时带上同目录的数据文件：

- `file_path`: `site/index.html`
- `files`: `{"data.json": "site/data.json", "terrain.png": "site/terrain.png", "relief.jpg": "site/relief.jpg", "photo.jpg": "site/photo.jpg"}`
- `icon`: `mountain`
- `description`: 可旋转缩放的富士山真实地形 3D 图：四条登山路线、合目、山小屋、海拔剖面，以及实时天气、看山指数和官方公告。
- `capabilities`:
  ```json
  {"db": {"rules": [{"path": "", "read": "view", "write": "owner"}]},
   "mcp": {"servers": [{"server": "GitHub", "tools": ["get_file_contents", "actions_run_trigger"]},
                       {"server": "github", "tools": ["get_file_contents", "actions_run_trigger"]}]}}
  ```

发布前按 Artifact 工具的规定先完整读一遍 `site/index.html`。以后同一个账号里再改，要发布到同一个文件路径（或传 `url`），否则会生成新网址。

## 实时数据的两条路（给 Claude 里的网页）

- 主路径：网页用 GitHub 连接器的 `get_file_contents`（owner `kyouhi-ctrl`、repo `fuji-live`、path `live.json`、ref `refs/heads/data`）读取，页面开着时每 5 分钟检查一次；「立即更新」调用 `actions_run_trigger`。
- 备用路径：网页的 db 文档 `live/now`。制作人要求手动更新时，运行 `python3 fetch.py /tmp/live.json`，再用 ArtifactData `set` 写入（先 `get` 拿 version 作 `if_version`；新发布的网页第一次写时省略）。网页显示两者中较新的一份。
- Claude 网页不能直接访问外部网站（CSP），所以只能经过这两条路拿数据。公开网址没有这个限制，直接读同目录的 `live.json`。
