"""Successor boundary, isolation, temporal and real-input provenance checks."""
import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
import jra_bvi_successor_research as s

NOW = '2026-11-01T12:00:00+00:00'


def write(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')


def install(root, *, extra=None):
    horses=[]
    for i in range(8):
        rows=[]
        for j,day in enumerate(['2026-01-03','2026-03-03','2026-05-03','2026-06-03',
                                '2026-07-03','2026-08-03','2026-09-03','2026-10-03']):
            rows.append(dict(date=day,venue='東京',surface='芝',distance_m=1600,
                             race_name='2勝クラス',finish=2+i,field_size=12,going='良'))
        if extra: rows += copy.deepcopy(extra)
        horses.append(dict(horse_name='合成馬'+str(i),sire='父'+str(i//4),dam='母'+str(i),
                           damsire='母父'+str(i//4),runs=rows))
    harvest=dict(official=True,source='www.jra.go.jp',harvested_at='2026-11-01T09:00:00Z',horses=horses)
    import hashlib
    harvest['sha256']=hashlib.sha256(json.dumps(harvest,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    path=root/'runtime/pedigree_corpus/test.json';write(path,harvest)
    summary=s.seal(dict(created_at='2026-11-01T10:00:00Z',target_race_date='2026-11-02',
        unique_composite_horses=8,unique_dedicated_prior_runs=8*len(horses[0]['runs']),
        verified_harvest_artifacts=[dict(file='test.json',file_sha256=s.file_sha(path),sha256=harvest['sha256'],
                                       oidc_verified_by='2026-11-01T09:30:00Z')]))
    target=root/'runtime/pedigree_intake_receipts/day-audit-test.json';write(target,summary)
    return target,path


def test_screen_excludes_named_jump_mixed_foreign_but_never_claims_complete_flat():
    base=dict(venue='東京',surface='芝',race_name='2勝クラス')
    assert s.screen(base) is None
    assert s.screen({**base,'race_name':'東京ハイＪ'})=='EXPLICIT_NAMED_JUMP'
    assert s.screen({**base,'race_name':'中山GJ'})=='EXPLICIT_NAMED_JUMP'
    assert s.screen({**base,'raw_surfaces':['芝ダ']})=='NON_SINGLE_FLAT_SURFACE'
    assert s.screen({**base,'venue':'大井'})=='NON_JRA_VENUE'


def test_dedicated_rows_provenance_and_training_cutoffs(tmp_path):
    summary,path=install(tmp_path)
    dataset=s.dataset_from_summary(tmp_path,summary,NOW)
    assert dataset['counts']['screened_rows']==64
    assert dataset['counts']['screened_composite_horses']==8
    assert dataset['counts']['independent_official_labels']==0
    assert not dataset['scientific_training_qualified'] and not dataset['certified_flat']
    assert all(r['provenance']==['test.json'] for r in dataset['rows'])
    report=s.evaluate_fold(dataset,s.PROTOCOL['folds'][0])
    assert report['training_runs']==40
    assert report['partitions']['VALIDATION']['n']==8
    assert report['partitions']['TEST']['n']==8
    assert report['partitions']['TEST']['metrics']['ENV']['n']==report['partitions']['TEST']['metrics']['GENERAL']['n']
    assert report['partitions']['TEST']['cluster_intervals']['horse_id']['clusters']==8
    assert report['partitions']['TEST']['cluster_intervals']['date']['interval'] is None


@pytest.mark.parametrize('mutation',['raw','selfhash','summary','future','denominator','path'])
def test_invalid_inherited_inputs_never_fit(tmp_path,mutation):
    summary,path=install(tmp_path); d=s.read(summary)
    if mutation=='raw': path.write_text(path.read_text()+' ')
    if mutation=='selfhash':
        h=s.read(path);h['sha256']='0'*64;write(path,h);d['verified_harvest_artifacts'][0]['file_sha256']=s.file_sha(path)
    if mutation=='summary':d['sha256']='0'*64
    if mutation=='future':d['created_at']='2026-11-02T10:00:00Z'
    if mutation=='denominator':d['unique_dedicated_prior_runs']+=1
    if mutation=='path':d['verified_harvest_artifacts'][0]['file']='../test.json'
    if mutation!='summary':d=s.seal({k:v for k,v in d.items() if k!='sha256'})
    write(summary,d)
    with pytest.raises(ValueError):s.run(tmp_path,summary_path=summary,observed_at=NOW)
    assert not list((tmp_path/'research').glob('**/model.json'))


def test_retry_reuses_model_and_never_edits_fixed_or_production(tmp_path,monkeypatch):
    summary,_=install(tmp_path)
    fixed=tmp_path/'runtime/fixed.json';write(fixed,{'unchanged':'fixed D marker'})
    before=fixed.read_bytes()
    one=s.run(tmp_path,observed_at=NOW)
    path=tmp_path/one['record']; original=path.read_bytes()
    monkeypatch.setattr(s,'train_model',lambda *a,**k:pytest.fail('same inputs must not refit'))
    two=s.run(tmp_path,observed_at='2026-11-01T13:00:00Z')
    assert one['candidate_id']==two['candidate_id']
    assert original==path.read_bytes() and fixed.read_bytes()==before
    assert two['last_checked_at']!=one['last_checked_at']
    assert two['next_cohort_state']=='WAITING_ELIGIBLE_CANDIDATE' and two['forward_oos_increment']==0


def test_tampered_cached_artifact_rejected_not_replaced(tmp_path):
    install(tmp_path);one=s.run(tmp_path,observed_at=NOW)
    folder=(tmp_path/one['record']).parent
    path=folder/'evaluation.json';path.write_text(path.read_text()+' ')
    with pytest.raises(ValueError,match='SAVED_ARTIFACT_CHANGED'):s.run(tmp_path,observed_at=NOW)


def test_folds_are_not_combined_into_a_false_independent_sample(tmp_path):
    summary,_=install(tmp_path)
    out=s.run(tmp_path,observed_at=NOW)
    report=s.read((tmp_path/out['record']).with_name('evaluation.json'))
    assert report['folds_are_not_pooled'] is True
    assert report['scientific_training_qualified'] is False
    assert report['capital_pfs'] is None and report['prediction_utility_success'] is False
    assert s.read(tmp_path/out['record'])['lifecycle_state']=='HISTORICAL_TESTED'


def test_repeated_horse_clusters_do_not_gain_independent_sample_size():
    r=[{'horse_id':'h1'},{'horse_id':'h1'}]
    assert s.cluster_interval(r,[.1,.1],'horse_id')['interval'] is None
    assert s.cluster_interval(r,[.1,.1],'sire')['status']=='MISSING_CLUSTER_ID'


@pytest.mark.parametrize('output',['runtime/results','research/../../runtime'])
def test_successor_cannot_write_outside_research(tmp_path,output):
    install(tmp_path)
    with pytest.raises(ValueError,match='OUTPUT_MUST_STAY'):s.run(tmp_path,output=output,observed_at=NOW)


def test_no_available_admissions_is_pending_work_not_empty_model(tmp_path):
    out=s.run(tmp_path,observed_at=NOW)
    assert out['status']=='NOT_EXECUTED'
    assert out['forward_oos_increment']==0 and not (tmp_path/'research').exists()


def test_interrupted_payload_write_resumes_original_acquisition_clock(tmp_path,monkeypatch):
    install(tmp_path);original=s.immutable
    def stop_before_record(path,value):
        if path.name=='record.json':raise OSError('injected interruption')
        return original(path,value)
    monkeypatch.setattr(s,'immutable',stop_before_record)
    with pytest.raises(OSError,match='injected'):s.run(tmp_path,observed_at=NOW)
    first=next((tmp_path/'research/bvi_successor').glob('*/dataset.json.gz')).read_bytes()
    monkeypatch.setattr(s,'immutable',original)
    out=s.run(tmp_path,observed_at='2026-11-01T13:00:00Z')
    assert (tmp_path/out['record']).with_name('dataset.json.gz').read_bytes()==first
    assert s.read(tmp_path/out['record'])['created_at']==NOW


@pytest.mark.parametrize('field,value',[('decision','ACCEPTED'),('status','VERIFIED_COMPLETE'),
    ('next_cohort_state','FORWARD_OOS_ACTIVE'),('production_authority',True)])
def test_resealed_progress_or_authority_is_not_a_valid_cached_record(tmp_path,field,value):
    install(tmp_path);out=s.run(tmp_path,observed_at=NOW);path=tmp_path/out['record']
    changed=s.read(path);changed[field]=value
    write(path,s.seal({k:v for k,v in changed.items() if k!='sha256'}))
    with pytest.raises(ValueError,match='SAVED_RECORD_CONTENT_CHANGED'):s.run(tmp_path,observed_at=NOW)
