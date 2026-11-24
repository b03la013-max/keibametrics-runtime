import json
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'runtime', 'banei_autopilot'))
import source  # noqa: E402
import run  # noqa: E402


def _row(no, name, load, bw, chg, pop, odds):
    start = ('<td class="race1"><div><span class="place">3</span></div>'
             '<span>帯広 26.10.26</span><br><span>Ｂ１－２</span><br><span>特別</span><br>'
             f'<span>200ダ {pop}人</span><br><span>西謙一 {load - 10}</span><br>'
             '<span>2:03.5 (10.2)</span><br><span>1048k 3番</span></td>')
    return (f'<tr class="box{no} odd"><td class="number">{no}</td>'
            f'<td class="name"><span class="mainHorse"><a href="#">{name}</a></span><div class="append">'
            f'<span class="rate">{odds}（{pop}人気）</span></div></td>'
            f'<td class="profile">牡5<br><a href="/jockey/detail/JOCKEYID/1">鈴木恵</a><br>{load}<br>西弘美</td>'
            f'<td class="weight">1030 | 1060</td><td class="weightDistance">{bw}<br>{chg:+d}</td>{start}</tr>')


def _card(n=8):
    rows = ''.join(_row(i, f'ウマ{i}', 700 - (20 if i == 5 else 0), 1050 + i, 4 - i, i, f'{1.5 + i:.1f}') for i in range(1, n + 1))
    return f'<html>馬場水分 1.4%<tbody class="raceCard">{rows}</tbody></html>'


def test_parse_card_ban():
    card = source.parse_card_ban(_card())
    assert len(card) == 8 and card[0]['load'] == 700 and card[4]['load'] == 680
    assert card[0]['body_weight'] == 1051 and card[0]['body_delta'] == 3 and card[0]['pop'] == 1
    s = card[0]['starts'][0]
    assert s['load'] == 690 and s['sec'] == 123.5 and s['body_weight'] == 1048 and s['finish'] == 3
    assert source.moisture_from_header(_card()) == 1.4


def test_speed_index_monotone_in_time():
    a = source.speed_index(120.0, 700, 1.5, 11, 'B1', False)
    b = source.speed_index(130.0, 700, 1.5, 11, 'B1', False)
    assert a > b


class FakeClient:
    def __init__(self, top):
        self.top = top

    def get(self, path):
        return self.top


class FakeReader:
    def __init__(self, day):
        d = day.replace('-', '')
        self.client = FakeClient(f'race_card/list/RACEID/{d}0303000001')
        self.d = d

    def card_page(self, rid):
        menu = ''.join(f'<a href="/RACEID/{self.d}03030000{i:02d}"><span class="num">{i}R</span>'
                       f'<span class="time">{9 + i}:00</span></a>' for i in range(1, 3))
        return '<ul class="raceNumber">' + menu.replace('<a href="/', '<a href="/race_card/list/') + '</ul>' + _card()

    def result_page(self, rid):
        return ''


def test_tick_predicts_inside_window(tmp_path, monkeypatch):
    day = '2026-11-21'
    out = tmp_path / day
    out.mkdir()
    rd = FakeReader(day)
    q = run.discover(rd, day, out)
    assert len(q['races']) == 2
    key = '01'
    post = datetime.fromisoformat(q['races'][key]['post'])
    monkeypatch.setattr(run, 'now_jst', lambda: post - timedelta(minutes=20))
    q = run.tick(day, out, rd, {})
    r = q['races'][key]
    assert r['state'] == 'PREDICTION_COMPLETE' and r['points'] <= 30
    assert r['formality'] == 'REFERENCE-RENDERED'           # no キンタロー feed -> not FORMAL
    assert (out / 'R01.md').read_text().count('三連複') >= 1


def test_kintaro_sample_if_present():
    import pytest
    p = os.environ.get('KM_BAN_KINTARO_SAMPLE')
    if not p or not os.path.exists(p):
        pytest.skip('no local キンタロー sample (PDFs are not committed)')
    import kintaro
    d = kintaro.parse(p)
    assert d and all('grades' in v for v in d.values())
    assert any(x['barrier_sec'] for v in d.values() for x in v['past'])


