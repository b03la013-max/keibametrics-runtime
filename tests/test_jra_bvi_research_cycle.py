from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import sys

import pytest

SPEC = importlib.util.spec_from_file_location("bvi_cycle", Path(__file__).resolve().parents[1] / "runtime/jra_bvi_research_cycle.py")
cycle = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cycle)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


@pytest.fixture
def root(tmp_path, monkeypatch):
    code = {}
    for name in cycle.BOUND_FILES:
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# synthetic fixed code " + name)
        code[name] = cycle.file_sha(target)
    model = {"model_sha256": cycle.FIXED_MODEL_SHA, "parent_distributions": {
        "sire": [{"parent": "UNIT SIRE", "runs": 500, "composite_offspring": 2}],
        "damsire": [{"parent": "UNIT DAMSIRE", "runs": 900, "composite_offspring": 3}]}}
    write(tmp_path / cycle.FIXED_MODEL, {"model": model, "code_file_sha256": code})
    monkeypatch.setattr(cycle, "FIXED_FILE_SHA", cycle.file_sha(tmp_path / cycle.FIXED_MODEL))
    for series, path in cycle.LEDGERS.items():
        write(tmp_path / path, {"eligible_settled_races": 61 if series == "SOURCE_DERIVED" else 0,
            "required_forward_races": 30, "automatic_promotion": False, "cohorts": {}})
    return tmp_path


def execute(root, **kwargs):
    return cycle.run(root, observed_at="2026-11-01T09:00:00+00:00", **kwargs)


def group(ids, *, model=None):
    return {"model_sha256": model or cycle.FIXED_MODEL_SHA, "current_base_policy": True,
            "eligible_settled_races": len(ids), "race_ids": ids, "automatic_promotion": False}


def install_groups(root, groups):
    write(root / cycle.LEDGERS["BVI_ENV_FIXED_D"], {"required_forward_races": 30,
        "eligible_settled_races": max((g['eligible_settled_races'] for g in groups.values()), default=0),
        "automatic_promotion": False, "cohorts": groups})


def race_ids(n, venue="TKY"):
    return [f"KM-JRA-{venue}-202611{1+i//12:02d}-R{1+i%12:02d}" for i in range(n)]


def test_series_are_never_pooled_and_seven_hypotheses_are_not_success(root):
    d = execute(root)
    assert d['ledgers']['SOURCE_DERIVED']['eligible_settled_races'] == 61
    assert d['ledgers']['STATIC_OWNER']['eligible_settled_races'] == 0
    assert d['ledgers']['BVI_ENV_FIXED_D']['eligible_settled_races'] == 0
    assert d['counts']['registered_hypotheses'] == 7
    assert d['counts']['tested_new_hypotheses'] == 0
    assert d['counts']['held_for_quality'] == 7
    assert d['status'] == 'PARTIAL' and d['audit_execution_status'] == 'VERIFIED_COMPLETE'
    assert d['stop_at_30'] is False and d['persistent_research_enabled'] is True
    assert d['forward_oos_increment'] == 0 and d['prediction_utility_success'] is False
    hypotheses = list((root/'research/bvi_research_cycle/hypotheses').glob('*.json'))
    assert all(cycle.load(p)['effect_estimate'] is None for p in hypotheses)
    assert all(cycle.load(p)['generated_at']=='2026-11-01T09:00:00+00:00' for p in hypotheses)


def test_same_evidence_is_idempotent_and_keeps_original_registration(root):
    a = execute(root)
    b = cycle.run(root, observed_at='2026-11-08T09:00:00+00:00')
    assert a['evidence_sha256'] == b['evidence_sha256']
    assert a['audit_record_sha256'] == b['audit_record_sha256']
    assert a['last_checked_at'] != b['last_checked_at']
    assert len(list((root/'research/bvi_research_cycle/audits').glob('*.json'))) == 1
    assert len(list((root/'research/bvi_research_cycle/hypotheses').glob('*.json'))) == 7


