"""Out-of-sample (2026-01..2026-10) readout: market baseline, own BSI, and the v4.0-BAN engine+compiler backtest."""
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, '/home/claude/keibametrics-runtime/runtime/banei_autopilot')
import engine, tickets  # noqa: E402

x = pd.read_pickle('runners.pkl')
p = pd.read_csv('/mnt/user-data/uploads/Downloads/KM_BAN_NAR/ban_payback.csv', dtype=str)
p['key'] = p['競走年月日'] + '-' + p['レース番号'].str.zfill(2)
x = x.drop_duplicates(['key', 'no'])
oos = x[(x['date'] >= '2026-01-01') & x['fin'].notna()].copy()
out = []
P = lambda s: f"{100 * s:.1f}%"

# 1. market baseline
f1 = oos[oos['pop'] == 1]
out.append(f"OOS races={oos['key'].nunique()} runners={len(oos)}")
out.append(f"1番人気: 勝率 {P((f1['fin'] == 1).mean())} / 3着内率 {P((f1['fin'] <= 3).mean())}")
for b in ['DRY', 'MID', 'WET']:
    s = f1[f1['band'] == b]
    out.append(f"  {b}: n={len(s)} 勝率 {P((s['fin'] == 1).mean())} 3着内 {P((s['fin'] <= 3).mean())}")
s = f1[f1['young']]
out.append(f"  2歳戦: n={len(s)} 勝率 {P((s['fin'] == 1).mean())}")

# 2. own BSI ranking (provisional weights)
def bsi(row):
    v = {'recent': row['recent'], 'track': row['track'], 'avg': row['avg5']}
    have = {k: z for k, z in v.items() if z == z}
    if not have:
        return np.nan
    w = sum(engine.BSI_W[k] for k in have)
    return sum(engine.BSI_W[k] * z for k, z in have.items()) / w
oos['bsi'] = oos.apply(bsi, axis=1)
oos['bsi_rank'] = oos.groupby('key')['bsi'].rank(ascending=False, method='first')
b1 = oos[oos['bsi_rank'] == 1]
out.append(f"自前BSI1位: 勝率 {P((b1['fin'] == 1).mean())} / 3着内率 {P((b1['fin'] <= 3).mean())}")
agree = b1[b1['pop'] == 1]
out.append(f"  BSI1位=1番人気: n={len(agree)} 勝率 {P((agree['fin'] == 1).mean())}; 不一致時のBSI1位 勝率 {P((b1[b1['pop'] != 1]['fin'] == 1).mean())}")

# 3. relative load
oos['lr'] = pd.cut(oos['load_rel'], [-999, -30, -20, -10, -1, 0], labels=['≤-30', '-20~-29', '-10~-19', '-1~-9', '0(最重)'])
for k, s in oos.groupby('lr', observed=True):
    out.append(f"相対重量 {k}: n={len(s)} 勝率 {P((s['fin'] == 1).mean())} 3着内 {P((s['fin'] <= 3).mean())}")
# 4. body weight change
oos['bwb'] = pd.cut(oos['bwd'], [-99, -16, -10, -1, 9, 15, 99], labels=['≤-16', '-10~-15', '-1~-9', '0~+9', '+10~+15', '≥+16'])
for k, s in oos.groupby('bwb', observed=True):
    out.append(f"馬体重増減 {k}: n={len(s)} 3着内 {P((s['fin'] <= 3).mean())}")

# 5. engine + compiler backtest (no キンタロー barrier data in NAR files -> BTA UNCONFIRMED for all)
hist = x.sort_values('date')
pay = p.drop_duplicates('key').set_index('key')
inv = ret = hits3 = hits3t = races = 0
by_shape = {}
for key, grp in oos.groupby('key'):
    if key not in pay.index or len(grp) < 5:
        continue
    horses = []
    for _, h in grp.iterrows():
        horses.append({'no': int(h['no']), 'name': h['馬名'], 'age': h['age'], 'load': h['load'],
                       'body_weight': h['bw'], 'body_delta': h['bwd'], 'pop': h['pop'], 'odds': None,
                       'idx_pre': {'recent': h['recent'], 'track': h['track'], 'avg': h['avg5']}})
    race = {'moisture': grp['moist'].iloc[0], 'special': grp['grade'].iloc[0] != '普通',
            'young': bool(grp['young'].iloc[0]), 'horses': horses}
    ev = engine.evaluate(race)
    tk = tickets.compile_race(ev)
    races += 1
    pr = pay.loc[key]
    tri = tuple(sorted(int(pr[c]) for c in ['３連複組番馬番1', '３連複組番馬番2', '３連複組番馬番3']))
    exa = tuple(int(pr[c]) for c in ['３連単組番馬番1', '３連単組番馬番2', '３連単組番馬番3'])
    cost = tk['points'] * 100
    back = (int(pr['３連複払戻金（円）']) if tri in set(tk['trio']) else 0) + \
           (int(pr['３連単払戻金（円）']) if exa in set(tk['exact']) else 0)
    inv += cost; ret += back
    hits3 += tri in set(tk['trio']); hits3t += exa in set(tk['exact'])
    s = by_shape.setdefault(tk['shape'], [0, 0, 0, 0])
    s[0] += 1; s[1] += cost; s[2] += back; s[3] += tri in set(tk['trio'])
out.append(f"エンジン逆算 races={races} 投資 {inv:,} 払戻 {ret:,} 回収率 {P(ret / inv)} 三連複的中 {P(hits3 / races)} 三連単的中 {P(hits3t / races)}")
for k, (n, c, b, hh) in by_shape.items():
    out.append(f"  型 {k}: n={n} 回収率 {P(b / c if c else 0)} 三連複的中 {P(hh / n)}")
open('readout.txt', 'w').write('\n'.join(out))
print('\n'.join(out))
