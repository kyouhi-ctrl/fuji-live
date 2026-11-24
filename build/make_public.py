#!/usr/bin/env python3
"""把 site/ 打包成可以放到 GitHub Pages 的独立网站：python3 build/make_public.py 输出目录 [live.json]"""
import os, shutil, sys
out = sys.argv[1]; live = sys.argv[2] if len(sys.argv) > 2 else None
os.makedirs(out, exist_ok=True)
page = open("site/index.html", encoding="utf-8").read()
head = """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="可旋转缩放的富士山真实地形 3D 图：吉田、须走、御殿场、富士宫四条登山路线，各合目、山小屋、海拔、气温，以及每天更新的山顶实测气温、天气预报和看山指数。">
<meta property="og:title" content="富士山登山立体图">
<meta property="og:description" content="四条登山路线、合目、山小屋、海拔与气温，可旋转缩放的真实地形 3D 图。">
<style>:root{color-scheme:light}body{margin:0;font:14px/1.5 system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>
</head><body>
"""
open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(head + page + "\n</body></html>\n")
for f in ("data.json", "terrain.png", "relief.jpg", "photo.jpg"):
    shutil.copy(os.path.join("site", f), os.path.join(out, f))
if live:
    shutil.copy(live, os.path.join(out, "live.json"))
open(os.path.join(out, ".nojekyll"), "w").close()
print("ok", sorted(os.listdir(out)))
