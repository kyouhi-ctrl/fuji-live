# 富士山登山立体图 · 实况数据

一个可以旋转、缩放的富士山真实地形 3D 网页：四条登山路线（吉田、须走、御殿场、富士宫）、各合目、2026 年官方山小屋、海拔剖面、按月份的常年气温，以及实时数据（山顶实测气温、各海拔预报、能不能看到富士山、火山警报、官方公告）。

- **公开网址（发给任何人都能看，不用登录）：https://kyouhi-ctrl.github.io/fuji-live/**
- 旧 Claude 账号里的网页（只有那个账号能打开）：https://claude.ai/artifact/1a8byBBTmg3gyfZyqZcbPj
- 换了 Claude 账号要接着改：见下文「换 Claude 账号」。

## 实时数据怎么来的（不消耗 Claude 额度）

GitHub 自带的定时任务（Actions，`.github/workflows/update.yml`）每天中午前后运行一次 `fetch.py`，把最新数据写到 `data` 分支的 `live.json`（只保留最新一份，仓库不会越来越大）。同一次运行还会把网页和最新数据一起发布到 GitHub Pages（公开网址）。Claude 里的网页通过 claude.ai 的 GitHub 连接读取 `live.json`；它的「立即更新」按钮会让这个定时任务马上跑一次（公开网址也会跟着更新）。

| 内容 | 来源 |
|---|---|
| 山顶和山脚（河口湖、山中湖、御殿场、富士市）实测气温、风 | 日本气象厅 AMeDAS（每 10 分钟观测） |
| 山顶、本八合目、四个五合目未来 48 小时预报 | 挪威气象局 MET Norway Locationforecast（按海拔订正） |
| 能不能看到富士山（北侧 / 南侧，未来 7 天上午 / 下午） | 富士見予報 fuji-san.info（応用気象エンジニアリング） |
| 火山警报 | 日本气象厅 |
| 官方公告 | 富士登山オフィシャルサイト |

**频率和费用**：现在是每天一次（`update.yml` 里的 `47 2 * * *`，UTC 2:47 = 日本时间 11:47；GitHub 的定时任务会排队，实际可能晚一些）。仓库是公开的，GitHub Actions 不限免费分钟数，需要时可以调高到每小时 `0 * * * *` 或每 30 分钟 `*/30 * * * *`，都不花钱。公开仓库如果连续 60 天没有任何改动，GitHub 会暂停定时任务并发邮件提醒，点邮件里的按钮就能恢复。网页上的「立即更新」随时可用。

**停用**：仓库的 Actions 页面 →「更新富士山实况」→ 右上角「…」→ Disable workflow。

## 目录

| 位置 | 内容 |
|---|---|
| `site/index.html` | 网页本体（three.js 3D 地形、面板、实况页）；同一份文件既发布到 Claude，也由 `build/make_public.py` 打包成公开网站 |
| `site/data.json` | 路线轨迹（本地米坐标）、合目、山小屋、地标 |
| `site/terrain.png` | 高程图：R×256+G = 海拔 ×10（分米），1024×990，范围 东经 138.620–138.835、北纬 35.275–35.445 |
| `site/relief.jpg` / `site/photo.jpg` | 按海拔着色的地形贴图 / 国土地理院航拍拼图 |
| `fetch.py` | 抓取实时数据，输出一个 JSON（只用 Python 标准库） |
| `build/` | 当初生成 `site/` 数据用的脚本（参考）：`tiles.py` 下载国土地理院高程和航拍瓦片 → `build_raster.py` 拼接重采样 → `build_tex.py` 生成地形贴图；`fetch_osm.sh` 下载 OpenStreetMap → `build_routes.py` 按真实登山道接出路线 → `build_places.py` 写入合目、山小屋、地标 |

## 换 Claude 账号

公开网址和每天的自动更新都在 GitHub 上，**换 Claude 账号不用做任何事**，照常能用。只有想接着改网站时才需要：

1. 新 Claude 账号连接 GitHub（和旧账号同一个 GitHub 账号 kyouhi-ctrl）。到 https://github.com/settings/installations → Claude → Configure，确认 `fuji-live` 在可访问的仓库里。
2. 新开云端会话，勾选 `kyouhi-ctrl/fuji-live`，先说一句：“读 CLAUDE.md，了解富士山项目的现状。”然后说要改什么。
3. （可选）想在 Claude 里也有一个带「立即更新」按钮的版本，就说“把富士山网页发布到 Claude 里”，会得到一个新网址。

谁能控制这个网站，取决于 GitHub 账号 kyouhi-ctrl，不取决于 Claude 账号。

## 资料来源

地形：国土地理院 数值标高模型（地理院タイル）；航拍：国土地理院 シームレス空中写真；登山道和小屋位置：© OpenStreetMap contributors（ODbL）；山小屋名单、路线距离与时间、开山日期：富士登山オフィシャルサイト（2026）；常年气温：気象庁 富士山 平年値（1991–2020）。
