"""Historical OHI cohort integrity; no new Live/OOS credit."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/"runtime")]

def test_readonly_cohort_metrics_preserve_missing_and_real_stake_sets():
    from scripts.ohi_frozen_acceptance import aggregate, ticket_difference
    partial=aggregate([{'investment':100,'return':None}, {'investment':100,'return':500}])
    assert partial['fixed_denominator']==2 and partial['unsettled']==1
    assert partial['return'] is None and partial['pfs'] is None
    assert partial['investment']==200 and partial['settled_investment']==100
    assert partial['max_drawdown'] is None and partial['drawdown_scope']=='INCOMPLETE_FULL_COHORT_UNKNOWN'
    unknown=aggregate([{'investment':None,'return':None},{'investment':100,'return':500}])
    assert unknown['investment'] is None and unknown['unknown_investment_races']==1
    a=[{'bet_type':'EXACTA','selection':[1,2],'stake':200}]
    b=[{'bet_type':'EXACTA','selection':[1,2],'stake':100},
       {'bet_type':'EXACTA','selection':[2,1],'stake':100}]
    diff=ticket_difference(a,b,{'finish_order':[1,2,3],'payouts':{'EXACTA':500}})
    assert diff['candidate_only_selection_count']==diff['baseline_only_selection_count']+1==1
    assert diff['shared']['investment']==100
    assert diff['baseline_displaced_stake']['return']==500
    assert diff['candidate_extra_stake']['return']==0


def test_frozen_cohort_keeps_bad_signature_race_and_serializes_failure(tmp_path,monkeypatch):
    from scripts import ohi_frozen_acceptance as audit
    from cryptography.exceptions import InvalidSignature
    actual=audit.verify
    monkeypatch.setattr(audit,'assess_runtime_health',lambda *a,**k:{'status':'PASS'})
    monkeypatch.setattr(audit,'materialize_production',lambda *a,**k:(_ for _ in ()).throw(ValueError('TEST_SKIP_RECOMPUTATION')))
    def broken(path,eid,phase,key):
        if eid=='KM-LOCAL-OHI-20261007-R01-LIVE-R1':raise InvalidSignature()
        return actual(path,eid,phase,key)
    monkeypatch.setattr(audit,'verify',broken)
    result=audit.audit(tmp_path,health={'receipt_public_key_b64':'jqWqOYlmhXXmpv/nR7lx3c2n/S5shDYava/WJVxn4kE='},retrain=False)
    cohort=result['cohorts']['20261007']
    assert cohort['production']['fixed_denominator']==12
    assert cohort['production']['unsettled']==1
    assert cohort['production']['return'] is None and cohort['production']['pfs'] is None
    assert cohort['races'][0]['first_failure'].startswith('InvalidSignature:')
    assert (tmp_path/'acceptance.json').is_file()