def test_sbo_ban_table_and_blend():
    import engine
    html = ('<p>馬場: 2.7%</p><table id="table"><tr><th>馬番</th></tr>'
            '<tr><td>1</td><td>A</td><td>t</td><td>715</td><td>j</td><td></td><td>92(5)</td><td>62(4)</td><td>81</td></tr>'
            '<tr><td>2</td><td>B</td><td>t</td><td>705</td><td>j</td><td></td><td>-(0)</td><td>70(1)</td><td>75</td></tr></table>')
    t, m = source.parse_sbo_ban(html)
    assert m == 2.7 and t[1] == {'recent': 92.0, 'track': 62.0, 'avg': 81.0, 'n_recent': 5, 'n_track': 4}
    assert t[2]['recent'] is None
    idx, src = engine.base_indices({'idx_sbo': t[1], 'own_past': [{'idx': 80, 'moisture': 2.7}]}, 2.7)
    assert src['recent'] == 'SBO+OWN' and idx['recent'] == round(0.3 * 92 + 0.7 * 80, 2)
    idx, src = engine.base_indices({'idx_sbo': t[1]}, 2.7)
    assert idx == {'recent': 92.0, 'track': 62.0, 'avg': 81.0} and set(src.values()) == {'SBO'}


def test_cci_band():
    assert source.cci_band('上位争い', '本来の姿に戻って') == 'VERY_STRONG'
    assert source.cci_band('ここも様子見', '追走いっぱい') == 'CAUTION'
    assert source.cci_band('障害次第') == 'NEUTRAL'          # conditional is not weak (v2.3 第63条)
    assert source.cci_band(None) is None


def test_nar_good_bw_range_fallback_and_pct(tmp_path):
    import sys
    sys.path.insert(0, 'runtime/banei_autopilot')
    import source
    (tmp_path / 'ban_racelist.csv').write_text(
        '﻿競馬場,競走年月日,レース番号,レース名,条件,馬場\n帯広ば,20261001,1,C1-1,一般,1.5\n帯広ば,20261008,1,C1-1,一般,2.0\n', encoding='utf-8')
    (tmp_path / 'ban_horselist.csv').write_text(
        '﻿競馬場,競走年月日,レース番号,馬名,負担重量,馬体重,着順,タイム\n'
        '帯広ば,20261001,1,テスト,700,1000,2,2000\n帯広ば,20261008,1,テスト,700,1030,1,2100\n', encoding='utf-8')
    hist = source.nar_history(tmp_path)
    assert hist['テスト'][0]['finish'] == 1 and hist['テスト'][0]['body_weight'] == 1030
    card = [{'no': 1, 'name': 'テスト', 'starts': [], 'good_bw_range': None, 'body_weight': 1040, 'body_delta': 10}]
    h = source.build_horses(card, 2.0, '2026-11-21', hist, {}, 1)[0]
    assert h['good_bw_range'] == (1000, 1030) and h['good_bw_src'] == 'NAR'
    assert h['body_delta_pct'] == round(100 * 10 / 1030, 2) and h['nar_starts'] == 2


def test_check10_keeps_rev1_when_nothing_changes_and_revises_on_change(tmp_path, monkeypatch):
    day = '2026-11-21'
    out = tmp_path / day
    out.mkdir()
    rd = FakeReader(day)
    q = run.discover(rd, day, out)
    post = datetime.fromisoformat(q['races']['01']['post'])
    monkeypatch.setattr(run, 'now_jst', lambda: post - timedelta(minutes=20))
    q = run.tick(day, out, rd, {})
    q['races']['01']['delivered'] = 'x'                       # no issue env in tests
    run.dump(out / 'queue.json', q)
    monkeypatch.setattr(run, 'now_jst', lambda: post - timedelta(minutes=9))
    q = run.tick(day, out, rd, {})
    c = q['races']['01']['check10']
    assert c['decision'].startswith('KEEP_REVISION_1') and q['races']['01'].get('effective') is None
    # a scratch before post -> Revision 2 (Rev1 file kept)
    q['races']['01'].pop('check10')
    run.dump(out / 'queue.json', q)
    orig = rd.card_page
    rd.card_page = lambda rid: orig(rid).replace('<td class="number">3</td>', '<td class="number">取消</td>')
    q = run.tick(day, out, rd, {})
    r = q['races']['01']
    assert r['check10']['decision'].startswith('REVISION_2') and r['effective'] == 'rev2'
    assert '出走馬の変更（取消・除外）' in r['check10']['reasons']
    assert (out / 'R01.json').exists() and (out / 'R01.rev2.json').exists()


