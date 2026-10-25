"""Adversarial offline qualification and exact RESULT-context boundaries."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

SPEC=importlib.util.spec_from_file_location('identity_label_audit',Path(__file__).with_name('identity_label_audit.py'))
audit=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


def seal(obj):
    obj['sha256']=audit.sha_obj({k:v for k,v in obj.items() if k!='sha256'})
    return obj


def fixture(tmp_path,monkeypatch):
    names=['runtime/pedigree_corpus/a.json','runtime/executions/source.json']
    hashes={}
    for name in names:
        p=tmp_path/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('{}\n')
        hashes[name]=audit.raw_sha(p)
    row={'corpus_file':names[0],'observation_index':0,'official_profile_token':'UNIT-NAV-NOT-ID',
         'proof':'unit','chronology_before_target':True,
         'run_bindings':[{'proof':'unit','chronology_before_target':True}]}
    r=seal({'target_cutoff':'2026-10-24T09:00:00+09:00',
            'corpus_files':{names[0]:{'file_sha256':hashes[names[0]]}},
            'source_files':{names[1]:hashes[names[1]]},
            'raw_proofs':{'unit':{'source_envelope':names[1]}},'resolved':[row]})
    q=seal({'recovery_sha256':r['sha256'],'target_cutoff':r['target_cutoff'],
            'research_training_eligible':False,'production_eligible':False,
            'permanent_registry_ids_resolved':0,
            'file_verifications':{name:{'file_sha256':h,'qualified':True,
                'checks':[{'verified':True,'verified_timestamps':['2026-10-20T00:00:00Z']}]}
                for name,h in hashes.items()},
            'qualified':[{'corpus_file':names[0],'observation_index':0,
                          'official_profile_token':'UNIT-NAV-NOT-ID'}],
            'qualified_profile_locator_observations':1,'qualified_result_locator_runs':1})
    called=[]
    monkeypatch.setattr(audit,'verify_recovery_bindings',lambda *args:called.append(args))
    return r,q,called


def test_retrieved_qualification_rebinds_originals_before_counting(tmp_path,monkeypatch):
    r,q,called=fixture(tmp_path,monkeypatch)
    rows,runs=audit.validate_qualification(r,q,tmp_path)
    assert rows==r['resolved'] and runs==1 and len(called)==1
    assert rows[0]['official_profile_token']=='UNIT-NAV-NOT-ID'
    assert q['permanent_registry_ids_resolved']==0


@pytest.mark.parametrize('mutation',['future_clock','changed_bytes','false_count','permanent_promotion','missing_binding'])
def test_rehashed_sidecar_does_not_establish_clock_or_identity(tmp_path,monkeypatch,mutation):
    r,q,_=fixture(tmp_path,monkeypatch)
    if mutation=='future_clock':
        for item in q['file_verifications'].values():item['checks'][0]['verified_timestamps']=['2026-10-25T00:00:00Z']
    elif mutation=='changed_bytes':(tmp_path/'runtime/pedigree_corpus/a.json').write_text('{"changed":true}')
    elif mutation=='false_count':q['qualified_profile_locator_observations']=2
    elif mutation=='permanent_promotion':q['permanent_registry_ids_resolved']=1
    else:q['qualified'][0]['official_profile_token']='UNSEEN-OPAQUE-ALIAS'
    seal(q)
    with pytest.raises(ValueError):audit.validate_qualification(r,q,tmp_path)


def test_result_id_comes_from_verified_source_context_not_token_decoding():
    art={'race_id':'KM-JRA-TKY-20261018-R10',
         'source_race_context':{'venue_id':'TKY','race_date':'2026-10-18','race_no':10}}
    assert audit.result_identity(art,1)==('KM-JRA-TKY-20261018-R01','2026-10-18','東京')
    art['source_race_context']['venue_id']='KYO'
    with pytest.raises(ValueError):audit.result_identity(art,1)
    assert audit.surface('芝ダ')=='芝ダ'


def test_independent_result_original_heading_must_match_context():
    from bs4 import BeautifulSoup
    soup=BeautifulSoup('<h1>レース結果 2026年10月18日（日曜）4回東京7日 1レース</h1>','html.parser')
    audit.verify_result_heading(soup,'2026-10-18','東京',1)
    for day,venue,race in [('2026-10-19','東京',1),('2026-10-18','京都',1),('2026-10-18','東京',2)]:
        with pytest.raises(ValueError):audit.verify_result_heading(soup,day,venue,race)


def test_all_ten_official_venue_ids_use_existing_registry():
    assert len(audit.VENUES)==10 and audit.VENUES['KKR']=='小倉'
    for venue,name in audit.VENUES.items():
        art={'race_id':f'KM-JRA-{venue}-20261018-R10',
             'source_race_context':{'venue_id':venue,'race_date':'2026-10-18','race_no':10}}
        assert audit.result_identity(art,1)==(f'KM-JRA-{venue}-20261018-R01','2026-10-18',name)
