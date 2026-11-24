#!/usr/bin/env python3
"""Fetch live Mt. Fuji conditions and write one JSON document (stdout path given as argv[1]).
Sources: JMA AMeDAS (observations), MET Norway locationforecast (altitude-pinned forecast),
JMA volcano warnings, fujisan-climb.jp announcements. Stdlib only."""
import json, re, sys, html, urllib.request, datetime as dt

UA = {"User-Agent": "fuji-route-viewer/1.0 (personal, non-commercial map)"}
JST = dt.timezone(dt.timedelta(hours=9))

def get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

out = {"updated": dt.datetime.now(JST).isoformat(timespec="minutes"), "errors": []}

# ---- JMA AMeDAS observations (10-minute) ----
STN = [("50066", "富士山 山顶", 3775), ("49251", "河口湖", 860), ("49256", "山中湖", 992),
       ("50136", "御殿场", 472), ("50196", "富士市", 66)]
try:
    lt = get("https://www.jma.go.jp/bosai/amedas/data/latest_time.txt").decode().strip()
    t = dt.datetime.fromisoformat(lt)
    obs = []
    for code, name, alt in STN:
        try:
            blk = f"{t:%Y%m%d}_{t.hour//3*3:02d}"
            d = json.loads(get(f"https://www.jma.go.jp/bosai/amedas/data/point/{code}/{blk}.json"))
            k = sorted(d)[-1]; v = d[k]
            g = lambda f: (v.get(f) or [None])[0]
            obs.append({"code": code, "name": name, "alt": alt,
                        "time": f"{k[0:4]}-{k[4:6]}-{k[6:8]}T{k[8:10]}:{k[10:12]}+09:00",
                        "temp": g("temp"), "min": g("minTemp"), "max": g("maxTemp"),
                        "wind": g("wind"), "wdir": g("windDirection"), "gust": g("gust"),
                        "hum": g("humidity"), "snow": g("snow")})
        except Exception as e:
            out["errors"].append(f"amedas {code}: {e}")
    out["obs"] = obs
except Exception as e:
    out["errors"].append(f"amedas: {e}")

# ---- MET Norway forecast at fixed altitudes ----
PTS = [("summit", "山顶 剑峰", 35.3606, 138.7274, 3776),
       ("Y", "吉田 五合目", 35.3946, 138.7333, 2305),
       ("S", "须走 五合目", 35.3657, 138.7784, 2000),
       ("G", "御殿场 新五合目", 35.3357, 138.7952, 1440),
       ("F", "富士宫 五合目", 35.3369, 138.7330, 2400),
       ("h8", "本八合目", 35.3690, 138.7390, 3400)]
fc = []
for pid, name, la, lo, alt in PTS:
    try:
        d = json.loads(get(f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={la}&lon={lo}&altitude={alt}"))
        ser = []
        for ts in d["properties"]["timeseries"][:54]:
            i = ts["data"]["instant"]["details"]; n1 = ts["data"].get("next_1_hours") or ts["data"].get("next_6_hours") or {}
            ser.append([ts["time"][:13], round(i["air_temperature"], 1), round(i["wind_speed"], 1),
                        round(i.get("wind_from_direction", 0)), round(i.get("cloud_area_fraction", 0)),
                        (n1.get("details") or {}).get("precipitation_amount"), (n1.get("summary") or {}).get("symbol_code")])
        fc.append({"id": pid, "name": name, "alt": alt, "s": ser})
    except Exception as e:
        out["errors"].append(f"metno {pid}: {e}")
out["fc"] = fc
out["fcFields"] = ["timeUTC", "temp", "wind", "wdir", "cloud", "precip", "symbol"]

# ---- JMA volcano warning for Mt. Fuji (code 314) ----
try:
    w = json.loads(get("https://www.jma.go.jp/bosai/volcano/data/warning.json"))
    hit = None
    for e in w:
        for vi in e.get("volcanoInfos", []):
            if "対象火山" not in vi.get("type", ""): continue
            for it in vi.get("items", []):
                if any(a.get("code") == "314" for a in it.get("areas", [])):
                    hit = {"name": it.get("name"), "code": it.get("code"), "time": e.get("reportDatetime")}
    out["volcano"] = hit or {"name": "噴火予報（活火山であることに留意）", "code": "level1", "time": None}
except Exception as e:
    out["errors"].append(f"volcano: {e}")

# ---- official announcements ----
try:
    s = get("https://www.fujisan-climb.jp/info/").decode("utf-8", "ignore")
    news = []
    for m in re.finditer(r'<a[^>]+href="(https://www\.fujisan-climb\.jp/info/\d+/)"[^>]*>(.*?)</a>', s, re.S):
        t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", m.group(2)))).strip()
        mm = re.search(r"(\d{4}\.\d{2}\.\d{2})\s*/\s*(\d{2}:\d{2})\s*(.*)", t)
        if mm and m.group(1) not in [n["url"] for n in news]:
            news.append({"url": m.group(1), "date": mm.group(1), "title": mm.group(3)[:140],
                         "tag": "重要" if t.startswith("重要") else ""})
        if len(news) >= 8: break
    out["news"] = news
except Exception as e:
    out["errors"].append(f"news: {e}")

# ---- 富士見予報 (fuji-san.info, AMECS): chance of seeing Mt. Fuji, from north / south ----
try:
    fj = {}
    for side in ("N", "S"):
        rows = get(f"https://fuji-san.info/data/fdata_{side}.csv").decode("shift_jis", "ignore").splitlines()
        rows = [r.strip().split(",") for r in rows if r.strip()]
        fj["init"] = rows[0][0]
        fj[side] = [[r[0][:16], int(float(r[1]))] for r in rows[1:] if len(r) >= 2 and r[1].strip()]
    out["fujimi"] = fj
except Exception as e:
    out["errors"].append(f"fujimi: {e}")

json.dump(out, open(sys.argv[1], "w"), ensure_ascii=False, separators=(",", ":"))
if not out.get("obs") and not fc:
    print("全部数据源都失败，不覆盖旧数据", out["errors"]); sys.exit(1)
print("ok", out["updated"], "obs", len(out.get("obs", [])), "fc", len(fc), "news", len(out.get("news", [])), "errors", out["errors"])
