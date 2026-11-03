"""Synthetic ZIP/gate correctness only; not real Provider rights or SOURCE."""
from copy import deepcopy
from datetime import datetime,timezone
import base64,csv,hashlib,io,zipfile
from pathlib import Path
import pytest
from runtime.local_fnb_csv_source_admission import assess,PROFILE,SOURCE_CLASS,sha
from runtime.local_nar_csv_reference import SCHEMAS
from runtime.local_fnb_r13_private_source_admission import admit,PURPOSE,SCOPE

NOW=datetime.fromisoformat('2026-11-03T03:21:00+00:00')
IDENTITY={'venue_id':'FNB','race_date':'2026-11-03','race_no':2,
 'scheduled_post_at':'2026-11-03T12:45:00+09:00','distance_m':1200,'surface':'DIRT','turn':'LEFT'}
REQUEST={'race_id':'KM-LOCAL-FNB-20261103-R02-RESEARCH-R1','family_id':'LOCAL',
 'venue_id':'FNB','race_date':'2026-11-03','race_no':2,
 'scheduled_post_at':IDENTITY['scheduled_post_at'],'prediction_cutoff':'2026-11-03T03:40:00+00:00',
 'race':{'race_date':'2026-11-03','race_no':2,'venue':'船橋','distance_m':1200,'surface':'DIRT','direction':'LEFT'},
 'runners':[{'runner_id':'1','name':'合成一号'},{'runner_id':'2','name':'合成二号'}]}

def inputs():
 race=dict.fromkeys(SCHEMAS['racelist'],'');race.update(競馬場='船橋',競走年月日='20261103',レース番号='2',発走時刻='1245',頭数='2',距離='1200',芝ダート区分='ダート',回り='左',天候='晴',馬場='良',条件='C3')
 horses=[]
 for n,name in ((1,'合成一号'),(2,'合成二号')):
  row=dict.fromkeys(SCHEMAS['horselist'],'');row.update(競馬場='船橋',競走年月日='20261103',レース番号='2',馬番=str(n),馬名=name,騎手名='合成騎手',齢='4',性='牡',負担重量='56.0',馬体重='490',馬体重増減='-2',父馬名='合成父',調教師='合成厩舎');horses.append(row)
 b=io.BytesIO()
 with zipfile.ZipFile(b,'w') as z:
  for kind,rows in [('racelist',[race]),('horselist',horses)]:
   s=io.StringIO(newline='');w=csv.writer(s);w.writerow(SCHEMAS[kind]);w.writerows([[r[k] for k in SCHEMAS[kind]] for r in rows]);z.writestr('20261103_'+kind+'.csv',s.getvalue())
 raw=b.getvalue();digest=hashlib.sha256(raw).hexdigest()
 capture={'provider':'NAR_OFFICIAL_CSV','http_status':200,'source_url':'https://www.keiba.go.jp/KeibaWeb/DataDownload/RaceDataDownload?type=daily',
  'retrieval_method':'OFFICIAL_BROWSER_DOWNLOAD','captured_at':'2026-11-03T03:19:00+00:00','raw_sha256':digest,'usage_qualification':{'status':'SYNTHETIC_NOT_REAL_QUALIFICATION'}}
 changes_raw=b'SYNTHETIC OFFICIAL CHANGE FIXTURE NOT EMPIRICAL'
 changes={'passed':True,'raw_sha256':hashlib.sha256(changes_raw).hexdigest(),'csv_raw_sha256':digest,
  'request_race_id':REQUEST['race_id'],'freeze_at':'2026-11-03T03:20:00+00:00','cutoff_at':REQUEST['prediction_cutoff'],'csv_captured_at':capture['captured_at'],
  'authority':'NAR_OFFICIAL','original_raw_reparsed':True,'external_receipt_verified':True,'receipt_sha256':'3'*64,
  'race_identity':deepcopy(IDENTITY),'official_race_id':'SYNTHETIC-OFFICIAL-COMPOSITE',
  'complete_declared_universe':True,'latest_changes_verified':True,'observed_at':'2026-11-03T03:20:00+00:00','source_updated_at':'2026-11-03T03:19:00+00:00',
  'runners':[{'horse_no':n,'name':name,'jockey':'合成騎手','status':'ACTIVE'} for n,name in ((1,'合成一号'),(2,'合成二号'))],'events':[]}
 rights={'passed':True,'provider_id':'NAR_OFFICIAL_CSV','raw_sha256':digest,'source_url':capture['source_url'],'retrieval_method':capture['retrieval_method'],
  'actor_id':'SYNTHETIC-TEST-ACTOR','permission_ref':'SYNTHETIC-NOT-PROVIDER-PERMISSION','permission_sha256':'2'*64,
  'private_retention_authorized':True,'cloud_processing_authorized':True,'retrieval_method_authorized':True,
  'effective_from':'2026-11-01T00:00:00+00:00','effective_until':'2026-12-01T00:00:00+00:00'}
 return {'raw':raw,'capture':capture,'request':deepcopy(REQUEST),'encoding':'utf-8','header_mode':'present',
  'freeze_at':'2026-11-03T03:20:00+00:00','actor_id':'SYNTHETIC-TEST-ACTOR','now':NOW,
  'qualification_verifier':lambda **kw:deepcopy(rights),'official_change_packet':{'raw':changes_raw},
  'official_change_verifier':lambda **kw:deepcopy(changes)},rights,changes


