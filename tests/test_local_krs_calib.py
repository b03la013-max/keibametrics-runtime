import json

from runtime.local_autopilot import krs_calib as kc, settle


def _race(root, day, key, order, ssr, odds, corners=None):
    d = root / day
    (d / 'formal').mkdir(parents=True, exist_ok=True)
    (d / f'{key}.result.json').write_text(json.dumps({'order': order, 'corners': corners or []}))
    (d / 'formal' / f'{key}.krs_prediction_utility.json').write_text(json.dumps({'summary': [
        {'horse_no': h, 'SSR-W': ssr[h], 'SSR-T3': min(1, 3 * ssr[h]),
         'positions': {'1角': {'median': i + 1, 'p25': i + 1, 'p75': i + 2}, '4角': {'median': i + 1, 'p25': i, 'p75': i + 2}}}
        for i, h in enumerate(sorted(ssr))]}))
    (d / f'{key}.json').write_text(json.dumps({'prediction': {'ranking': [
        {'no': h, 'p_win': ssr[h], 'win': odds[h]} for h in ssr]}}))
    (d / 'formal' / f'{key}.summary.json').write_text(json.dumps({'ranking': [str(h) for h in sorted(ssr, key=lambda h: -ssr[h])]}))


def test_baseline_metrics_and_weekly(tmp_path):
    for i in range(20):
        ssr = {1: 0.5, 2: 0.2, 3: 0.15, 4: 0.1, 5: 0.05, 6: 0.0}
        order = [1, 2, 3, 4, 5, 6] if i % 2 else [2, 1, 3, 4, 5, 6]
        cor = [['1コーナー', '1,2,3,4,5,6'], ['4コーナー', '2,1,3,4,5,6']] if i < 5 else None
        _race(tmp_path, f'2026-11-{16 + i % 10:02d}', f'OHI_{i:02d}', order, ssr, {h: 2 + h for h in ssr}, cor)
    rep = kc.evaluate(tmp_path)
    assert rep['races'] == 20 and rep['probability']['krs_w']['winner_at_zero'] == 0
    assert rep['stage']['races_with_passing_order'] == 5 and rep['stage']['1角']['mae_positions'] == 0
    assert rep['stage']['predicted_leader_led_1角'] == 1.0
    assert rep['increment']['same'] == 20 and rep['temperature']['krs_w']['T_fitted_on_train'] > 0
    assert kc.weekly(tmp_path, '2026-11-23') and kc.weekly(tmp_path, '2026-11-25') is None
    assert 'KRS の較正測定' in kc.md(rep)


def test_result_page_corners_parsed():
    html = ('<tbody class="record"><tr class="box"><td class="order">1</td><td class="number">3</td></tr>'
            '<tr class="box"><td class="order">2</td><td class="number">1</td></tr>'
            '<tr class="box"><td class="order">3</td><td class="number">2</td></tr></tbody>'
            '<table summary="払戻金"><tr><th scope="row">単勝</th><td class="number">3</td><td class="money">250円</td></tr></table>'
            '<table summary="コーナー通過順位"><tr><th scope="row">1コーナー</th><td class="time">3,1,2</td></tr>'
            '<tr><th scope="row">4コーナー</th><td class="time">3-1,2</td></tr></table>')
    r = settle.parse_result(html)
    assert r['corners'] == [['1コーナー', '3,1,2'], ['4コーナー', '3-1,2']]


def test_research_rerun_variant_and_compare(tmp_path):
    from runtime.local_autopilot import krs_research as kr
    ssr = {1: 0.5, 2: 0.2, 3: 0.15, 4: 0.1, 5: 0.05}
    _race(tmp_path, '2026-11-27', 'OHI_01', [1, 2, 3, 4, 5], ssr, {h: 2 + h for h in ssr},
          [['1コーナー', '1,2,3,4,5'], ['4コーナー', '1,2,3,4,5']])
    kin = {'race': {'race_id': 'R'}, 'simulation': {'master_seed': 7},
           'horses': [{'horse_no': h, 'hsv': {'early_position_hold': 95.0, 'midrace_hold': 40.0, 'front_friction_tolerance': 10.0}} for h in ssr]}
    (tmp_path / '2026-11-27' / 'formal' / 'OHI_01.krs_input.json').write_text(json.dumps(kin))
    v = kr.variant_input(kin, 'HOLD15')['horses'][0]['hsv']
    assert v == {'early_position_hold': 100.0, 'midrace_hold': 55.0, 'front_friction_tolerance': 25.0}
    seen = []

    def fake(inp, rid, n, seed):
        seen.append((rid, n, seed))
        summ = [{'horse_no': h, 'SSR-W': ssr[h], 'SSR-T3': 0.5,
                 'positions': {'1角': {'median': h, 'p25': h, 'p75': h}, '4角': {'median': h, 'p25': h, 'p75': h}}} for h in ssr]
        return {'http_status': 200, 'receipt_status': 'EXECUTED'}, {'artifact': {'raw_output': {'summary': summ}}}
    assert kr.nightly(tmp_path, '2026-11-27', runner=fake) == 1 and seen == [('R-RESEARCH-HOLD15', 5000, 7)]
    assert kr.nightly(tmp_path, '2026-11-27', runner=fake) == 0           # not run twice
    cv = kc.compare_variants(tmp_path)
    assert cv['HOLD15']['HOLD15']['front3_stays_front3']['predicted'] == 1.0 and cv['HOLD15']['formal']['races'] == 1
