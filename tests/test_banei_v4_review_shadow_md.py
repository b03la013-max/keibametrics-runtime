import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'runtime', 'banei_autopilot'))
import challengers  # noqa: E402
import engine  # noqa: E402
import review  # noqa: E402

ROW = {'id': 'NEWC', 'n': 3, 'winner_rank_mean': 2.0, 'winner_top1': 1, 'winner_top3': 3, 'top3_in_place5_mean': 2.0,
       'honmei_top3': 1, 'trio_hit': 1, 'exact_hit': 0, 'pfs': 50.0, 'pfs_ex_top1': 20.0}


def test_shadow_md_shows_registry_candidates_what_and_status():
    md = review._shadow_md([ROW], {'NEWC': {'what': '新しい候補の内容', 'status': 'SHADOW'}})
    assert '| NEWC | 新しい候補の内容 | SHADOW | 3 |' in md
    # without the registry the row still renders (blank description), as before
    assert '| NEWC |  |  | 3 |' in review._shadow_md([ROW])


def test_shadow_md_registry_status_overrides_prereg():
    md = review._shadow_md([dict(ROW, id='MKT30')], {'MKT30': {'what': 'x', 'status': 'PRODUCTION'}})
    assert '| MKT30 | x | PRODUCTION |' in md


def test_queue_candidates_apply_to_mpa_brs():
    q = json.load(open(os.path.join(os.path.dirname(review.__file__), 'candidates_queue.json')))
    past_back = [{'pos_first': 2, 'pos_barrier': 5, 'pos_finish': 8}]
    past_fwd = [{'pos_first': 8, 'pos_barrier': 3, 'pos_finish': 1}]
    assert engine.mpa(past_back) == -2.0 and engine.brs(past_back) == -2.0
    with challengers.applied(q['candidates']['POS_NOBACK']['config']):
        assert engine.mpa(past_back) == 0.0 and engine.brs(past_back) == 0.0
        assert engine.mpa(past_fwd) == 5.0 and engine.brs(past_fwd) == 4.0
    assert engine.mpa(past_back) == -2.0 and engine.brs(past_fwd) == 4.0   # production restored
