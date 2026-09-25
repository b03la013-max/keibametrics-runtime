from __future__ import annotations
import re,urllib.request,urllib.parse,http.cookiejar,json,sys
sys.path.insert(0,"runtime/jra_source_runtime")
from source_acquisition import _html_tables,_html_text,_decode

UA="KeibaMetrics-JRA-RaceCard-Discovery-Probe/0.4"
CAL="https://www.jra.go.jp/keiba/calendar2026/2026/9/0926.html"
BASE="https://www.jra.go.jp"
MEETING_KEY="0620260408"; DATE="20260926"; RACE_NO=8
jar=http.cookiejar.CookieJar(); OP=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
def fetch(url,data=None,referer=None):
    h={"User-Agent":UA,"Accept":"text/html,application/xhtml+xml;q=0.9,*/*;q=0.1","Accept-Language":"ja,en;q=0.3"}
    if referer:h["Referer"]=referer
    q=urllib.request.Request(url,data=data,headers=h)
    with OP.open(q,timeout=30) as r:
        raw=r.read(5000000); return str(r.geturl()),raw,{str(k).lower():str(v) for k,v in r.headers.items()}
def post(tok,ref):
    return fetch(BASE+"/JRADB/accessD.html",urllib.parse.urlencode({"cname":tok}).encode(),ref)

u0,r0,h0=fetch(CAL); s0=_decode(r0,h0.get("content-type",""))
entry=re.search(r"doAction\('/JRADB/accessD\.html'\s*,\s*'([^']+)'\)",s0).group(1)
u1,r1,h1=post(entry,u0); s1=_decode(r1,h1.get("content-type",""))
day=re.search(r"(pw01drl00"+MEETING_KEY+DATE+r"/[0-9A-Fa-f]{2})",s1).group(1)
u2,r2,h2=post(day,u1); s2=_decode(r2,h2.get("content-type",""))
tok=re.search(r"(pw01dde01"+MEETING_KEY+f"{RACE_NO:02d}"+DATE+r"/[0-9A-Fa-f]{2})",s2).group(1)
u3,r3,h3=post(tok,u2); s3=_decode(r3,h3.get("content-type",""))
tables=_html_tables(s3)
sample=[]
for i,t in enumerate(tables):
    if not t:continue
    flat=" | ".join(" / ".join(row) for row in t[:3])
    if "馬番" in flat or "馬名" in flat or "前走" in flat or i<8:
        sample.append({"i":i,"rows":len(t),"maxcols":max(len(x) for x in t),"head":t[:4]})
        if len(sample)>=18:break
print(json.dumps({
 "entry":entry,"day":day,"race":tok,"final_url":u3,"byte_count":len(r3),
 "html_text_head":_html_text(s3)[:3000],
 "tables":sample,
 "doAction_horse_tokens":list(dict.fromkeys(re.findall(r"doAction\('/JRADB/accessU\.html'\s*,\s*'([^']+)'\)",s3)))[:30]
},ensure_ascii=False,indent=2))
