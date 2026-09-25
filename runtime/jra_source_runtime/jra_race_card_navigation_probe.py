from __future__ import annotations
import re, urllib.request, urllib.parse, http.cookiejar, json

UA="KeibaMetrics-JRA-RaceCard-Discovery-Probe/0.1"
URL="https://www.jra.go.jp/keiba/calendar2026/2026/9/0926.html"

def fetch(url, data=None):
    req=urllib.request.Request(url,data=data,headers={"User-Agent":UA,"Accept":"text/html,application/xhtml+xml;q=0.9,*/*;q=0.1","Accept-Language":"ja,en;q=0.3"})
    with OP.open(req,timeout=30) as r:
        raw=r.read(3000000)
        return str(r.geturl()),raw.decode("utf-8","replace")

jar=http.cookiejar.CookieJar()
OP=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
final,html=fetch(URL)
patterns=[
    r"doAction\([^\n]{0,300}\)",
    r"accessD\.html[^\"'<>\s]{0,220}",
    r"pw01dde01[^\"'<>\s]{0,100}",
    r"sw01ddd01[^\"'<>\s]{0,100}",
    r"CNAME[^\n]{0,250}",
]
out={"final":final,"length":len(html),"cookies":[c.name for c in jar],"matches":{}}
for p in patterns:
    vals=[]
    for m in re.finditer(p,html,re.I):
        v=m.group(0)
        if v not in vals: vals.append(v)
        if len(vals)>=30: break
    out["matches"][p]=vals
print(json.dumps(out,ensure_ascii=False,indent=2))
