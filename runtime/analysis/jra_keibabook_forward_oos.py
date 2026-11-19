"""Forward OOS for the Keibabook Production connection (Owner 2026-11-15; NON-PRODUCTION shadow).

freeze <date>: for every FINAL still before post, recompute the Static ZAI-WIN ranking from the
  frozen FORMAL request with the Keibabook features removed (features whose evidence_refs point at
  a SUPP:KEIBABOOK-* source). The Production frozen ranking is the "with Keibabook" arm; recompute
  of the full request must reproduce it (checked and recorded). Immutable once written.
evaluate: after RESULT (freeze strictly before the result capture), compare winner rank and top-3
  capture of the two rankings, with venue x surface strata and the venue rule.
"""
import copy, datetime as dt, glob, hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'runtime'), str(ROOT / 'runtime/jra_source_runtime'), str(ROOT / 'runtime/analysis')]
from jra_evidence_to_base_production import load_mapping, build_production_ledger  # noqa: E402
from jra_index_provenance_builder import zai_formula_version, zai_win_value  # noqa: E402

OUT = 'runtime/jra_keibabook_forward_oos'
MAPPING = 'mapping/jra_base_index_evidence_mapping_v1.0_20260921.json'


def _rank(root, rid, runners):
    led = build_production_ledger(rid, runners, load_mapping(str(root / MAPPING)))
    v = zai_formula_version(rid)
    z = {str(k): zai_win_value({i: x['value'] for i, x in r['base_indices'].items()}, v) for k, r in led['runners'].items()}
    return sorted(z, key=lambda k: -z[k])


def _strip_keibabook(runners):
    out, removed = copy.deepcopy(runners), 0
    for r in out:
        ef = r.get('evidence_features') or {}
        for name in [n for n, f in ef.items()
                     if any(str(x).startswith('SUPP:KEIBABOOK-') for x in (f.get('evidence_refs') or []))]:
            ef.pop(name); removed += 1
    return out, removed


def freeze(date8, root=ROOT, now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    made = []
    for p in sorted(glob.glob(str(root / f'runtime/final_artifacts/KM-JRA-*-{date8}-R*.json'))):
        rid = Path(p).stem
        out = root / OUT / rid / 'pre_result.json'
        if out.exists() or (root / 'runtime/results' / f'{rid}.json').exists():
            continue
        final = json.loads(Path(p).read_text())
        if now >= dt.datetime.fromisoformat(final['scheduled_post_at']):
            continue
        reqs = sorted(glob.glob(str(root / f'runtime/requests/{rid}-LIVE-R*-FORMAL.json')))
        if not reqs:
            continue
        req = json.loads(Path(reqs[-1]).read_text())
        prod = [str(x) for x in final['static_prediction']['ranking']]
        without, removed = _strip_keibabook(req['runners'])
        body = {'profile': 'KM-JRA-KEIBABOOK-FORWARD-OOS-v1', 'race_id': rid, 'frozen_at': now.isoformat(),
                'scheduled_post_at': final['scheduled_post_at'], 'production_effect': 'NONE',
                'keibabook_features_removed': removed, 'with_keibabook_ranking': prod,
                'recompute_reproduces_production': _rank(root, rid, req['runners']) == prod,
                'without_keibabook_ranking': _rank(root, rid, without) if removed else prod}
        body['sha256'] = hashlib.sha256(json.dumps(body, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(body, ensure_ascii=False, indent=1) + '\n')
        made.append(rid)
    return made


def evaluate(root=ROOT):
    from jra_oos_strata import conditions, keys, split, venue_rule
    rows = []
    for p in sorted(glob.glob(str(root / OUT / '*' / 'pre_result.json'))):
        pre = json.loads(Path(p).read_text())
        rp = root / 'runtime/results' / f"{pre['race_id']}.json"
        if not rp.exists() or not pre['keibabook_features_removed'] or not pre['recompute_reproduces_production']:
            continue
        off = json.loads(rp.read_text())['official_result']
        if not off.get('captured_at') or pre['frozen_at'] >= off['captured_at']:
            continue
        top3 = [str(x) for x in off['finish_order'][:3]]
        m = lambda rk: {'winner_rank': rk.index(top3[0]) + 1, 'top3_in_top3': sum(h in rk[:3] for h in top3)}
        rows.append({'race_id': pre['race_id'], 'with': m(pre['with_keibabook_ranking']),
                     'without': m(pre['without_keibabook_ranking']),
                     'strata': keys(pre['race_id'], conditions(root, pre['race_id']))})
    if not rows:
        return {'races': 0}
    mean = lambda arm, k: round(sum(r[arm][k] for r in rows) / len(rows), 3)
    sp = split(rows, lambda r: r['without']['winner_rank'] - r['with']['winner_rank'])  # + = Keibabook better
    return {'classification': 'FORWARD_OOS (frozen before result)', 'races': len(rows),
            'with_keibabook': {k: mean('with', k) for k in ('winner_rank', 'top3_in_top3')},
            'without_keibabook': {k: mean('without', k) for k in ('winner_rank', 'top3_in_top3')},
            'strata': sp, 'venue_rule': venue_rule(sp), 'note': 'no significance claim below 100 races'}


if __name__ == '__main__':
    if sys.argv[1] == 'freeze':
        print(json.dumps({'frozen': freeze(sys.argv[2].replace('-', ''))}))
    else:
        print(json.dumps(evaluate(), ensure_ascii=False, indent=1))
