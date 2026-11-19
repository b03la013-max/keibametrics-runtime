"""Research only (not adopted): blend market rank (人気) into the v4.0 engine and compare OOS ROI."""
import sys, pandas as pd
sys.path.insert(0, '/home/claude/keibametrics-runtime/runtime/banei_autopilot')
import engine, tickets
x = pd.read_pickle('runners.pkl').drop_duplicates(['key', 'no'])
p = pd.read_csv('/mnt/user-data/uploads/Downloads/KM_BAN_NAR/ban_payback.csv', dtype=str)
p['key'] = p['競走年月日'] + '-' + p['レース番号'].str.zfill(2); pay = p.drop_duplicates('key').set_index('key')
oos = x[(x['date'] >= '2026-01-01') & x['fin'].notna()]
def run(k):
    inv = ret = h3 = ht = n = 0
    for key, g in oos.groupby('key'):
        if key not in pay.index or len(g) < 5: continue
        hs = [{'no': int(h['no']), 'age': h['age'], 'load': h['load'], 'body_weight': h['bw'], 'body_delta': h['bwd'],
               'pop': h['pop'], 'idx_pre': {'recent': h['recent'], 'track': h['track'], 'avg': h['avg5']}} for _, h in g.iterrows()]
        ev = engine.evaluate({'moisture': g['moist'].iloc[0], 'special': g['grade'].iloc[0] != '普通', 'young': bool(g['young'].iloc[0]), 'horses': hs})
        if k:
            N = len(ev['rows'])
            for r in ev['rows']:
                r['tpi'] = None if r['tpi'] is None else r['tpi']
                bonus = k * (N + 1 - 2 * (r['pop'] or N)) / N * 10      # +k*10 for 1番人気 ... -k*10 for 最低人気
                r['bsi'] = r['bsi']
                r['tpi'] = (r['tpi'] if r['tpi'] is not None else None)
                r['_mk'] = bonus
            nt = engine._neutral(ev['rows'], 'tpi')
            for r in ev['rows']:
                r['tpi'] = (r['tpi'] if r['tpi'] is not None else nt) + r['_mk']
            engine._rank(ev['rows'], {'young': False})
            ev.update(engine._race_level(ev['rows'], {'young': False}))
        tk = tickets.compile_race(ev); n += 1
        pr = pay.loc[key]
        tri = tuple(sorted(int(pr[c]) for c in ['３連複組番馬番1', '３連複組番馬番2', '３連複組番馬番3']))
        exa = tuple(int(pr[c]) for c in ['３連単組番馬番1', '３連単組番馬番2', '３連単組番馬番3'])
        inv += tk['points'] * 100
        ret += (int(pr['３連複払戻金（円）']) if tri in set(tk['trio']) else 0) + (int(pr['３連単払戻金（円）']) if exa in set(tk['exact']) else 0)
        h3 += tri in set(tk['trio']); ht += exa in set(tk['exact'])
    print(f"market k={k}: races={n} 回収率 {100*ret/inv:.1f}% 三連複的中 {100*h3/n:.1f}% 三連単的中 {100*ht/n:.1f}% 平均点数 {inv/n/100:.1f}")
for k in (0, 0.5, 1.0, 2.0):
    run(k)
