# 给 Claude 的说明

这是制作人的「富士山登山立体图」项目。和制作人沟通一律用简体中文，少用术语。先读 `README.md` 了解全貌。

## 重新发布网页（换账号、网页丢失时）

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

发布前按 Artifact 工具的规定先完整读一遍 `site/index.html`。发布后把新网址写进 `README.md` 第一段并提交。

## 实时数据

- 主路径：GitHub Actions（`.github/workflows/update.yml`，每 30 分钟）运行 `fetch.py`，强推到 `data` 分支的 `live.json`。网页用 GitHub 连接器的 `get_file_contents`（owner `kyouhi-ctrl`、repo `fuji-live`、path `live.json`、ref `refs/heads/data`）读取，每 5 分钟检查一次；「立即更新」调用 `actions_run_trigger`（`run_workflow`，`update.yml`，ref `main`）。
- 备用路径：网页的 db 文档 `live/now`。制作人要求手动更新时，运行 `python3 fetch.py /tmp/live.json`，再用 ArtifactData `set` 写入（先 `get` 拿 version 作 `if_version`）。网页会显示两者中较新的一份。
- 网页不能直接访问外部网站（CSP），所以所有实时数据都只能经过 GitHub 连接器或 db 进来。

## 注意

- 富士見予報（fuji-san.info）的数据版权归応用気象エンジニアリング，只用于制作人个人查看；仓库保持私有，公开分享或用于视频前先征得对方同意。
- 每年登山季规则（开山日期、入山费、限流）会变：`site/index.html` 里 `ROUTES`、「整体」页的规则框和 `seasonInfo()` 写的是 2026 年的，新一季官方公布后更新。
