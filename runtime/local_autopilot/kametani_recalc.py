"""Recompute C7 kametani v2 evidence from FROZEN pre-race inputs (Owner 2026-11-19 18:54「計算し直して含めて」;
prereg amendment R3-A2). Evidence only; signed revision files are never modified.

Why: from 2026-11-19 morning every revision's prediction.kametani was {'status': 'ERROR', KeyError 'rules'}
(cache collision with nankan(), fixed in 68728e33). The matcher reads only pre-race facts, so it can be rerun:
  race      prediction.race_cond (distance / going / surface of THAT revision)
  sire/dam  formal full29 bloodline_bvi_research (sire, damsire; built pre-race by the formal runner)
  starts    prediction.prior_runs (the horse's past starts as parsed pre-race)
  frame     prediction.ranking[].frame          popularity  rank of prediction.ranking[].win (that revision's odds)
  sex/age   a pre-race card capture (Keibabook 出馬表 性齢, captured before the first post), else UNKNOWN
The output carries every input's sha256, the rules sha, the code version and recomputed_at, and is marked
RECOMPUTED_FROM_FROZEN_PRE_RACE_INPUTS. Results are not consulted: the matcher has no outcome input.
"""
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from runtime.local_autopilot import bloodline_kametani as bk

CLASS = 'RECOMPUTED_FROM_FROZEN_PRE_RACE_INPUTS (prereg R3-A2)'
JST = timezone(timedelta(hours=9))


def _sha(b):
    return hashlib.sha256(b if isinstance(b, bytes) else json.dumps(b, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def _sire_map(day_dir, key):
    for p in (day_dir / 'formal' / f'{key}.full29.json', day_dir / 'formal' / 'rev2' / f'{key}.full29.json'):  # original first
        try:
            d = json.loads(p.read_text())
        except (OSError, ValueError):
            continue
        rows = (d.get('production_numerical_summary') or {}).get('bloodline_bvi_research') or []
        return {int(x['runner_id']): (x.get('sire'), x.get('damsire')) for x in rows}, p
    return {}, None


def sexage_from_keibabook(pages_json):
    """{(venue_name, race_no): {horse_no: '牝3'}} from a keibabook_local_collect capture (出馬表 table)."""
    out = {}
    for r in pages_json.get('races') or []:
        m = {}
        for t in (r.get('pages', {}).get('出馬表') or {}).get('tables') or []:
            for row in t.get('rows') or []:
                if len(row) > 2 and row[0].strip().isdigit():
                    s = re.search(r'(牡|牝|セン|騸|せん)\s*(\d+)', row[2])
                    if s:
                        m[int(row[0])] = ('セ' if s[1] in ('セン', '騸', 'せん') else s[1]) + s[2]
        if m:
            out[(r['venue'], int(r['race_no']))] = m
    return out


def recompute(day_dir, rev_path, sexage=None, sexage_source=None):
    day_dir, rev_path = Path(day_dir), Path(rev_path)
    raw = rev_path.read_bytes()
    rev = json.loads(raw)
    pred = rev.get('prediction') or {}
    key = rev_path.name.split('.')[0]
    sires, sire_src = _sire_map(day_dir, key)
    rc = pred.get('race_cond') or {}
    ranking = pred.get('ranking') or []
    odds = sorted((x['win'], x['no']) for x in ranking if x.get('win'))
    pop = {no: i + 1 for i, (_, no) in enumerate(odds)}
    race = {'distance': rc.get('distance'), 'going': rc.get('going'), 'surface': rc.get('surface'),
            'venue_id': key.split('_')[0]}
    runners = []
    for x in ranking:
        no = x['no']
        sa = (sexage or {}).get(no)
        sire, dam = sires.get(no, (None, None))
        runners.append({'horse_no': no, 'sire': sire, 'damsire': dam, 'frame_no': x.get('frame'),
                        'sex_age': sa, 'age': int(re.sub(r'\D', '', sa)) if sa and re.search(r'\d', sa) else None,
                        'popularity': pop.get(no), 'starts': (pred.get('prior_runs') or {}).get(str(no)) or []})
    bk._CACHE.clear()
    ev = bk.race_evidence(race, runners)
    try:
        code = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=Path(__file__).resolve().parents[2],
                              capture_output=True, text=True).stdout.strip() or None
    except OSError:
        code = None
    ev.update({'class': CLASS, 'revision': rev_path.stem, 'recomputed_at': datetime.now(JST).isoformat(),
               'code_version': code, 'original_status': (pred.get('kametani') or {}).get('status'),
               'original_error': (pred.get('kametani') or {}).get('error'),
               'inputs': {'revision_sha256': _sha(raw), 'revision_frozen_at': rev.get('frozen_at'),
                          'full29': str(sire_src.relative_to(day_dir)) if sire_src else None,
                          'full29_sha256': _sha(sire_src.read_bytes()) if sire_src else None,
                          'sex_age_source': sexage_source if sexage else 'UNAVAILABLE (sex/age conditions -> UNKNOWN)'},
               'sire_coverage': sum(1 for r in runners if r['sire']), 'runners_total': len(runners)})
    return ev


def run_day(day_dir, sexage_by_race=None, sexage_source=None, venue_names=None):
    day_dir = Path(day_dir)
    out_dir = day_dir / 'kametani_recalc'
    done = []
    for rp in sorted((day_dir / 'rev').glob('*.json')):
        try:
            rev = json.loads(rp.read_text())
        except ValueError:
            continue
        kg = (rev.get('prediction') or {}).get('kametani') or {}
        if kg.get('status') != 'ERROR':
            continue
        key = rp.name.split('.')[0]
        v, rno = key.split('_')
        sa = (sexage_by_race or {}).get(((venue_names or {}).get(v, v), int(rno)))
        ev = recompute(day_dir, rp, sa, sexage_source)
        out_dir.mkdir(exist_ok=True)
        (out_dir / f'{rp.stem}.json').write_text(json.dumps(ev, ensure_ascii=False) + '\n')
        done.append(rp.stem)
    return done


def load(day_dir, revision):
    try:
        return json.loads((Path(day_dir) / 'kametani_recalc' / f'{revision}.json').read_text())
    except (OSError, ValueError):
        return None


if __name__ == '__main__':
    # python -m runtime.local_autopilot.kametani_recalc <day_dir> [<keibabook_pages.json.gz>]
    import gzip
    sa, src = None, None
    if len(sys.argv) > 2:
        raw = Path(sys.argv[2]).read_bytes()
        sa = sexage_from_keibabook(json.loads(gzip.decompress(raw)))
        src = f'keibabook 出馬表 capture {Path(sys.argv[2]).name} sha256={hashlib.sha256(raw).hexdigest()}'
    names = {'OHI': '大井', 'KAW': '川崎', 'FNB': '船橋', 'URW': '浦和', 'MIZ': '水沢', 'MOR': '盛岡', 'KNZ': '金沢',
             'KSM': '笠松', 'NGY': '名古屋', 'SON': '園田', 'HMJ': '姫路', 'KOC': '高知', 'SAG': '佐賀', 'MON': '門別'}
    print('KAMETANI_RECALC', run_day(sys.argv[1], sa, src, names))
