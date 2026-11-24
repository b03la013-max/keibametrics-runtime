"""亀谷 sire rules v3 (B4, Drive 精読 q423 GAP n63/n64/n66/n67, 2026-11-24).

v3 = v2 (sire_rules_v2.json, left untouched because it feeds the EXT label KAME) with
  * the corrections found by the full read of the dictionary (runtime/local_autopilot/kametani_v2c.PATCHES:
    023 / 034 / 039 / 052 / 058 / 075 / 076 / 109 / 087 / 106 / 094 / 099) applied entry by entry,
  * two further corrections: 022 シスキン dirt buy = short distance (原文「ダート短距離に高い適性の可能性」),
    041 ゴールドドリーム「白い砂の地方中距離は母系欧州型も可」(著者予測, the 白い砂 venues are not named -> x),
  * the empty 「この項目の要点」 items that carry a NAR-readable scene:
      072 母父ディープインパクト (DAMSIRE): caution ダート短距離の古馬混合で人気
      089 米国型 (TYPE, sire country type): buy ダート1400m以下の2・3歳限定 (下級条件 -> x)
      090 日本型 (TYPE): caution ダート (原文「日本型が相対的に不得意な…ダートでは他系統のスペシャリストの価値が上がる」)
    and the ones that do not (listed under 'omitted').
Keys are those of v2 plus kametani_v2c.NEW_KEYS (bornle, gapmax, nar) and ds 'US|MP', last '2-5' / 'top3'.
The rules decide WHICH label a horse carries (EXT label KAME3); how strong it is comes from NAR data, and its weight
starts at 0 and moves only through the weekly hold-out refit (ext_model.fit_weights).
Run: python3 research/kametani/build_rules_v3.py
"""
import copy
import json
import sys
from pathlib import Path

H = Path(__file__).resolve().parent
sys.path.insert(0, str(H.parents[1]))
from runtime.local_autopilot import kametani_v2c as kc  # noqa: E402

B = 9999
EXTRA = [
    ('C11', '022', 'buy', 'merge', 1, {'d': [0, 1400]}, '原文「ダートでは母父が米国型…（ダート短距離に高い適性の可能性）」'),
    ('C12', '041', 'buy', 'append', None, {'S': 'D', 'd': [1600, 2000], 'ds': 'EU', 'nar': 1, 'x': ['白い砂の地方']},
     '原文「白い砂の地方中距離は母系欧州型も可」（著者予測。白い砂の場は特定されないため x）'),
]
DAMSIRE = [{'no': '072', 'name': 'ディープインパクト', 'kind': 'DAMSIRE',
            'buy': [], 'caution': [{'S': 'D', 'd': [0, 1400], 'age': 'old', 'pop': 'fav'}],
            'source_caution': 'ダート短距離の古馬混合戦で人気（短距離 = 1400m以下で代用）'}]
TYPE = [{'no': '089', 'name': '米国型', 'kind': 'TYPE', 'country': '米国型',
         'buy': [{'S': 'D', 'd': [0, 1400], 'age': '2-3', 'x': ['下級条件']}], 'caution': [],
         'source_buy': 'ダート1400m以下の2・3歳限定の下級条件（国別タイプ集計で米国型の好走数・好走率が優秀）'},
        {'no': '090', 'name': '日本型', 'kind': 'TYPE', 'country': '日本型', 'buy': [], 'caution': [{'S': 'D'}],
         'source_caution': '日本型が相対的に不得意な芝短距離・ダートでは他系統のスペシャリストの価値が上がる'}]
OMITTED = {
    '003': '母父マンハッタンカフェ：芝・JRA クラス条件のみ（NOT_LOCAL）',
    '014': '予想手順（父の国タイプ×人気ランクの層別で複勝回収率を見る方法）：ルールではない',
    '015': 'ダート1700m 父米国型/欧州型ミスプロ系：全種牡馬の国別タイプ表（血統ビーム、未入手）が無いと照合できない',
    '016': '父欧州型マル外：NAR の出走表でマル外・ゴドルフィン所有・4ライン系統が読めない',
    '071': '母父シンボリクリスエス：買いは「GⅠなど大舞台・父サンデー系後継」で地方の出走表では条件化できない',
    '088': '欧州型：割引は「JRA下級条件・2・3歳戦」（JRA 限定）、買いは芝長距離（NOT_LOCAL）',
    '091': '大系統/小系統の分類法：ルールではない',
}


def build():
    v2 = json.loads((H / 'sire_rules_v2.json').read_text())
    entries, applied = [], {}
    for e in v2['entries']:
        e2, a = kc.corrected_entry(e)
        for pid, no, side, op, i, pay, _ in EXTRA:
            if e2.get('no') != no:
                continue
            alts = e2.setdefault(side, [])
            if op == 'merge' and i is not None and i < len(alts):
                alts[i] = {**alts[i], **pay}
            elif op == 'append':
                alts.append(copy.deepcopy(pay))
            else:
                continue
            a.append(pid)
        if a:
            e2['v3_patches'] = a
            applied[e2['no']] = a
        entries.append(e2)
    reasons = {p[0]: p[6] for p in kc.PATCHES + EXTRA}
    return {'profile': 'KM-KAMETANI-SIRE-RULES-STRUCTURED-v3.0-20261124', 'source_profile': v2['profile'],
            'sha256_source': v2.get('sha256_source'),
            'source': 'Drive q423 亀谷敬正の競馬血統辞典（同名馬統合版）全文精読 2026-11-21/24（GAP n63 n64 n66 n67, bundle B4）',
            'semantics': v2['semantics'] + '\nv3 adds keys bornle N (born year <= N, from age) · gapmax N (days since the last '
            'start <= N) · nar 1 (NAR card) · ds \'US|MP\' · last \'2-5\'/\'top3\'; kind DAMSIRE entries match the runner\'s '
            'damsire, kind TYPE entries match the sire\'s country type (v1 type text).\n',
            'patches': reasons, 'patched_entries': applied, 'omitted': {**v2.get('omitted', {}), **OMITTED},
            'entries': entries, 'damsire_entries': DAMSIRE, 'type_entries': TYPE}


if __name__ == '__main__':
    out = build()
    (H / 'sire_rules_v3.json').write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n')
    print('v3 entries', len(out['entries']), 'patched', len(out['patched_entries']),
          'damsire', len(out['damsire_entries']), 'type', len(out['type_entries']))