def test_quality_counter_totals_do_not_establish_training_and_keep_scopes(root):
    s = cycle.sealed({'actual_reader_corpus': {'horse_count':4524,'run_count':45327,'manifest_sha256':'a'*64},
        'created_at':'2026-11-01T00:36:24+00:00',
        'unique_composite_horses':3919,'unique_dedicated_prior_runs':39895,
        'raw_horse_observations':5805,'verified_window_count':139,'permanent_registry_horse_ids':0})
    p = root/'summary.json';write(p,s)
    d = execute(root, corpus_summary=p)
    q = d['quality']
    assert q['composite_horses'] == 4524 and q['history_rows'] == 45327
    assert q['dedicated_harvest_scope']['composite_horses'] == 3919
    assert q['scientific_training_qualified'] is False and q['qualified_independent_labels'] is None
    assert q['permanent_official_horse_ids'] == 0
    assert 'NO_FRESH_OIDC' in q['status']
    assert d['counts']['held_for_quality'] == 7


def test_unverified_summary_is_rejected(root):
    p=root/'summary.json';write(p,{'actual_reader_corpus':{'horse_count':50000}})
    with pytest.raises(ValueError, match='SUMMARY_HASH_INVALID'):
        execute(root,corpus_summary=p)


def test_missing_ledger_remains_unknown_not_zero(root):
    (root/cycle.LEDGERS['SOURCE_DERIVED']).unlink()
    d=execute(root)
    assert d['ledgers']['SOURCE_DERIVED']['eligible_settled_races'] is None
    assert d['ledgers']['SOURCE_DERIVED']['status']=='NOT_OBSERVED'


def test_two_twenty_race_cohorts_do_not_reach_thirty(root):
    install_groups(root,{'c1':group(race_ids(20)), 'c2':group(race_ids(20,'KYO'))})
    d=execute(root)
    assert d['counts']['milestone_review_events']==0 and d['forward_oos_increment']==0


def test_other_model_sixty_one_does_not_complete_fixed_d(root):
    install_groups(root,{'other':group(race_ids(61),model='b'*64)})
    d=execute(root)
    assert d['counts']['milestone_review_events']==0


@pytest.mark.parametrize('mutation',['duplicate','count','non_jra','wrong_venue','boolean'])
def test_corrupt_cohort_membership_is_rejected(root,mutation):
    ids=race_ids(2);g=group(ids)
    if mutation=='duplicate':g['race_ids']=[ids[0],ids[0]]
    if mutation=='count':g['eligible_settled_races']=30
    if mutation=='non_jra':g['race_ids'][0]='KM-LOCAL-OHI-20261101-R01'
    if mutation=='wrong_venue':g['race_ids'][0]='KM-JRA-OHI-20261101-R01'
    if mutation=='boolean':g['eligible_settled_races']=True
    install_groups(root,{'c1':g})
    with pytest.raises(ValueError):execute(root)


def test_aggregate_thirty_without_canonical_records_cannot_advance(root):
    install_groups(root,{'c1':group(race_ids(30))})
    d=execute(root)
    assert d['status']=='BLOCKED' and d['counts']['milestone_review_events']==0
    assert d['counts']['failures']==1


def test_thirty_creates_one_review_packet_not_next_candidate_or_stop(root):
    ids=race_ids(30);install_groups(root,{'c1':group(ids)})
    for rid in ids:
        record=cycle.sealed({'race_id':rid,'oos_eligible':True,'signed_result_verified':True,
            'policy_fingerprint':'c1','environment_candidate':{'model_sha256':cycle.FIXED_MODEL_SHA}})
        write(root/'runtime/jra_static_owner_forward_oos'/rid/'pedigree_env_result.json',record)
    a=execute(root);b=cycle.run(root,observed_at='2026-11-08T09:00:00+00:00')
    assert a['evidence_sha256']==b['evidence_sha256'] and a['stop_at_30'] is False
    assert a['audit_record_sha256']==b['audit_record_sha256']
    assert a['counts']['milestone_review_events']==1 and a['forward_oos_increment']==0
    event=cycle.load(next((root/'research/bvi_research_cycle/milestones').glob('*.json')))
    assert event['next_cohort']['state']=='WAITING_ELIGIBLE_CANDIDATE'
    assert event['next_cohort']['candidate_id'] is None
    assert event['independent_review']=='REQUIRED_NOT_AUTOMATICALLY_PERFORMED'
    assert event['automatic_promotion'] is False and event['quality_audit_continues'] is True
    assert event['signature_verification_repeated_here'] is False