def test_validated_candidate_has_original_zip_and_parsed_schema_but_no_html_or_admission():
 args,_,_=inputs();out=assess(**args);s=out['source_candidate']
 assert out['ready_for_private_research_parsed_numeric'] is True
 assert out['formal_source_admitted'] is out['r13_r20_existing_admission_passed'] is False
 assert s['sources'][0]['source_class']==SOURCE_CLASS
 assert s['sources'][0]['official'] is False
 assert 'race_card_tables' not in s['normalized_evidence']
 assert 'raw_gzip_b64' not in s['sources'][0]
 assert base64.b64decode(s['sources'][0]['raw_b64'])==args['raw']
 assert s['parsed_runner_evidence']['1']['current_body_weight_change']==-2
 assert s['parsed_runner_evidence']['1']['horse_id'] is None
 assert s['parsed_runner_evidence']['1']['starts']==[]
 assert 'CSV_FORMAL_PROFILE_NOT_ADOPTED_R13_R20_HTML_GATES_UNCHANGED' in out['terminals']
 assert s['sha256']==sha({k:v for k,v in s.items() if k!='sha256'})
 with pytest.raises(ValueError,match='ONE_ORIGINAL_NAR_RACE_CARD_REQUIRED'):
  admit(source=s,request=args['request'],purpose=PURPOSE,classification=SCOPE,destination=Path('/tmp/csv-synthetic-test'),public_repo_root=Path(__file__).resolve().parents[1])


def test_capture_permission_booleans_cannot_substitute_for_external_gate():
 args,_,_=inputs();args['qualification_verifier']=None;args['capture']['usage_qualification']={'passed':True,'authorized':True}
 out=assess(**args);assert out['source_candidate'] is None
 assert 'CSV_PROVIDER_QUALIFICATION_UNVERIFIED' in out['terminals']


@pytest.mark.parametrize('field,value',[('actor_id','WRONG'),('raw_sha256','f'*64),('retrieval_method_authorized',False),('cloud_processing_authorized',False),('effective_until','2026-11-03T03:19:30+00:00')])
def test_provider_gate_binds_exact_actor_raw_method_and_validity(field,value):
 args,rights,_=inputs();rights[field]=value
 out=assess(**args);assert not out['ready_for_private_research_parsed_numeric']
 assert 'CSV_PROVIDER_QUALIFICATION_UNVERIFIED' in out['terminals']


def test_raw_hash_tamper_is_rejected_before_any_admission():
 args,_,_=inputs();args['raw']+=b'tamper'
 with pytest.raises(ValueError,match='PROVENANCE'):assess(**args)


def test_headcount_never_establishes_active_without_independent_official_raw_gate():
 args,_,_=inputs();args['official_change_verifier']=None
 out=assess(**args);assert out['source_candidate'] is None
 assert 'CSV_INDEPENDENT_OFFICIAL_CHANGES_UNVERIFIED' in out['terminals']


@pytest.mark.parametrize('field,value',[('raw_sha256','f'*64),('csv_raw_sha256','f'*64),('external_receipt_verified',False),('complete_declared_universe',False)])
def test_independent_change_evidence_is_bound_to_actual_bytes_and_csv(field,value):
 args,_,changes=inputs();changes[field]=value
 out=assess(**args);assert out['source_candidate'] is None
 assert 'CSV_INDEPENDENT_OFFICIAL_CHANGES_UNVERIFIED' in out['terminals']


