from __future__ import annotations
import re,urllib.request,urllib.parse,http.cookiejar,json
UA="KeibaMetrics-JRA-RaceCard-Discovery-Probe/0.3"
CAL="https://www.jra.go.jp/keiba/calendar2026/2026/9/0926.html"
BASE="https://www.jra.go.jp"
MEETING_KEY="0620260408"
RACE_DATE="20260926"
RACE_NO=8

jar=http.cookiejar.CookieJar()
OP=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

def fetch(url,data=None,referer=None):
    headers={"User-Agent":UA,"Accept":"text/html,application/xhtml+xml;q=0.9,*/*;q=0.1","Accept-Language":"ja,en;q=0.3"}
    if referer: headers["Referer"]=referer
    req=urllib.request.Request(url,data=data,headers=headers)
    with OP.open(req,timeout=30) as r:
        raw=r.read(4000000)
        ctype=str(r.headers.get("content-type") or "")
        charset="utf-8"
        m=re.search(r"charset=([^; ]+)",ctype,re.I)
        if m: charset=m.group(1)
        for enc in [charset,"utf-8","cp932","shift_jis","euc_jp"]:
            try: txt=raw.decode(enc); break
            except Exception: txt=None
        if txt is None: txt=raw.decode("utf-8","replace")
        return str(r.geturl()),txt,int(getattr(r,"status",200))

def post_token(token,referer):
    return fetch(BASE+"/JRADB/accessD.html",urllib.parse.urlencode({"cname":token}).encode(),referer)

u0,h0,s0=fetch(CAL)
entry=re.search(r"doAction\('/JRADB/accessD\.html'\s*,\s*'([^']+)'\)",h0).group(1)
u1,h1,s1=post_token(entry,u0)
prefix="pw01drl00"+MEETING_KEY+RACE_DATE
day_tokens=re.findall(r"doAction\('/JRADB/accessD\.html'\s*,\s*'("+re.escape(prefix)+r"/[0-9A-Fa-f]{2})'\)",h1)
if not day_tokens:
    raise SystemExit("DAY_TOKEN_NOT_FOUND")
day=day_tokens[0]
u2,h2,s2=post_token(day,u1)
race_prefix=f"pw01dde01{MEETING_KEY}{RACE_NO:02d}{RACE_DATE}"
all_race_tokens=re.findall(r"pw01dde01\d{10}\d{2}\d{8}/[0-9A-Fa-f]{2}",h2)
race_tokens=[x for x in all_race_tokens if x.startswith(race_prefix)]
print(json.dumps({
 "entry":entry,"day":day,
 "step1":{"url":u1,"status":s1,"len":len(h1)},
 "step2":{"url":u2,"status":s2,"len":len(h2)},
 "race_token":race_tokens[:3],
 "all_race_tokens":list(dict.fromkeys(all_race_tokens))[:30],
 "cookies":[c.name for c in jar],
},ensure_ascii=False,indent=2))
