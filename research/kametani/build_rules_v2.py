"""Hand-structured 亀谷 sire rules v2 (read entry by entry from sire_rules.json, 2026-11-18).

Each entry: buy / caution = list of ALTERNATIVES (OR); each alternative = dict of conditions that must ALL hold.
Keys: S surface D/T · d [min,max] metres · sex M (牡・せん) / F · ds damsire class (US EU JP SS nonUS nonEU
nonJP nonSS SS|KM SS|EU; 原文「母が◯◯」も母父で代用 = proxy) · front 1/0 (近走先行 = last-3 first-corner rank
≤ 1/3 of field; proxy for テンP50以内) · age '2-3' (2・3歳限定戦→馬齢≤3 proxy) / 'old' (古馬混合→馬齢≥4) ·
wet 1/0 · last 'lost' (前走2着以下) / '4+' / 'win' / 'top5' · new 1/0 (新馬戦) · car N (≥N戦) · bw N (前走≥N kg) ·
bwlt N (前走<N kg) · frame [lo,hi] 枠 · chg 'short'/'ext'/'notext' (前走比距離) · lastsurf T/D · pop 'fav' (≤3番人気) /
'long' (≥6) · x [...] conditions that cannot be read on a NAR card (直線・坂・上がり・クラス・生産者 …) → UNKNOWN ·
jra 1 → the alternative names JRA courses only → NOT_LOCAL.
Alternatives judged too vague to test are left out (listed under 'omitted').
"""
import json
from pathlib import Path

H = Path(__file__).resolve().parent
T, D = 'T', 'D'
B = 9999