def test_first_failure_with_json_string_keys():
    tk = {'terminal': {'5': 'HEAD-PURCHASED'}, 'trio': [[5, 7, 9]], 'exact': [[5, 7, 9]]}
    assert run.first_failure(tk, [5, 7, 3]) == 'PAIR-P3-TERMINAL'
    assert run.first_failure(tk, [5, 7, 9]) == 'NONE'
    assert run.first_failure(tk, [8, 7, 9]) == 'ROLE'


def test_review_writes_race_and_daily_summary(tmp_path, monkeypatch):
    import review
    day = '2026-11-21'
    out = tmp_path / day
    out.mkdir()
    rd = FakeReader(day)
    q = run.discover(rd, day, out)
    for key in ('01', '02'):
        post = datetime.fromisoformat(q['races'][key]['post'])
        monkeypatch.setattr(run, 'now_jst', lambda post=post: post - timedelta(minutes=20))
        q = run.tick(day, out, rd, {})
    rec = json.loads((out / 'R01.json').read_text())
    trio = rec['tickets']['trio'][0]
    order = list(trio)
    for key in ('01', '02'):
        run.dump(out / f'R{key}.result.json', {'order': order, 'payouts': {'TRIO': {'-'.join(map(str, sorted(order))): 1500}},
                                              'stake': 2800, 'return': 1500, 'pfs': 53.6, 'first_failure_layer': 'EXACT',
                                              'effective_revision': 1})
        q['races'][key]['state'] = 'SETTLED'
    assert review.daily(out, q)
    s = json.loads((out / 'review' / 'daily_summary.json').read_text())
    assert s['races'] == 2 and s['trio_hit'] >= 1 and (out / 'review' / 'daily_summary.md').exists()
    rv = json.loads((out / 'review' / 'R01.review.json').read_text())
    assert any(p['id'] == 'P2:COMPONENT_PFS' for p in rv['proposals'])
    assert (tmp_path / 'review_period_summary.md').exists()


def test_shadow_challengers_saved_and_base_matches_production(tmp_path, monkeypatch):
    import challengers
    import engine
    day = '2026-11-21'
    out = tmp_path / day
    out.mkdir()
    rd = FakeReader(day)
    q = run.discover(rd, day, out)
    post = datetime.fromisoformat(q['races']['01']['post'])
    monkeypatch.setattr(run, 'now_jst', lambda: post - timedelta(minutes=20))
    run.tick(day, out, rd, {})
    sh = json.loads((out / 'R01.shadow.json').read_text())['candidates']
    prod = json.loads((out / 'R01.json').read_text())['tickets']
    assert set(challengers.PREREG['candidates']) <= set(sh)            # + candidates_queue.json entries
    assert sh['BASE']['trio'] == prod['trio'] and sh['BASE']['exact'] == prod['exact']
    assert all('error' not in v for v in sh.values())
    assert engine.MARKET_W == 0.0 and engine.SBO_SHARE == 0.30      # patches restored after the shadow run


def test_shadow_metrics_table():
    import review
    revs = [{'shadow': {'BASE': {'winner_win_rank': 1, 'top3_in_place5': 3, 'honmei_top3': True, 'trio_hit': True,
                                  'exact_hit': False, 'stake': 2800, 'return': 1500},
                         'MKT50': {'winner_win_rank': 3, 'top3_in_place5': 2, 'honmei_top3': False, 'trio_hit': False,
                                   'exact_hit': False, 'stake': 2800, 'return': 0}}, 'moisture_band': 'WET'}]
    t = {r['id']: r for r in review.shadow_table(revs)}
    assert t['BASE']['winner_top1'] == 1 and t['MKT50']['winner_top3'] == 1 and t['BASE']['pfs'] == 53.6
    assert review._shadow_md(review.shadow_table(revs)).count('|') > 20


def test_settle_refund_reduces_effective_stake(tmp_path, monkeypatch):
    day = '2026-11-21'
    out = tmp_path / day
    out.mkdir()
    rd = FakeReader(day)
    q = run.discover(rd, day, out)
    post = datetime.fromisoformat(q['races']['01']['post'])
    monkeypatch.setattr(run, 'now_jst', lambda: post - timedelta(minutes=20))
    q = run.tick(day, out, rd, {})
    tk = json.loads((out / 'R01.json').read_text())['tickets']
    gone = tk['trio'][0][0]
    n_gone = sum(1 for c in tk['trio'] + tk['exact'] if gone in c)
    monkeypatch.setattr(run.ST, 'parse_result', lambda html: {'order': [9, 8, 7], 'payouts': {'TRIO': {}}, 'non_starters': [gone]})
    run.settle_race(rd, q, '01', out)
    res = json.loads((out / 'R01.result.json').read_text())
    assert res['refund'] == 100 * n_gone and res['stake'] == tk['points'] * 100 - 100 * n_gone