@pytest.mark.parametrize('mutation',['model','code'])
def test_fixed_d_raw_and_code_cannot_change(root,mutation):
    target=root/(cycle.FIXED_MODEL if mutation=='model' else sorted(cycle.BOUND_FILES)[0])
    target.write_text(target.read_text()+' ')
    with pytest.raises(ValueError,match='FIXED_D_'):execute(root)


def test_settlement_failures_do_not_prevent_independent_quality_audit(root):
    p=root/'settlement.json';write(p,{'status':'PARTIAL','counts':{'success_count':1,'failure_count':1,'retry_count':1},
        'required_stages':{'static_owner':{'status':'PARTIAL'}}})
    d=execute(root,settlement_manifest=p)
    assert d['status']=='PARTIAL' and d['counts']['registered_hypotheses']==7
    assert d['settlement']['counts']['failure_count']==1 and d['settlement']['research_audit_still_runs']


def test_historical_mse_worsening_is_retained_and_no_refit(root):
    p=root/'basis.json';write(p,{'classification':'HISTORICAL_PROXY_DIAGNOSTIC_NOT_FIXED_D_FORWARD_OOS',
        'source':{'commit':'unit'},'test':{'GENERAL_ONLY':{'n':10,'mse':.09},'HIERARCHICAL_ENV':{'n':10,'mse':.091}}})
    d=execute(root,basis=p)
    assert d['historical_basis']['decision']=='REJECT_HISTORICAL_INCREMENT'
    assert d['counts']['rejected_historical_candidates']==1 and d['new_candidate_fit']=='NOT_EXECUTED'
    assert d['forward_oos_increment']==0


@pytest.mark.parametrize('n',[0,9])
def test_different_or_empty_historical_populations_do_not_improve(root,n):
    p=root/'basis.json';write(p,{'classification':'HISTORICAL_PROXY_DIAGNOSTIC_NOT_FIXED_D_FORWARD_OOS',
        'source':{'commit':'unit'},'test':{'GENERAL_ONLY':{'n':n if n==0 else 10,'mse':.09},'HIERARCHICAL_ENV':{'n':n,'mse':.01}}})
    d=execute(root,basis=p)
    assert d['historical_basis']['decision']=='HOLD'


@pytest.mark.parametrize('output',['runtime/results','research/../../runtime'])
def test_output_cannot_write_production_or_escape_research(root,output):
    with pytest.raises(ValueError,match='OUTPUT_MUST_STAY'):execute(root,output=Path(output))


def test_tampered_hypothesis_protocol_is_rejected(root):
    execute(root);p=next((root/'research/bvi_research_cycle/hypotheses').glob('*.json'));d=cycle.load(p)
    d['protocol']['production_authority']=True;write(p,d)
    with pytest.raises(ValueError,match='HYPOTHESIS_PROTOCOL_CHANGED'):execute(root)


def test_missing_required_settlement_manifest_is_visible_without_stopping_quality(root):
    d=execute(root,settlement_manifest=root/'missing.json')
    assert d['settlement']['status']=='BLOCKED'
    assert d['settlement']['reason']=='REQUIRED_SETTLEMENT_MANIFEST_MISSING'
    assert d['counts']['registered_hypotheses']==7 and d['status']=='PARTIAL'


