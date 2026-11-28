"""Keibabook (中央) full-page capture -> workout / stable-comment bands (keibabook_bands.json).

The browser collector (keibabook_jra_collect.js) stores every per-race page in the PRIVATE repo. This
derives the same compact the in-session __kmCapture used ({date8, races:[{id, t, s, w}]}) from its 調教
and 厩舎の話 tables, runs the registered band rules of keibabook_bands.js (__kmBands, via node) and writes
the bands file the pack builder reads (jra_external_pack_builder.py --keibabook). Only bands leave the
private side; workout rows and trainer comments are never printed.

  python runtime/capture/keibabook_jra_bands_from_pages.py <pages.json.gz> --out <private>/jra/<date>/keibabook_bands.json
"""
import argparse
import gzip
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEG = re.compile(r"(\d{1,2}/\d{1,2})[ \u00a0](\S+?)[ \u00a0](?:良|稍|重|不)")
TIMES = re.compile(r"(?:\d{2,3}\.\d)+")
LETTER = {"EXCEPTIONAL": "X", "VERY_STRONG": "V", "STRONG": "S", "POSITIVE": "P", "NEUTRAL": "N", "CAUTION": "C", None: "-"}


def workouts(text: str) -> list:
    out = []
    marks = list(SEG.finditer(text))
    for i, m in enumerate(marks):
        seg = text[m.end(): marks[i + 1].start() if i + 1 < len(marks) else len(text)]
        run = TIMES.search(seg)
        if not run:
            continue
        toks = re.findall(r"\d{2,3}\.\d", run.group(0))
        out.append([f"{m.group(1)} {m.group(2)}", float(toks[-1])])
    return out


def compact(pages: dict) -> dict:
    races = []
    for r in pages["races"]:
        p = r["pages"]
        w, s = [], []
        for t in (p.get("調教") or {}).get("tables") or []:
            rows = t.get("rows") or []
            for i, row in enumerate(rows):
                if len(row) >= 4 and row[1].isdigit():
                    nxt = rows[i + 1][0] if i + 1 < len(rows) and rows[i + 1] and len(rows[i + 1]) == 1 else ""
                    w.append([int(row[1]), row[2], row[3] or None, workouts(nxt)])
        for t in (p.get("厩舎の話") or {}).get("tables") or []:
            rows = t.get("rows") or []
            for i, row in enumerate(rows):
                if len(row) >= 3 and row[1].isdigit() and i + 1 < len(rows) and rows[i + 1] and rows[i + 1][0]:
                    s.append([int(row[1]), rows[i + 1][0]])
        races.append({"id": r["kb_id"], "t": r.get("title"), "s": s, "w": w})
    return {"date8": pages["date"], "races": races}


def bands(c: dict) -> list:
    js = (ROOT / "runtime/capture/keibabook_bands.js").read_text()
    prog = "global.window={};" + js + ";process.stdout.write(JSON.stringify(window.__kmBands(JSON.parse(require('fs').readFileSync(0,'utf8')))))"
    out = subprocess.run(["node", "-e", prog], input=json.dumps(c, ensure_ascii=False), capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pages")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if "keibametrics-private-evidence" not in a.out:
        raise SystemExit("DEST_NOT_PRIVATE")
    pages = json.loads(gzip.decompress(Path(a.pages).read_bytes()))
    c = compact(pages)
    res, n, ws = {}, 0, 0
    for r in bands(c):
        cells = ",".join(f"{h['no']}{LETTER[h['wcap']]}{LETTER[h['wspd']]}{LETTER[h['stab']]}" for h in r["h"])
        res.setdefault(r["id"][6:8], []).append([r["id"], cells])
        n += len(r["h"]); ws += sum(1 for h in r["h"] if h["wspd"])
    d8 = pages["date"]
    doc = {"date": f"{d8[:4]}-{d8[4:6]}-{d8[6:]}", "captured_at": pages.get("collected_at"),
           "captured_via": "BUILT_IN_BROWSER_ASSISTED", "production_authority": False,
           "rules": ["JRA-WORKOUT-CAPABILITY-COMMENT-v1", "JRA-WORKOUT-FINAL1F-BAND-v1", "KM-JRA-STABLE-COMMENT-STATE-v1"],
           "legend": "no+wcap+wspd+stab; X=EXCEPTIONAL V=VERY_STRONG S=STRONG P=POSITIVE N=NEUTRAL C=CAUTION -=none",
           "n": n, "workout_speed_covered": ws, "res": res}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(doc, ensure_ascii=False) + "\n")
    print(json.dumps({"races": sum(len(v) for v in res.values()), "horses": n, "workout_speed_covered": ws,
                      "stable_comment": sum(1 for r in c["races"] for _ in r["s"])}))


if __name__ == "__main__":
    main()
