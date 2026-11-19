import json

from runtime.local_autopilot import kametani_recalc as kr


def test_recompute_from_frozen_inputs(tmp_path):
    day = tmp_path / '2026-11-19'
    (day / 'rev').mkdir(parents=True)
    (day / 'formal').mkdir()
    rev = {'frozen_at': '2026-11-19T09:00:00+09:00', 'prediction': {
        'kametani': {'status': 'ERROR', 'error': "KeyError:'rules'"},
        'race_cond': {'distance': 1200, 'going': '良', 'surface': 'DIRT'},
        'ranking': [{'no': 1, 'win': 2.0, 'frame': 1}, {'no': 2, 'win': 5.0, 'frame': 2}],
        'prior_runs': {'1': [{'distance': 1400, 'surface': 'DIRT', 'finish': 2, 'field_size': 10, 'content_positions': [1]}]}}}
    (day / 'rev' / 'OHI_01.r1.json').write_text(json.dumps(rev, ensure_ascii=False))
    (day / 'formal' / 'OHI_01.full29.json').write_text(json.dumps({'production_numerical_summary': {'bloodline_bvi_research': [
        {'runner_id': '1', 'sire': 'ヘニーヒューズ', 'damsire': 'サンデーサイレンス'}, {'runner_id': '2', 'sire': 'X', 'damsire': None}]}}, ensure_ascii=False))
    done = kr.run_day(day, {('大井', 1): {1: '牡3'}}, 'test capture', {'OHI': '大井'})
    assert done == ['OHI_01.r1']
    ev = kr.load(day, 'OHI_01.r1')
    assert ev['profile'].startswith('KM-LOCAL-KAMETANI-PEDIGREE-EVIDENCE-v2') and ev['class'].startswith('RECOMPUTED')
    assert ev['original_status'] == 'ERROR' and ev['inputs']['full29_sha256'] and ev['sire_coverage'] == 2
    assert json.loads((day / 'rev' / 'OHI_01.r1.json').read_text()) == rev        # signed file untouched


def test_sexage_parser():
    pages = {'races': [{'venue': '笠松', 'race_no': 1, 'pages': {'出馬表': {'tables': [{'rows': [
        ['馬番', 'x', '馬名'], ['1', '★', 'マウンテンドーター\n 牝3\xa0\n 望月洵'], ['2', '★', 'アドバンス\n セン3\xa0']]}]}}}]}
    assert kr.sexage_from_keibabook(pages) == {('笠松', 1): {1: '牝3', 2: 'セ3'}}