def test_nar_history_skips_nonfinishers(tmp_path):
    (tmp_path / 'ban_racelist.csv').write_text(
        '﻿競馬場,競走年月日,レース番号,レース名,条件,馬場\n帯広ば,20261001,1,C1-1,一般,1.5\n', encoding='utf-8')
    (tmp_path / 'ban_horselist.csv').write_text(
        '﻿競馬場,競走年月日,レース番号,馬名,負担重量,馬体重,着順,タイム,着差\n'
        '帯広ば,20261001,1,カンソウ,700,1000,2,2000,\n帯広ば,20261001,1,トリケシ,☆620,－,,,出走取消\n'
        '帯広ば,20261001,1,チュウシ,700,1000,,,競走中止\n', encoding='utf-8')
    h = source.nar_history(tmp_path)
    assert 'カンソウ' in h and 'トリケシ' not in h and 'チュウシ' not in h


def test_urgent_soon_defers_settlement():
    now = datetime.fromisoformat('2026-11-21T18:00:00+09:00')
    q = {'races': {'01': {'state': 'PREDICTION_COMPLETE', 'post': '2026-11-21T17:30:00+09:00', 'delivered': 'x'},
                   '02': {'state': 'DISCOVERED', 'post': '2026-11-21T18:36:00+09:00'}}}
    assert run._urgent_soon(q, now)                       # 02 opens its prediction window at 18:01
    q['races']['02']['post'] = '2026-11-21T19:30:00+09:00'
    assert not run._urgent_soon(q, now)


def test_axis2_challenger_keeps_lines_without_honmei(tmp_path, monkeypatch):
    day = '2026-11-21'
    out = tmp_path / day
    out.mkdir()
    rd = FakeReader(day)
    q = run.discover(rd, day, out)
    post = datetime.fromisoformat(q['races']['01']['post'])
    monkeypatch.setattr(run, 'now_jst', lambda: post - timedelta(minutes=20))
    run.tick(day, out, rd, {})
    sh = json.loads((out / 'R01.shadow.json').read_text())['candidates']
    hm = sh['AXIS2']['honmei']
    assert sh['AXIS2']['points'] <= 30 and any(hm not in t for t in sh['AXIS2']['trio'])


def test_kintaro_comment_picks_class_if_sample():
    p = os.environ.get('KM_BAN_KINTARO_SAMPLE')
    if not p or not os.path.exists(p):
        return
    import kintaro
    d = kintaro.parse(p)
    horses = d
    assert len({b for v in horses.values() for b in v['pick_boxes']}) >= 2 and all(isinstance(v['picks'], int) for v in horses.values())
    assert sum(1 for v in horses.values() if v.get('comment')) >= len(horses) - 1
    assert sum(1 for v in horses.values() for q in v['past'] if q.get('race_class')) >= len(horses) * 3


def test_parse_odds_rank_trio_and_trifecta():
    trio = ('<tbody class="rank"><tr class=""> <td>1</td> <td>8-9-10</td> <td class=""><span class="hot">9.0</span></td> </tr>'
            '<tr class="even"> <td>2</td> <td>4-9-10</td> <td class=""><span class="">1,211.2</span></td> </tr></tbody>')
    ex = '<tbody class="rank"><tr> <td>1</td> <td>9→10→8</td> <td class=""><span class="">31.7</span></td> </tr></tbody>'
    assert source.parse_odds_rank(trio, False) == {(8, 9, 10): 9.0, (4, 9, 10): 1211.2}
    assert source.parse_odds_rank(ex, True) == {(9, 10, 8): 31.7}


def test_official_comment_feeds_cci():
    feed = {'11': {'3': {'trainer': '好調をキープ、チャンスはある', 'jockey': '上位争いしたい'}}}
    assert source.official_comment_band(feed, 11, 3).startswith('好調')
    assert source.cci_band(None, None, None, None, source.official_comment_band(feed, 11, 3)) in ('STRONG', 'VERY_STRONG')


