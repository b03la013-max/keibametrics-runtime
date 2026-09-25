from __future__ import annotations
import re,urllib.request,urllib.parse,http.cookiejar,json
UA="KeibaMetrics-JRA-RaceCard-Discovery-Probe/0.2"
CAL="https://www.jra.go.jp/keiba/calendar2026/2026/9/0926.html"
BASE="https://www.jra.go.jp"

jar=http.cookiejar.CookieJar()
OP=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

def fetch(url,data=None):
    req=urllib.request.Request(url,data=data,headers={"User-Agent":UA,"Accept":"text/html,application/xhtml+xml;q=0.9,*/*;q=0.1","Accept-Language":"ja,en;q=0.3","Referer":CAL})
    with OP.open(req,timeout=30) as r:
        raw=r.read(3000000)
        return str(r.geturl()),raw.decode("utf-8","replace"),int(getattr(r,"status",200))

def matches(html):
    pats=[r"doAction\([^\n]{0,350}\)",r"pw01dde01[^\"'<>\s]{0,160}",r"pw01d[^\"'<>\s]{0,160}",r"sw01ddd01[^\"'<>\s]{0,160}"]
    out={}
    for p in pats:
        vals=[]
        for m in re.finditer(p,html,re.I):
            v=m.group(0)
            if v not in vals: vals.append(v)
            if len(vals)>=80: break
        out[p]=vals
    return out

f,h,s=fetch(CAL)
entry=re.search(r"doAction\('/JRADB/accessD\.html'\s*,\s*'([^']+)'\)",h)
if not entry: raise SystemExit("ENTRY_NOT_FOUND")
token=entry.group(1)
attempts=[]
for key in ("cname","CNAME"):
    try:
        data=urllib.parse.urlencode({key:token}).encode()
        u,h2,s2=fetch(BASE+"/JRADB/accessD.html",data)
        attempts.append({"field":key,"url":u,"status":s2,"len":len(h2),"title":re.findall(r"<title[^>]*>(.*?)</title>",h2,re.I|re.S)[:1],"matches":matches(h2)})
    except Exception as e:
        attempts.append({"field":key,"error":type(e).__name__+":"+str(e)})
print(json.dumps({"entry_token":token,"cookies":[c.name for c in jar],"attempts":attempts},ensure_ascii=False,indent=2))