def test_verified_scratch_excludes_only_official_inactive_and_preserves_declared():
 args,_,changes=inputs();changes['runners'][1]['status']='CANCELLED';args['request']['runners']=args['request']['runners'][:1]
 out=assess(**args);s=out['source_candidate']
 assert [r['runner_id'] for r in s['active_runner_universe']['runners']]==['1']
 assert len(s['declared_runner_universe']['runners'])==2
 assert list(s['parsed_runner_evidence'])==['1']


def test_new_jockey_requires_specific_verified_change_not_majority_or_name_guess():
 args,_,changes=inputs();changes['runners'][0]['jockey']='変更騎手'
 out=assess(**args);assert out['source_candidate'] is None
 assert 'CSV_JOCKEY_CONFLICT_WITHOUT_VERIFIED_CHANGE:1' in out['terminals']
 changes['events']=[{'horse_no':1,'field':'jockey','from':'合成騎手','to':'変更騎手'}]
 out=assess(**args);assert out['source_candidate']['parsed_runner_evidence']['1']['current_jockey']=='変更騎手'
 assert out['reconciled_official_changes'][0]['official_current_value']=='変更騎手'


def test_unknown_change_fields_hold_instead_of_silently_using_stale_weight():
 args,_,changes=inputs();changes['events']=[{'horse_no':1,'field':'body_weight','from':490,'to':495}]
 out=assess(**args);assert out['source_candidate'] is None
 assert 'CSV_OFFICIAL_CHANGE_FIELD_NOT_IMPLEMENTED:body_weight' in out['terminals']


def test_official_race_same_alias_with_different_conditions_is_not_equal():
 args,_,changes=inputs();changes['race_identity']['distance_m']=1500
 out=assess(**args);assert out['source_candidate'] is None
 assert 'CSV_OFFICIAL_RACE_CONDITION_CONFLICT:distance_m' in out['terminals']


def test_forecast_cannot_be_backdated_or_run_after_cutoff():
 args,_,_=inputs();args['now']=datetime.fromisoformat('2026-11-03T03:41:00+00:00')
 out=assess(**args);assert out['source_candidate'] is None
 assert 'CSV_FETCH_FREEZE_NOW_CUTOFF_POST_ORDER_INVALID' in out['terminals']


def test_external_signature_matching_never_adopts_new_profile():
 args,_,_=inputs();args['source_receipt']={'SYNTHETIC':'NOT_REAL_SIGNATURE'}
 args['source_receipt_verifier']=lambda **kw:{'passed':True,'profile_id':PROFILE,'signature_verified':True,
  'source_candidate_sha256':kw['source_candidate']['sha256'],'raw_sha256':kw['source_candidate']['sources'][0]['raw_sha256'],'receipt_sha256':'4'*64}
 out=assess(**args)
 assert out['external_signature_verified_by_supplied_gate'] is True
 assert out['formal_source_admitted'] is False
 assert out['r13_r20_existing_admission_passed'] is False
 assert out['new_OOS']==0


@pytest.mark.parametrize('field,value',[('official_race_id',None),('freeze_at','2026-11-03T03:18:00+00:00'),('cutoff_at','2026-11-03T03:39:00+00:00'),('request_race_id','OTHER'),('source_updated_at','2026-11-03T03:22:00+00:00')])
def test_missing_identity_or_stale_temporal_binding_is_terminal(field,value):
 args,_,changes=inputs();changes[field]=value
 out=assess(**args);assert out['source_candidate'] is None
 assert 'CSV_INDEPENDENT_OFFICIAL_CHANGES_UNVERIFIED' in out['terminals']


def test_csv_facts_are_consumed_by_existing_research29_without_making_history_or_formal_source():
 from runtime.local_fnb_csv_source_admission import compile_research_numeric
 args,_,_=inputs();out=assess(**args);numeric=compile_research_numeric(out,args['request'])
 assert len(numeric['runners'])==2
 assert all(len(r['canonical_components'])==29 for r in numeric['runners'])
 assert all(r['raw_candidate_evidence']['starts']==[] for r in numeric['runners'])
 assert numeric['csv_research_consumer']['zip_raw_sha256']==args['capture']['raw_sha256']
 assert numeric['csv_research_consumer']['formal_source_admitted'] is False
 assert all(v['production_authority'] is False for r in numeric['runners'] for v in r['canonical_components'].values())