def test_production_config_from_registry_is_applied(tmp_path, monkeypatch):
    import registry
    day = '2026-11-21'
    out = tmp_path / day
    out.mkdir()
    reg = registry.load(tmp_path)
    reg['production'] = {'id': 'AXIS2', 'version': 'KM-BAN-v4.0-static-r1+AXIS2@20261201',
                         'config': {'tpatch': {'FORCE_TRIO_AXIS': 2}}, 'since': '2026-12-01'}
    registry.save(tmp_path, reg)
    rd = FakeReader(day)
    q = run.discover(rd, day, out)
    post = datetime.fromisoformat(q['races']['01']['post'])
    monkeypatch.setattr(run, 'now_jst', lambda: post - timedelta(minutes=20))
    run.tick(day, out, rd, {})
    rec = json.loads((out / 'R01.json').read_text())
    sh = json.loads((out / 'R01.shadow.json').read_text())['candidates']
    assert rec['evaluation']['ruleset_version'].endswith('AXIS2@20261201')
    assert rec['tickets']['trio'] == sh['BASE']['trio'] == sh['AXIS2']['trio']
    import tickets
    assert tickets.FORCE_TRIO_AXIS is None                      # restored after the production block


def test_candidates_queue_configs_name_existing_knobs():
    """candidates_queue.json の候補は既存の名前付き定数だけを動かす（本番の値は変えない）。"""
    import json
    from pathlib import Path
    import engine, tickets, derive
    q = json.loads((Path(engine.__file__).with_name('candidates_queue.json')).read_text())
    for cid, c in q['candidates'].items():
        cfg = c['config']
        assert set(cfg) <= {'patch', 'tpatch', 'cuts', 'nopos'}, cid
        assert all(hasattr(engine, k) for k in cfg.get('patch', {})), cid
        assert all(hasattr(tickets, k) for k in cfg.get('tpatch', {})), cid
        assert all(k in derive.CUTS for k in cfg.get('cuts', {})), cid
    assert q['candidates']['MKT30_PICKS']['config'] == {'patch': {'MARKET_W': 0.3, 'PICKS_W': 1.5}}
    assert engine.MARKET_W == 0.0 and engine.PICKS_W == 0.0          # 本番の値は不変


def test_special_notes_jockey_change_and_result_scratch():
    card = ("<ul class='specialNote'> <li>10番&nbsp;騎手変更&nbsp;鈴木恵介→阿部武臣</li> <li>4番&nbsp;出走取消</li> </ul>")
    assert source.special_notes(card) == [(10, '騎手変更 鈴木恵介→阿部武臣'), (4, '出走取消')]
    res = ('<tr> <td class="order">-</td> <th class="position" scope="row">4</th> <td class="number">4</td> '
           '<td class="time">-</td> <td class="lead"> <span style="color: #ff0000; ">取消</span> </td> </tr>'
           '<tr> <td class="order">9</td> <td class="number">3</td> <td class="lead"> </td> </tr>')
    assert source.result_non_starters(res) == [4]


def test_watch_alerts_once_per_race(tmp_path, monkeypatch):
    posts = []
    monkeypatch.setenv('KM_BAN_DELIVERY_ISSUE', '429')
    monkeypatch.setattr(run, '_gh', lambda m, p, b=None: posts.append(b['body']) or {})
    now = run.now_jst()
    q = {'races': {
        '01': {'no': 1, 'post': (now - timedelta(minutes=90)).isoformat(), 'state': 'PREDICTION_COMPLETE', 'delivered': 'x'},
        '02': {'no': 2, 'post': (now - timedelta(minutes=5)).isoformat(), 'state': 'MISSED_DEADLINE', 'last_error': 'E'},
        '03': {'no': 3, 'post': (now + timedelta(minutes=60)).isoformat(), 'state': 'DISCOVERED', 'err_n': 3, 'last_error': 'X'},
    }, 'review_fail': 'boom'}
    run.watch(q, tmp_path, now)
    run.watch(q, tmp_path, now)
    assert set(q['alerts']) == {'SETTLE_LATE:01', 'MISSED_DEADLINE:02', 'REPEATED_ERROR:03', 'REVIEW_FAIL:day'}
    assert len(posts) == 4


def test_compression_loss_only_when_in_universe():
    import review
    fin = {k: {'in_role': True} for k in ('1', '2', '3')}
    tk = {'trio': [[2, 5, 8]], 'exact': [[8, 5, 2]]}
    assert review.compression_loss(fin, (5, 8, 2), tk) == {'in_universe': True, 'compressed_out_trio': False, 'compressed_out_exact': True}
    fin['2']['in_role'] = False                                  # 役割の段階で外れたなら圧縮の責任ではない
    assert review.compression_loss(fin, (5, 8, 2), {'trio': [], 'exact': []}) == {
        'in_universe': False, 'compressed_out_trio': False, 'compressed_out_exact': False}
