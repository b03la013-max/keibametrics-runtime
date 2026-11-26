"""KIEP-BAN P0: Formula Ledger（ばんえい v4.0 の全指数・全成分の算式・係数・閾値・欠損時の扱い・接続先）。

Owner 2026-11-26 21:43「KIEP を永続的に実施」。コードの定数から毎回組み立てるので、手で書いた台帳と実装がずれない。
formula_sha は算式に効く定数すべての SHA256。registry.step が毎晩記録し、変わった日を履歴に残す（本番の値は変えない）。
"""
import hashlib
import inspect
import json

import derive
import engine
import tickets

# 成分の定義（算式の意味・欠損時の扱い・接続先）。係数・閾値は下の constants() がコードから読む。
COMPONENTS = {
    'bsi': {'name': 'BSI 基礎能力', 'source': 'NAR過去成績・楽天・キンタロー（近走・同場・平均）', 'formula': 'BSI_W で近走・同場・平均を加重（SBO_SHARE 分は水分ボンバーの指数）',
            'missing': '過去走なし → None（TPI も None、DCR 低）', 'consumer': ['tpi', 'win_score', 'place_score']},
    'isv': {'name': 'ISV 安定性', 'source': '近走の指数のばらつき', 'formula': '標準偏差（小さいほど安定）→ LIS', 'missing': 'None', 'consumer': ['lis', 'place_score（SCORE.isv）']},
    'lis': {'name': 'LIS 安定加点', 'source': 'isv', 'formula': 'isv≤1:+2、≤3:+1、それ以外0', 'missing': '0', 'consumer': ['place_score', 'hole_score']},
    'bta': {'name': 'BTA-B 第2障害', 'source': 'キンタロー障害区間秒', 'formula': 'BTA_BANDS（秒以下→補正）', 'missing': '0（未確認は SCORE.unconfirmed_pen）', 'consumer': ['tpi', 'win_score']},
    'mpa': {'name': 'MPA-B 位置変化', 'source': 'キンタロー丸数字（暫定の読み方）', 'formula': 'MPA_BANDS（前進頭数→補正）、後退は MPA_BACK', 'missing': 'None→0', 'consumer': ['tpi']},
    'brs': {'name': 'BRS-B 障害後', 'source': 'キンタロー丸数字（障害→ゴール）', 'formula': 'BRS_BANDS（順位上昇→補正）、後退は BRS_BACK', 'missing': 'None→0', 'consumer': ['tpi', 'win_score']},
    'wda': {'name': 'WDA-B 重量', 'source': '出馬表の負担重量・前走比', 'formula': '重い上位3頭の平均との差 ≥30kg:MID(8,12)、≥20:MID(5,8)、≥10:MID(2,4)、規定戦以外は×0.5（weight_terms）', 'missing': '0', 'consumer': ['tpi']},
    'front_bonus': {'name': '先行加点', 'source': 'キンタロー短評・競馬ブック', 'formula': '軽量＋先行（WDA/FLA の大きい方、MID(2,4)）と race_pace（CUTS.pace_H_*）', 'missing': '0', 'consumer': ['tpi']},
    'jbr': {'name': 'JBR-B 騎手', 'source': 'NAR騎手成績・同馬好走・前進', 'formula': '該当1:MID(2,3)、2以上:MID(3,6)（CUTS.jockey_*）', 'missing': '0', 'consumer': ['tpi']},
    'adf': {'name': 'ADF-B 水分', 'source': '馬場水分・過去の水分帯成績', 'formula': 'DRY のときだけ5項目', 'missing': '0', 'consumer': ['tpi']},
    'bwl': {'name': 'BWL-B 馬体重', 'source': '当日馬体重・好走時の体重帯', 'formula': '±0.8% 未満は中立、帯の外で減点', 'missing': '0（NEUTRAL）', 'consumer': ['tpi']},
    'cci': {'name': 'CCI-B コメント', 'source': '競馬ブック・キンタロー短評・公式コメント', 'formula': 'VERY_STRONG +3 / STRONG +1.5 / CAUTION −1.5', 'missing': '0', 'consumer': ['tpi']},
    'cpu': {'name': 'CPU 昇級', 'source': 'クラス（キンタロー→楽天→NAR）', 'formula': '昇級かつ連勝中でない → −1.5', 'missing': '0', 'consumer': ['tpi']},
    'tpi': {'name': 'TPI 総合', 'source': '上の成分', 'formula': 'bsi + Σ COMP_W[c]×成分', 'missing': 'bsi が None なら None', 'consumer': ['tpi_eff（＋PICKS_W・TRACKFIT_W は影のみ）', 'win_score', 'place_score', 'hole_score']},
    'win_score': {'name': '1着の点', 'source': 'tpi_eff・bta・brs', 'formula': 'tpi_eff + SCORE.win_brs×brs + SCORE.win_bta×bta − SCORE.unconfirmed_pen（障害未確認）', 'missing': '—', 'consumer': ['win_rank', 'role_w']},
    'place_score': {'name': '3着内の点', 'source': 'tpi_eff・isv・lis・障害の安定', 'formula': 'tpi_eff + SCORE.isv[isv_label] + lis + SCORE.place_stable（障害 STABLE）', 'missing': '—', 'consumer': ['place_rank', 'role_p2', 'role_p3']},
    'hole_score': {'name': '穴の点', 'source': 'place_score・人気・lis', 'formula': 'place_score + SCORE.hole_longshot（人気 SCORE.longshot_pop 番以下）+ lis', 'missing': '—', 'consumer': ['hole_rank', '▲']},
}


def constants():
    """算式に効く定数をコードから読む（関数・正規表現など JSON にできないものは除く）。"""
    out = {}
    for mod, names in ((engine, ('BSI_W', 'SBO_SHARE', 'PICKS_W', 'TRACKFIT_W', 'BTA_BANDS', 'MPA_BANDS', 'MPA_BACK', 'BRS_BANDS',
                                 'BRS_BACK', 'SCORE', 'COMP_W', 'MARKET_FREE', 'MARKET_W', 'RULESET')),
                       (derive, ('CUTS', 'FRONT_WORDS', 'FADE_WORDS')),
                       (tickets, ('CAP_TOTAL', 'FORCE_TRIO_AXIS', 'EXACT_RULE', 'EXACT_PICK'))):
        for n in names:
            if hasattr(mod, n):
                v = getattr(mod, n)
                try:
                    json.dumps(v)
                    out[f'{mod.__name__}.{n}'] = v
                except TypeError:
                    out[f'{mod.__name__}.{n}'] = repr(v)
    return out


def build():
    c = constants()
    code = {m.__name__: hashlib.sha256(inspect.getsource(m).encode()).hexdigest()[:16] for m in (engine, derive, tickets)}
    body = {'profile': 'KIEP-BAN-FORMULA-LEDGER-v1', 'ruleset': engine.RULESET, 'components': COMPONENTS,
            'constants': c, 'implementation_sha16': code}
    body['formula_sha'] = hashlib.sha256(json.dumps(c, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    return body
