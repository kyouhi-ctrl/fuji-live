#!/usr/bin/env bash
# 下载富士山一带的 OpenStreetMap 原始数据（登山道、山小屋、合目），存到 dl/osm1.xml … osm6.xml
mkdir -p dl && i=0
for lo in 138.68 138.74 138.80; do for la in 35.30 35.36; do i=$((i+1))
  hi=$(python3 -c "print(round($lo+0.06,2))"); la2=$(python3 -c "print(round($la+0.06,2))")
  curl -s -m 110 -o dl/osm$i.xml "https://api.openstreetmap.org/api/0.6/map?bbox=$lo,$la,$hi,$la2"
done; done