def test_missing_profile_adoption_cannot_be_replaced_by_even_a_trusted_signature_callback():
 from runtime.local_fnb_csv_source_admission import consume_with_approved_profile,CsvConsumerBinding
 args,_,_=inputs();out=assess(**args)
 binding=CsvConsumerBinding('a'*64,'b'*64,'SINGLE_RACE_PRESTART_NONPRODUCTION_NOT_REGISTERED_OOS',lambda **kw:{'passed':True},lambda **kw:{'passed':True})
 with pytest.raises(ValueError,match='PROFILE_NOT_ADOPTED'):
  consume_with_approved_profile(out,args['request'],binding=binding,source_receipt={})


def test_exact_adopted_private_profile_and_signed_gate_can_consume_without_formal_promotion(tmp_path):
 """Exercise the dormant path with synthetic approvals in an isolated repo."""
 import json
 import runtime.local_fnb_csv_source_admission as m
 repo=Path(__file__).resolve().parents[1]
 actual_profile=repo/'profiles/local_fnb_nar_csv_source_candidate_v0.1_20261103.json'
 original=actual_profile.read_bytes()
 profile=json.loads(original);profile.update(enabled=True,status='APPROVED_PRIVATE_NONPRODUCTION_CSV_PROFILE')
 (tmp_path/'profiles').mkdir();target=tmp_path/'profiles'/actual_profile.name
 target.write_text(json.dumps(profile))
 (tmp_path/'mapping').symlink_to(repo/'mapping',target_is_directory=True)
 args,_,_=inputs();out=assess(**args)
 scope='SINGLE_RACE_PRESTART_NONPRODUCTION_NOT_REGISTERED_OOS'
 profile_sha=hashlib.sha256(target.read_bytes()).hexdigest()
 def approved(**kw):return {'passed':True,'profile_sha256':kw['profile_sha256'],'scope':scope,'approval_ref':'SYNTHETIC_ONLY','approval_sha256':'5'*64,'effective_from':'2026-11-03T00:00:00+00:00','effective_until':'2026-11-04T00:00:00+00:00'}
 def signed(**kw):return {'passed':True,'signature_verified':True,'profile_id':PROFILE,'scope':scope,
  'source_candidate_sha256':kw['source_candidate']['sha256'],'race_id':args['request']['race_id'],
  'cutoff_at':args['request']['prediction_cutoff'],'freeze_at':args['freeze_at'],'receipt_sha256':'6'*64}
 binding=m.CsvConsumerBinding(profile_sha,hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest(),scope,approved,signed,actor_id='SYNTHETIC-TEST-ACTOR')
 result=m.consume_with_approved_profile(out,args['request'],binding=binding,source_receipt={'fixture':'NOT_REAL'},repo_root=tmp_path,now=NOW)
 assert len(result['numerical']['runners'])==2
 assert result['csv_private_profile_admission']['formal_R13_R20_admission'] is False
 assert result['csv_private_profile_admission']['production_numeric_consumers_authorized'] is False
 assert actual_profile.read_bytes()==original
 # An exact approved Profile cannot substitute for an actual SOURCE verifier.
 bad=m.CsvConsumerBinding(profile_sha,binding.adapter_code_sha256,scope,approved,lambda **kw:{'passed':True},actor_id='SYNTHETIC-TEST-ACTOR')
 with pytest.raises(ValueError,match='SOURCE_SIGNATURE_GATE_UNVERIFIED'):
  m.consume_with_approved_profile(out,args['request'],binding=bad,source_receipt={},repo_root=tmp_path,now=NOW)
 with pytest.raises(ValueError,match='CUTOFF_EXPIRED'):
  m.consume_with_approved_profile(out,args['request'],binding=binding,source_receipt={},repo_root=tmp_path,now='2026-11-03T03:45:00+00:00')


@pytest.mark.parametrize('mutation',[
 lambda q:q['race'].update(distance_m=1500),
 lambda q:q['race'].update(**{'class':'A1'}),
 lambda q:q.update(prediction_cutoff='2026-11-03T03:44:00+00:00'),
 lambda q:q['runners'][0].update(name='変更馬名'),
])
def test_request_cannot_change_after_assessment_even_with_same_race_id(mutation):
 from runtime.local_fnb_csv_source_admission import compile_research_numeric
 args,_,_=inputs();out=assess(**args);mutation(args['request'])
 with pytest.raises(ValueError,match='ASSESSED_REQUEST_OR_HASH_MISMATCH'):
  compile_research_numeric(out,args['request'])
