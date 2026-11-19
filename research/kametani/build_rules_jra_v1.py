"""亀谷 sire rules for JRA (D6 port, 2026-11-20): rebuild sire_rules_v2.json for central courses.

v2 was written for NAR, so its JRA-only scenes (jra=1 → NOT_LOCAL) and its course words (x → UNKNOWN)
never resolved. This build keeps every v2 scene and only re-reads those two kinds into JRA keys:
  venue [...]        JRA venue names (Japanese, as in the official race card)
  straight long/short  home straight from COURSE below (long ≥ 400 m, short ≤ 310 m, else mid)
  slope 1/0          an uphill in the home straight (COURSE); 0 = flat
  flat_or_long 1     「直線が長いか平坦」
  root 1/0           根幹距離 = multiple of 400 m
  cls low/maiden/maiden_1win/2win+   from the official race name
  born_le YYYY       birth year = race year − age (JRA age convention)
  bw 500             「大型馬」 proxy on the previous-run body weight (v2 bw semantics) (research threshold, not policy)
  ds SS              「母父ディープ系かTサンデー系」 proxy
Course words that a card cannot show (軽い馬場, 上がりがかかる, 生産者 …) stay in x → UNKNOWN.
Kyoto / Niigata / Hanshin turf have inner and outer courses that the card does not name → straight UNKNOWN.
Research evidence only (production_effect NONE)."""
import json
from pathlib import Path

H = Path(__file__).resolve().parent
B = 9999

# venue -> surface -> (straight class, uphill in straight). None = not determinable from the card.
COURSE = {
    '東京': {'T': ('long', 1), 'D': ('long', 1)}, '中京': {'T': ('long', 1), 'D': ('long', 1)},
    '中山': {'T': ('short', 1), 'D': ('short', 1)}, '阪神': {'T': (None, 1), 'D': ('mid', 1)},
    '京都': {'T': (None, 0), 'D': ('mid', 0)}, '新潟': {'T': (None, 0), 'D': ('mid', 0)},
    '札幌': {'T': ('short', 0), 'D': ('short', 0)}, '函館': {'T': ('short', 0), 'D': ('short', 0)},
    '小倉': {'T': ('short', 0), 'D': ('short', 0)}, '福島': {'T': ('short', None), 'D': ('short', None)},
}

X_MAP = {
    '直線が長いコース': {'straight': 'long'}, '直線の長いコース': {'straight': 'long'},
    '直線の短いコース': {'straight': 'short'}, '直線が短いコース': {'straight': 'short'},
    '直線の長いダート': {'straight': 'long'}, '直線が長いか平坦': {'flat_or_long': 1},
    '直線が長く坂のあるコース': {'straight': 'long', 'slope': 1}, '直線に坂': {'slope': 1},
    '根幹距離': {'root': 1}, '非根幹距離': {'root': 0}, '非根幹距離（2000m除く）': {'root': 0},
    '直線の長い根幹距離': {'straight': 'long', 'root': 1},
    '未勝利戦': {'cls': 'maiden'}, '未勝利・1勝クラス': {'cls': 'maiden_1win'}, '下級条件': {'cls': 'low'},
    '2勝クラス以上': {'cls': '2win+'}, '2021年以前生まれ': {'born_le': 2021},
    '大型馬': {'bw': 500}, '母父ディープ系かTサンデー系': {'ds': 'SS'},
}

# v2 scenes marked jra=1, re-read from the entry's source text (source_buy).
JRA_SCENES = {
    '008': [dict(S='D', venue=['東京'], d=[1600, B]), dict(S='D', venue=['東京'], wet=1)],
    '029': [dict(S='D', d=[0, 1400], straight='long'), dict(S='D', venue=['東京', '中京'], wet=1)],
    '032': [dict(S='D', venue=['東京'])],
    '037': [dict(S='D', venue=['東京', '中京', '京都', '阪神'], wet=1)],
}


def convert(alt, no):
    if alt.get('jra'):
        return JRA_SCENES[no]
    a = {k: v for k, v in alt.items() if k != 'x'}
    rest = []
    for x in alt.get('x') or []:
        m = X_MAP.get(x)
        if m is None:
            rest.append(x)
            continue
        for k, v in m.items():
            if k in a and a[k] != v:
                rest.append(x)  # conflicts with an explicit condition: keep it unresolved
                break
        else:
            a.update(m)
    if rest:
        a['x'] = rest
    return [a]


if __name__ == '__main__':
    src = json.loads((H / 'sire_rules_v2.json').read_text())
    out, resolved = [], 0
    for e in src['entries']:
        n = dict(e)
        for side in ('buy', 'caution'):
            alts = []
            for a in e.get(side) or []:
                new = convert(a, e['no'])
                resolved += (a.get('jra') or bool(a.get('x'))) and new != [a]
                alts += new
            n[side] = alts
        out.append(n)
    doc = {'profile': 'KM-JRA-KAMETANI-SIRE-RULES-v1.0-20261120', 'source_profile': src['profile'],
           'sha256_source': src.get('sha256_source'), 'course': COURSE, 'scenes_reread': resolved,
           'semantics': __doc__, 'entries': out}
    (H / 'sire_rules_jra_v1.json').write_text(json.dumps(doc, ensure_ascii=False, indent=1) + '\n')
    print(len(out), 'entries,', resolved, 'scenes re-read for JRA')
