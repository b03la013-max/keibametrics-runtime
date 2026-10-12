import json
from pathlib import Path
import pytest
from tools.local_aki_matched_comparison import portfolio,compare,ticket_key
ROOT=Path(__file__).resolve().parents[1]


def test_integer_budget_preserves_full_coverage_and_never_mutates_prediction():
    tickets=[{'bet_type':'EXACTA','selection':[1,2],'stake':100},
             {'bet_type':'TRIO','selection':[3,2,1],'stake':100}]
    original=json.dumps(tickets,sort_keys=True)
    full=portfolio(tickets,['OHI','2026-10-07',4],5)
    assert sum(t['stake'] for t in full)==500
    assert {ticket_key(t) for t in full}=={ticket_key(t) for t in tickets}
    assert all(t['stake']>=100 and t['stake']%100==0 for t in full)
    assert json.dumps(tickets,sort_keys=True)==original
    assert full==portfolio(list(reversed(tickets)),['OHI','2026-10-07',4],5)


def test_count_matching_is_research_only_and_rejects_duplicate_unordered_ticket():
    ts=[{'bet_type':'TRIO','selection':[1,2,3]}, {'bet_type':'TRIO','selection':[3,1,2]}]
    with pytest.raises(ValueError,match='DUPLICATE_FROZEN_TICKET'):portfolio(ts,['OHI','2026-10-07',4],2)
    with pytest.raises(ValueError,match='NOT_FEASIBLE'):portfolio(ts[:1],['OHI','2026-10-07',4],0)


def test_real_corpus_has_equal_integer_budget_and_count_without_oos():
    import gzip
    corpus=json.loads(gzip.decompress((ROOT/'research/local_aki_columns_20261012/corpus_audit.json.gz').read_bytes()))
    x=compare(corpus)
    assert x['unknown_future_oos_count']==0
    assert x['prediction_portfolios_modified'] is False
    assert x['automatic_promotion'] is False
    for mode,m in x['modes'].items():
        assert m['races']==39
        for r in m['portfolios']:
            c=r['candidate_tickets'];p=r['production_tickets']
            assert sum(t['stake'] for t in c)==sum(t['stake'] for t in p)==r['budget_yen']
            if mode=='equal_budget_equal_count': assert len(c)==len(p)