R = {
 '001': dict(buy=[dict(S=D, d=[0, 1200], ds='US', sex='M')]),
 '002': dict(buy=[dict(S=T, d=[0, 1200], ds='nonSS', front=1)], caution=[dict(ds='SS')]),
 '004': dict(buy=[dict(S=T, d=[2000, B], ds='nonUS', x=['直線が短いコース'])], caution=[dict(S=D), dict(ds='US')]),
 '005': dict(buy=[dict(S=D, d=[0, 1400], ds='nonSS'), dict(S=D, d=[1600, 1700], ds='SS', front=1)],
             caution=[dict(S=D, d=[0, 1400], ds='SS'), dict(S=D, d=[1800, B])]),
 '006': dict(buy=[dict(S=T, d=[0, 1600], front=1)]),
 '007': dict(buy=[dict(S=T, d=[2200, B], sex='M', x=['直線が長いコース']), dict(S=D, d=[1800, B], ds='US', sex='M')],
             caution=[dict(S=T, d=[0, 1600]), dict(sex='F')]),
 '008': dict(buy=[dict(jra=1)], caution=[dict(S=D, d=[0, 1400], wet=0)]),
 '009': dict(buy=[dict(S=T, d=[0, 1400]), dict(S=D, d=[0, 1400], sex='M', ds='US', x=['大型馬'])]),
 '010': dict(buy=[dict(S=T, x=['直線が長いコース', '軽い馬場'])], caution=[dict(S=D)]),
 '011': dict(buy=[dict(S=T, d=[1800, 2400], x=['直線が長いコース'])], caution=[dict(S=D)]),
 '012': dict(buy=[dict(sex='M', ds='nonSS', S=T, d=[0, 1400], age='old'),
                  dict(sex='F', S=T, d=[1600, 1800], x=['母父ディープ系かTサンデー系']),
                  dict(S=T, d=[0, 1600], x=['2勝クラス以上']), dict(sex='M', S=D, d=[0, 1600], age='old')],
             caution=[dict(S=T, d=[1800, 2200], age='2-3')]),
 '013': dict(buy=[dict(sex='M', bw=480, S=D, d=[1600, B]), dict(S=D, ds='US'), dict(S=T, front=1)],
             caution=[dict(S=T, d=[0, 1800], front=0), dict(S=D, d=[0, 1400], sex='F')]),
 '019': dict(buy=[dict(sex='M', ds='SS', S=T, d=[2000, B], age='old', x=['直線が長いコース'])]),
 '020': dict(buy=[dict(ds='EU', S=T, d=[2000, B], x=['直線の短いコース'])], caution=[dict(S=T, d=[0, 1400])]),
 '021': dict(buy=[dict(ds='EU', S=T, d=[0, 1400])]),
 '022': dict(buy=[dict(S=T, ds='SS', x=['軽い馬場の中距離']), dict(S=D, ds='US')]),
 '023': dict(buy=[dict(S=T, d=[0, 1400], front=1), dict(S=D, d=[0, 1400], ds='US', sex='M', age='2-3', x=['大型馬'])],
             caution=[dict(S=T, d=[1600, B]), dict(ds='SS')]),
 '024': dict(buy=[dict(sex='M', S=T, d=[1800, B], x=['直線の長いコース'])], caution=[dict(S=D), dict(S=T, d=[0, 1400])]),
 '025': dict(buy=[dict(S=D, d=[0, 1400])], caution=[dict(S=T, d=[1800, 2400], x=['直線の長いコース'])]),
 '026': dict(buy=[dict(S=T, d=[2400, B])]),
 '027': dict(buy=[dict(sex='M', S=T, d=[2000, B], new=0)], caution=[dict(sex='F'), dict(new=1)]),
 '028': dict(buy=[dict(ds='nonUS', sex='M', S=T, d=[1800, B], x=['直線の短いコース']), dict(ds='nonEU', sex='M', S=D, d=[1800, B]),
                  dict(sex='F', S=T, d=[0, 1400])], caution=[dict(S=D, d=[1600, 2000], ds='EU')]),
 '029': dict(buy=[dict(S=T, d=[0, 1400]), dict(S=D, d=[0, 1400], x=['直線の長いダート']), dict(jra=1)]),
 '030': dict(buy=[dict(ds='SS', sex='M', S=T, d=[2000, B], age='old', x=['直線の短いコース']), dict(S=T, d=[1600, B], x=['ノーザンファーム関連馬'])]),
 '031': dict(buy=[dict(ds='nonUS', S=T, d=[2000, B], x=['直線の短いコース'])], caution=[dict(ds='EU', d=[0, 1200])]),
 '032': dict(buy=[dict(jra=1), dict(S=D, wet=1)]),
 '033': dict(buy=[dict(ds='nonEU', sex='F', S=D), dict(ds='SS', sex='M', S=D, d=[1800, B])], caution=[dict(ds='EU', sex='F', S=D)]),
 '034': dict(buy=[dict(S=T, d=[1800, B], x=['上がりのかかる芝']), dict(S=D, d=[1800, B])], caution=[dict(S=D, d=[0, 1400])]),
 '035': dict(buy=[dict(S=D, d=[0, 1400]), dict(S=D, d=[1800, B], age='2-3')], caution=[dict(S=T, d=[1800, 2400])]),
 '036': dict(buy=[dict(S=T, ds='nonSS', front=1), dict(S=D, d=[1600, 2000], sex='M', front=1)], caution=[dict(ds='SS', sex='F', S=D)]),
 '037': dict(buy=[dict(S=D, ds='nonUS', front=0), dict(jra=1), dict(ds='nonUS', sex='M', S=T, d=[0, 1800], x=['直線が長いか平坦'])],
             caution=[dict(ds='US', sex='F', S=D, d=[0, 1400])]),
 '038': dict(buy=[dict(S=T, d=[1800, B], x=['非根幹距離'])], caution=[dict(d=[0, 1400], sex='F')]),
 '039': dict(buy=[dict(ds='EU', sex='M', S=T, d=[1800, B], x=['直線の長いコース']), dict(S=D, d=[1800, B], ds='US', x=['2021年以前生まれ']),
                  dict(S=D, d=[1800, B], bw=460, x=['2021年以前生まれ'])], caution=[dict(S=D, d=[0, 1400])]),
 '040': dict(buy=[dict(S=T, d=[1800, B])], caution=[dict(S=D)]),
 '041': dict(buy=[dict(S=D, d=[1600, B])], caution=[dict(S=D, d=[0, 1200], ds='nonUS')]),
 '042': dict(buy=[dict(S=T, d=[0, 1400]), dict(S=D, d=[0, 1400], ds='US')]),
 '043': dict(buy=[dict(S=T, d=[1800, B], x=['直線の短いコース'])], caution=[dict(S=D, sex='F'), dict(S=D, d=[0, 1400])]),
 '044': dict(buy=[dict(S=T, d=[0, 1400])], caution=[dict(ds='EU', S=D)]),
 '045': dict(buy=[dict(sex='M', ds='EU', S=T, d=[1600, B]), dict(sex='F', S=T, d=[0, 1400], front=1)], caution=[dict(S=D, bwlt=460)]),
 '046': dict(buy=[dict(S=T, d=[1600, B]), dict(ds='nonUS', S=D, d=[1600, B])], caution=[dict(d=[0, 1400])]),
 '047': dict(buy=[dict(S=T, d=[1600, B])]),
 '048': dict(buy=[dict(sex='M', ds='EU', S=T, d=[1600, B], x=['直線の短いコース']), dict(ds='US', d=[0, 1800])], caution=[dict(ds='EU', S=D)]),
 '049': dict(buy=[dict(sex='M', S=T, d=[1800, B], ds='SS|KM'), dict(sex='F', S=T, d=[1600, 2400], x=['直線の長い根幹距離'])],
             caution=[dict(d=[0, 1200]), dict(S=D, sex='F')]),
 '050': dict(buy=[dict(ds='US', S=D, d=[1700, B])], caution=[dict(S=D, d=[0, 1400], pop='fav')]),
 '051': dict(buy=[dict(ds='nonUS', S=T)], caution=[dict(ds='US', S=T)]),
 '052': dict(buy=[dict(S=T, d=[1800, B], sex='M'), dict(sex='F', S=T, d=[1800, B], x=['母父ディープ系かTサンデー系']),
                  dict(ds='US', S=D, d=[0, 1400], x=['未勝利・1勝クラス'])], caution=[dict(ds='EU', S=D, d=[1600, B], pop='fav')]),
 '053': dict(buy=[dict(S=D, ds='nonUS'), dict(S=T, d=[0, 1200], age='2-3')]),
 '055': dict(caution=[dict(S=T, d=[0, 1200]), dict(S=D)]),
 '056': dict(buy=[dict(S=D, d=[0, 1400], ds='SS|KM'), dict(S=T, d=[0, 1200], ds='SS|KM')]),
 '057': dict(buy=[dict(S=D, d=[1600, B], frame=[5, 8], ds='nonEU'), dict(S=T, front=1, ds='SS|EU')],
             caution=[dict(S=D, d=[0, 1200], frame=[1, 4], pop='fav'), dict(S=D, ds='EU')]),
 '058': dict(buy=[dict(S=T, front=1, x=['上がりがかかる条件']), dict(S=D, new=0, ds='nonSS')], caution=[dict(front=0), dict(new=1)]),
 '059': dict(buy=[dict(S=T, d=[1600, B], x=['直線が長いコース']), dict(S=D, d=[0, 1400], bw=460)]),
 '060': dict(buy=[dict(S=T, d=[1600, B], last='win')], caution=[dict(S=D, d=[0, 1400])]),
 '061': dict(buy=[dict(S=T, d=[0, 1200])], caution=[dict(S=D)]),
 '062': dict(buy=[dict(S=T, d=[1800, 2200], x=['直線の短いコース'])], caution=[dict(S=D)]),
 '063': dict(buy=[dict(S=D, d=[1600, B], frame=[5, 8]), dict(S=D, wet=1)], caution=[dict(S=D, frame=[1, 3])]),
 '064': dict(buy=[dict(S=T, d=[0, 1200], age='old', front=1, car=4)], caution=[dict(S=T, d=[1400, B])]),
 '065': dict(buy=[dict(sex='M', S=D, d=[1700, B]), dict(sex='M', S=T, d=[1800, 2400], front=1)], caution=[dict(sex='F', S=D)]),
 '066': dict(buy=[dict(S=T, d=[1800, 2400], x=['直線の長いコース'])], caution=[dict(S=D, sex='F')]),
 '067': dict(buy=[dict(ds='EU', sex='M', S=T, d=[1800, B]), dict(S=T, d=[1200, 1200], sex='F', front=1)],
             caution=[dict(ds='EU', sex='F', S=D, pop='fav')]),
 '068': dict(buy=[dict(S=T, d=[2000, B], front=1)], caution=[dict(sex='M', S=T, d=[0, 1200], pop='fav'), dict(ds='nonUS', sex='F', S=D, pop='fav')]),
 '070': dict(buy=[dict(S=D, d=[1700, B]), dict(S=T, d=[1600, B], wet=1)], caution=[dict(S=T, d=[0, 1400], pop='fav')]),
 '073': dict(buy=[dict(sex='F', S=D, d=[1600, B])], caution=[dict(ds='EU', sex='M', pop='fav')]),
 '074': dict(buy=[dict(sex='F', S=T, d=[0, 1400]), dict(sex='M', S=T, d=[2200, B]), dict(sex='M', S=D, d=[1800, B], bw=480),
                  dict(sex='M', S=D, d=[1800, B], ds='US')], caution=[dict(S=T, d=[1600, 2000], pop='fav', x=['直線が長いコース'])]),
 '075': dict(buy=[dict(S=D, d=[1600, B], ds='US'), dict(S=T, d=[1600, B], x=['母父ディープ系かTサンデー系']), dict(S=D, chg='short')],
             caution=[dict(S=T, d=[0, 1200], pop='fav')]),
 '076': dict(buy=[dict(S=D, d=[1600, 1800], ds='US')], caution=[dict(S=D, d=[0, 1200], age='old', ds='nonUS', pop='fav'), dict(d=[1900, B])]),
 '077': dict(buy=[dict(S=T, d=[0, 1800], age='old', ds='US')], caution=[dict(S=D, ds='nonUS', pop='fav')]),
 '078': dict(buy=[dict(S=D, d=[0, 1200], ds='SS')],
             caution=[dict(S=T, ds='nonSS', pop='fav'), dict(S=D, d=[1600, B], ds='nonJP', pop='fav'), dict(S=D, d=[0, 1200], ds='nonSS')]),
 '079': dict(buy=[dict(S=T, d=[1800, B], frame=[6, 8], x=['直線が長く坂のあるコース']), dict(S=T, d=[1600, B], ds='SS'),
                  dict(S=T, d=[0, 1500], age='2-3', ds='nonJP')], caution=[dict(S=D, d=[0, 1400], ds='EU', pop='fav')]),
 '080': dict(buy=[dict(S=T, d=[2000, 2400], last='top5'), dict(S=T, d=[1800, B], new=1), dict(ds='US', sex='M', S=D, d=[1600, B])],
             caution=[dict(sex='F', S=T, d=[0, 1400], chg='short', pop='fav'), dict(ds='EU', S=D, pop='fav')]),
 '081': dict(buy=[dict(S=D, d=[1700, B], ds='US'), dict(ds='nonSS', sex='F', S=T, d=[0, 1400], pop='long')],
             caution=[dict(S=D, d=[0, 1400], ds='nonUS', pop='fav')]),
 '082': dict(buy=[dict(S=T, d=[0, 1400], ds='nonSS'), dict(S=T, d=[1500, B], age='2-3', ds='SS|KM')],
             caution=[dict(S=D, d=[0, 1400], ds='nonUS', pop='fav')]),
 '083': dict(buy=[dict(ds='nonSS', sex='M', age='old', S=D, d=[1400, B], x=['直線に坂']), dict(ds='SS|EU', sex='M', age='old', S=T, x=['下級条件'])],
             caution=[dict(sex='F', S=D, pop='fav')]),
 '084': dict(buy=[dict(S=D, d=[1800, B]), dict(sex='F', S=T, d=[0, 1400], age='2-3')], caution=[dict(sex='M', S=T, pop='fav'), dict(age='old', chg='short')]),
 '085': dict(buy=[dict(ds='US', sex='F', S=T), dict(S=D, d=[0, 1400], age='2-3', sex='F')], caution=[dict(sex='M', S=T, d=[0, 1400], pop='fav')]),
 '086': dict(buy=[dict(sex='F', S=T, d=[0, 1600]), dict(sex='M', ds='US', age='2-3', S=D, d=[0, 1400])],
             caution=[dict(sex='M', S=T), dict(sex='M', S=D, d=[0, 1400], age='old')]),
 '087': dict(buy=[dict(S=D, d=[0, 1300], new=0, ds='nonSS'), dict(S=T, d=[1600, B], new=0, ds='SS|EU', x=['直線が長いコース'])],
             caution=[dict(new=1), dict(S=D, d=[0, 1400], ds='SS')]),
 '092': dict(buy=[dict(S=D, d=[1600, B], sex='M', front=1), dict(sex='F', S=T, d=[0, 1400], pop='long')], caution=[dict(S=D, d=[1700, B], sex='F')]),
 '093': dict(buy=[dict(S=D, d=[1700, B], age='old', ds='nonEU')], caution=[dict(S=D, d=[0, 1200], age='2-3', ds='nonUS', pop='fav')]),
 '094': dict(buy=[dict(S=D, d=[1600, B], age='2-3'), dict(S=D, age='2-3', ds='US')], caution=[dict(S=D, d=[0, 1400], age='old', pop='fav')]),
 '095': dict(buy=[dict(S=D, d=[1700, B], ds='nonSS'), dict(S=D, d=[1400, 1400], front=1)], caution=[dict(S=D, d=[0, 1300], ds='SS', pop='fav')]),
 '096': dict(buy=[dict(S=D, d=[1700, B], ds='nonEU')], caution=[dict(S=D, d=[0, 1200], ds='nonUS', pop='fav'), dict(S=D, d=[1400, 1400], pop='fav')]),
 '097': dict(buy=[dict(S=D, d=[0, 1400], age='2-3', ds='nonSS'), dict(S=T, age='2-3', d=[0, 1400])], caution=[dict(d=[1600, B]), dict(age='old')]),
 '098': dict(buy=[dict(S=D, age='2-3', ds='US', last='lost'), dict(S=D, age='2-3', ds='US', new=1)],
             caution=[dict(S=D, d=[1400, B], age='old', ds='SS', pop='fav'), dict(car=15), dict(age='old', d=[1600, B])]),
 '099': dict(buy=[dict(S=D, d=[1600, B], ds='US')], caution=[dict(S=D, d=[0, 1400], ds='nonUS', sex='F')]),
 '100': dict(caution=[dict(S=D, d=[1600, B], sex='F'), dict(S=T, d=[1600, B])]),
 '101': dict(buy=[dict(S=D, d=[1800, B], front=1), dict(S=D, d=[1800, B], chg='ext')], caution=[dict(S=T, pop='fav')]),
 '102': dict(buy=[dict(S=T, d=[2200, B], front=1), dict(S=T, wet=1)], caution=[dict(S=D, d=[0, 1400], ds='nonUS', pop='fav')]),
 '103': dict(buy=[dict(sex='M', S=T, d=[1600, 2400], x=['根幹距離'])], caution=[dict(sex='F')]),
 '104': dict(buy=[dict(sex='M', S=D, lastsurf=T), dict(S=D, ds='US', front=1)], caution=[dict(S=T, d=[0, 1200], pop='fav')]),
 '105': dict(buy=[dict(S=D, d=[1600, B], sex='M', ds='nonEU', chg='notext')], caution=[dict(S=T, d=[0, 1200], ds='nonUS', pop='fav'), dict(chg='ext')]),
 '106': dict(buy=[dict(S=D, d=[1600, B], last='4+')], caution=[dict(S=D, d=[1200, 1200], chg='short', pop='fav')]),
 '107': dict(buy=[dict(S=D, d=[1600, 1800], ds='US')], caution=[dict(S=D, d=[0, 1400], ds='EU', sex='F', pop='fav')]),
 '108': dict(buy=[dict(S=T, d=[1800, 2200], x=['非根幹距離（2000m除く）'])], caution=[dict(S=D, pop='fav')]),
 '109': dict(buy=[dict(S=T, d=[1600, B], sex='M'), dict(S=D, d=[1900, B], ds='US')], caution=[dict(S=T, d=[0, 1200], front=1, pop='fav')]),
 '110': dict(buy=[dict(S=D, d=[0, 1200], frame=[7, 8], last='4+', x=['前走内枠']), dict(S=D, d=[0, 1400], ds='US', x=['未勝利戦'])],
             caution=[dict(ds='EU', x=['未勝利戦'])]),
}
OMITTED = {
 '054': 'スワーヴリチャード：買い・消しとも抽象的（「短距離・ダート（母系の米国要素）」等）で条件化しない',
 '055': 'シュヴァルグラン：買いは「主流の芝条件」で条件化しない（消しのみ構造化）',
 '069': 'ハービンジャー：買い・消しとも東京芝・世代など地方出走表で読めない',
 '100': 'スウェプトオーヴァーボード：買いは「本文は消し中心」（消しのみ構造化）',
 '017/018': '特別企画（種牡馬名が見出しにない）はGENERAL扱いで照合対象外',
}

if __name__ == '__main__':
    src = json.loads((H / 'sire_rules.json').read_text())
    by_no = {e['no']: e for e in src['entries']}
    out = []
    for no, r in sorted(R.items()):
        e = by_no[no]
        out.append({'no': no, 'name': e['name'], 'kind': e['kind'], 'type': e.get('type'),
                    'buy': r.get('buy', []), 'caution': r.get('caution', []),
                    'source_buy': e.get('buy'), 'source_caution': e.get('caution'), 'source': e.get('source')})
    doc = {'profile': 'KM-KAMETANI-SIRE-RULES-STRUCTURED-v2.0-20261118', 'source_profile': src.get('profile'),
           'sha256_source': src.get('sha256_source'), 'entries_structured': len(out), 'omitted': OMITTED,
           'semantics': __doc__, 'entries': out}
    (H / 'sire_rules_v2.json').write_text(json.dumps(doc, ensure_ascii=False, indent=1) + '\n')
    print(len(out), 'entries')
