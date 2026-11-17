import json

from runtime.local_autopilot import checkpoint10 as c10


def test_roles_and_ticket_diff():
    r = c10._roles_from_ranking(list(range(1, 12)))
    assert r['W'] == {'1', '2', '3'} and len(r['P3']) == 9
    old = [{'bet_type': 'TRIO', 'selection': [1, 2, 3]}, {'bet_type': 'EXACTA', 'selection': [1, 2]}]
    new = [{'bet_type': 'TRIO', 'selection': [1, 2, 3]}, {'bet_type': 'EXACTA', 'selection': [2, 1]}]
    d = c10.ticket_diff(old, new)
    assert d['added'] == [('EXACTA', '2-1')] and d['removed'] == [('EXACTA', '1-2')]


def test_effective_dir_prefers_signed_rev2(tmp_path):
    f = tmp_path / 'formal'
    (f / 'rev2').mkdir(parents=True)
    (f / 'OHI_01.summary.json').write_text('{"status": "SIGNED_FINAL"}')
    assert c10.effective_dir(tmp_path, 'OHI_01') == f
    (f / 'rev2' / 'OHI_01.summary.json').write_text(json.dumps({'status': 'HOLD'}))
    assert c10.effective_dir(tmp_path, 'OHI_01') == f            # a held Revision 2 never replaces Revision 1
    (f / 'rev2' / 'OHI_01.summary.json').write_text(json.dumps({'status': 'SIGNED_FINAL'}))
    assert c10.effective_dir(tmp_path, 'OHI_01') == f / 'rev2'