def test_cli_persists_failure_and_reuses_one_incident_id(root,monkeypatch):
    (root/sorted(cycle.BOUND_FILES)[0]).write_text('corrupted')
    monkeypatch.setattr(sys,'argv',['research-cycle','--root',str(root)])
    assert cycle.main()==1
    p=root/'research/bvi_research_cycle/current.json';first=cycle.load(p)
    assert first['status']=='BLOCKED' and first['audit_execution_complete'] is False
    assert cycle.main()==1
    second=cycle.load(p)
    assert second['incident_id']==first['incident_id']
    assert second['first_failure_sha256']==first['sha256']
    assert len(list((p.parent/'failures').glob('*.json')))==1


@pytest.mark.parametrize('mutation',['status','tested','effect','lifecycle'])
def test_rehashed_hypothesis_claims_are_not_accepted(root,mutation):
    execute(root);p=next((root/'research/bvi_research_cycle/hypotheses').glob('*.json'));d=cycle.load(p)
    changes={'status':('status','ACCEPTED'),'tested':('tested',True),
             'effect':('effect_estimate',.9),'lifecycle':('lifecycle_state','INDEPENDENTLY_REVIEWED')}
    key,value=changes[mutation];d[key]=value
    write(p,cycle.sealed({k:v for k,v in d.items() if k!='sha256'}))
    with pytest.raises(ValueError,match='HYPOTHESIS_PROTOCOL_CHANGED'):execute(root)


def test_rehashed_audit_cannot_fabricate_utility_or_oos(root):
    execute(root);p=next((root/'research/bvi_research_cycle/audits').glob('*.json'));d=cycle.load(p)
    d.update(prediction_utility_success=True,forward_oos_increment=30)
    d['ledgers']['BVI_ENV_FIXED_D']['eligible_settled_races']=30
    write(p,cycle.sealed({k:v for k,v in d.items() if k!='sha256'}))
    with pytest.raises(ValueError,match='AUDIT_CONTENT_CHANGED'):execute(root)


def test_rehashed_milestone_cannot_register_candidate_or_promote(root):
    ids=race_ids(30);install_groups(root,{'c1':group(ids)})
    for rid in ids:
        write(root/'runtime/jra_static_owner_forward_oos'/rid/'pedigree_env_result.json',
            cycle.sealed({'race_id':rid,'oos_eligible':True,'signed_result_verified':True,
                'policy_fingerprint':'c1','environment_candidate':{'model_sha256':cycle.FIXED_MODEL_SHA}}))
    execute(root);p=next((root/'research/bvi_research_cycle/milestones').glob('*.json'));d=cycle.load(p)
    d['next_cohort'].update(state='NEXT_COHORT_REGISTERED',candidate_id='UNVERIFIED')
    d['automatic_promotion']=True;write(p,cycle.sealed({k:v for k,v in d.items() if k!='sha256'}))
    current=execute(root)
    assert current['status']=='BLOCKED' and current['counts']['milestone_review_events']==0
    assert 'MILESTONE_CONTENT_CHANGED' in current['failures'][0]['reason']


def test_default_selects_persisted_latest_summary_and_quarantines_bad_or_future(root):
    folder=root/'runtime/pedigree_intake_receipts'
    base={'actual_reader_corpus':{'horse_count':4524,'run_count':45327},'permanent_registry_horse_ids':0}
    write(folder/'day-audit-1.json',cycle.sealed({**base,'created_at':'2026-10-31T00:00:00Z'}))
    write(folder/'day-audit-2.json',cycle.sealed({**base,'created_at':'2026-11-01T01:00:00Z'}))
    write(folder/'day-audit-3.json',cycle.sealed({**base,'created_at':'2026-11-07T00:00:00Z'}))
    write(folder/'day-audit-4.json',{**base,'created_at':'2026-11-01T02:00:00Z','sha256':'bad'})
    d=execute(root)
    assert d['quality']['summary_file_sha256']==cycle.file_sha(folder/'day-audit-2.json')
    assert len(d['quality']['quarantined_summaries'])==2
    assert d['quality']['scientific_training_qualified'] is False


def test_research_root_symlink_cannot_redirect_writes_to_production(root):
    (root/'research').symlink_to(root/'runtime',target_is_directory=True)
    with pytest.raises(ValueError,match='OUTPUT_MUST_STAY'):execute(root)
