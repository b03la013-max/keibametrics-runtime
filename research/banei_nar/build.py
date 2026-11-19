"""Build the BAN runner ledger from NAR official monthly data and an own speed index (no leakage)."""
import re
import numpy as np
import pandas as pd

D = '/mnt/user-data/uploads/Downloads/KM_BAN_NAR/'
r = pd.read_csv(D + 'ban_racelist.csv', dtype=str)
h = pd.read_csv(D + 'ban_horselist.csv', dtype=str)

Z2H = str.maketrans('０１２３４５６７８９ＡＢＣＯＰ', '0123456789ABCOP')


def cls(name):
    s = str(name).translate(Z2H)
    m = re.search(r'(A1|A2|B1|B2|B3|B4|C1|C2|C3|OP|オープン)', s)
    return (m.group(1) if m else 'OTHER').replace('オープン', 'OP')


r['key'] = r['競走年月日'] + '-' + r['レース番号'].str.zfill(2)
r['moist'] = pd.to_numeric(r['馬場'], errors='coerce')
r['cls'] = r['レース名'].map(cls)
r['young'] = r['条件'].str.contains('2歳|２歳')
r['grade'] = r['競走種類名称']
h['key'] = h['競走年月日'] + '-' + h['レース番号'].str.zfill(2)
h['load'] = pd.to_numeric(h['負担重量'].str.replace(r'[^\d]', '', regex=True), errors='coerce')
h['bw'] = pd.to_numeric(h['馬体重'], errors='coerce')
h['bwd'] = pd.to_numeric(h['馬体重増減'].str.replace('+', ''), errors='coerce')
h['fin'] = pd.to_numeric(h['着順'], errors='coerce')
h['pop'] = pd.to_numeric(h['人気'], errors='coerce')
h['age'] = pd.to_numeric(h['齢'], errors='coerce')
h['no'] = pd.to_numeric(h['馬番'], errors='coerce')
t = h['タイム'].str.zfill(4)
h['sec'] = pd.to_numeric(t.str[:-3], errors='coerce') * 60 + pd.to_numeric(t.str[-3:], errors='coerce') / 10
x = h.merge(r[['key', 'moist', 'cls', 'young', 'grade']], on='key', how='left')
x['date'] = pd.to_datetime(x['競走年月日'])
x['load_rel'] = x['load'] - x.groupby('key')['load'].transform('max')
ok = x['sec'].notna() & x['moist'].notna() & x['load'].notna() & (x['sec'] > 40)
# speed model: time ~ load + moisture(+^2) + class + young + month ; fit on data before 2026 only (no leakage)
feat = pd.get_dummies(x[['cls']], dtype=float)
X = pd.concat([x[['load']], x['moist'].rename('m'), (x['moist'] ** 2).rename('m2'),
               x['young'].astype(float).rename('y'),
               pd.get_dummies(x['date'].dt.month, prefix='mon', dtype=float), feat], axis=1)
X['c'] = 1.0
train = ok & (x['date'] < '2026-01-01')
coef, *_ = np.linalg.lstsq(X[train].fillna(0).values, x.loc[train, 'sec'].values, rcond=None)
res = x['sec'] - X.fillna(0).values @ coef
sd = res[train].std()
x['idx'] = np.where(ok, 80 - 10 * res / sd, np.nan)
print('model sd(sec)=', round(sd, 1), 'load coef sec/kg=', round(coef[0], 3), 'moist coef', round(coef[1], 2), round(coef[2], 2))
x['band'] = pd.cut(x['moist'], [-1, 1.5, 2.55, 99], labels=['DRY', 'MID', 'WET'])
x = x.sort_values(['馬名', 'date', 'key'])
g = x.groupby('馬名')
x['recent'] = g['idx'].shift(1)
x['avg5'] = g['idx'].transform(lambda s: s.shift(1).rolling(5, min_periods=1).mean())
x['nprev'] = g.cumcount()
tr = []
for name, grp in g:
    prev = []
    for i, row in grp.iterrows():
        same = [v for b, v in prev if b == row['band'] and v == v]
        tr.append((i, np.mean(same[-5:]) if same else np.nan))
        prev.append((row['band'], row['idx']))
tv = dict(tr)
x['track'] = x.index.map(tv)
win = x[x['fin'] <= 3]
x['prev_good_bw_lo'] = np.nan
x.to_pickle('/home/claude/banei_nar/runners.pkl')
r.to_pickle('/home/claude/banei_nar/races.pkl')
print(x.shape, x['recent'].notna().mean().round(3), x['track'].notna().mean().round(3))
