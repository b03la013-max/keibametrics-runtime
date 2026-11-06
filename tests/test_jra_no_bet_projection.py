"""Synthetic zero-exposure fixtures; no Source, signature, delivery or OOS credit."""
from copy import deepcopy
import ast
import json
from pathlib import Path
import re
from types import SimpleNamespace
import pytest

from test_jra_no_bet_postresult_learning import build_input,run
from jra_no_bet_postresult_learning import (JRANoBetLearningError,_hash,
    select_no_bet_paths,build_no_bet_review_state,persist_no_bet_review_state,require_no_bet_final_absent,verify_no_bet_oidc)

ROOT=Path(__file__).resolve().parents[1]
RACE='KM-JRA-TKY-20261010-R05'
EFFECTIVE='2026-10-10T13:05:00+09:00'

def fixture():
    terminal,result=build_input()
    return terminal,run(terminal,result)

def project(terminal,learning,**kwargs):
    return build_no_bet_review_state(terminal,learning,effective_time=EFFECTIVE,
                                    official_capture_verified=True,**kwargs)

def verified_oidc_fixture(command):
    from hashlib import sha256
    path=Path(command[3]);workflow=command[command.index('--signer-workflow')+1]
    terminal=workflow.endswith('km-jra-formal-single-entry.yml')
    capture=not terminal and '--source-digest' in command
    code='2'*40 if terminal else '1'*40 if capture else '3'*40
    certificate={'issuer':'https://token.actions.githubusercontent.com',
       'subjectAlternativeName':'https://github.com/'+workflow+'@refs/heads/main',
       'sourceRepositoryDigest':code,'sourceRepositoryRef':'refs/heads/main','runnerEnvironment':'github-hosted',
       'runInvocationURI':'https://github.com/b03la013-max/keibametrics-runtime/actions/runs/123/attempts/1'}
    value={'verificationResult':{'signature':{'certificate':certificate},
       'verifiedTimestamps':[{'timestamp':'2026-10-10T12:11:00+09:00' if terminal else '2026-10-10T13:00:01+09:00'}],
       'statement':{'subject':[{'digest':{'sha256':sha256(path.read_bytes()).hexdigest()}}]}}}
    return SimpleNamespace(stdout=json.dumps([value])),value

def test_exact_manual_selector_excludes_other_races_in_both_existing_worker_stages(tmp_path):
    touched=[]
    for folder in ('terminals','captures'):
        directory=tmp_path/folder;directory.mkdir()
        for eid in (RACE+'-LIVE-R1','KM-JRA-TKY-20261010-R06-LIVE-R1','KM-JRA-KYO-20261010-R05-LIVE-R1'):
            (directory/(eid+'.json')).write_text(json.dumps({'race_id':eid.split('-LIVE')[0]}))
        for path in select_no_bet_paths(directory,RACE):
            touched.append(json.loads(path.read_text())['race_id'])
        assert len(select_no_bet_paths(directory))==3
    assert touched==[RACE,RACE]
    assert sum(x!=RACE for x in touched)==0

@pytest.mark.parametrize('selected',['KM-LOCAL-TKY-20261010-R05','KM-JRA-XXX-20261010-R05',
    'KM-JRA-TKY-20260230-R05','KM-JRA-TKY-20261010-R13',RACE+'-LIVE-R1',False])
def test_invalid_selector_fails_before_any_official_source_attempt(tmp_path,selected):
    with pytest.raises(JRANoBetLearningError,match='SELECTOR_INVALID'):
        select_no_bet_paths(tmp_path,selected)

def test_ambiguous_revisions_hold_instead_of_spending_on_multiple_captures(tmp_path):
    for rev in (1,2):(tmp_path/f'{RACE}-LIVE-R{rev}.json').write_text('{}')
    with pytest.raises(JRANoBetLearningError,match='AMBIGUOUS_EXECUTION'):
        select_no_bet_paths(tmp_path,RACE)

def test_workflow_both_stages_use_same_optional_selector_and_no_broad_copy_before_projection():
    text=(ROOT/'.github/workflows/km-jra-no-bet-postresult-learning.yml').read_text()
    assert 'Optional exact JRA Race ID' in text
    assert text.count('RACE_ID_FILTER: ${{ inputs.race_id }}')==2
    assert 'select_no_bet_paths(Path("runtime/jra_no_bet_terminals"),selected)' in text
    assert 'select_no_bet_paths(Path("runtime_out/capture"),selected)' in text
    assert text.index('projection=persist_no_bet_review_state(')<text.index('dest=Path("runtime_out/learning")/path.name')
    # Keep the embedded Python parseable without starting a worker.
    embedded=list(re.finditer(r"(?m)^          python - <<'PY'\n(.*?)(?m:^          PY)$",text,re.S))
    assert len(embedded)==3  # capture, settle, and final Owner B health reflection
    for match in embedded:
        ast.parse('\n'.join(line[10:] for line in match[1].splitlines()))

def test_zero_exposure_projects_to_shared_review_state_without_a_fake_final():
    terminal,learning=fixture();before=deepcopy((terminal,learning))
    out=project(terminal,learning);review,state=out['review'],out['state']
    assert (terminal,learning)==before
    assert review['source_no_bet_result_sha256']==learning['sha256']
    assert review['source_no_bet_terminal_sha256']==terminal['sha256']
    assert not {'final_receipt_sha256','immutable_final_artifact_sha256'}&set(review)
    assert review['prediction']['role_capture']=={}
    assert review['failure_localization']['no_bet_reason']==terminal['decision_reason']
    assert review['failure_localization']['prediction_quality_assessment']=='NOT_PERFORMED_WITHOUT_SIGNED_FINAL'
    assert review['capital']['investment']==review['capital']['return']==0
    assert review['capital']['pfs'] is None
    assert review['pfs_improvement']['pfs_status']=='NOT_APPLICABLE'
    assert state['source_review_sha256']==review['sha256']
    assert state['reference_metrics']['pfs'] is None
    assert state['reference_metrics']['zero_exposure'] is True
    assert state['reference_metrics']['first_material_failure']=='NONE' and state['shadow_candidates']==[]
    assert state['production_change_authorized'] is False
    assert state['learning_validity']=='FAMILY-CANDIDATE'
    assert state['prediction_use']=='SHADOW_REVIEW_CONTEXT_ONLY'
    assert state['numeric_production_learning_consumption']=='NOT_ESTABLISHED'

@pytest.mark.parametrize('patch',[{'race_id':'KM-JRA-KYO-20261010-R05'},
    {'decision_lineage_sha256':'b'*64},{'ticket_count':1},{'investment':100},{'pfs':0},
    {'family_id':'LOCAL'},{'profile':'UNAPPROVED'},
    {'signed_final_verified':True},{'production_effect':'APPLIED'}])
def test_rehashed_conflicting_or_nonzero_learning_cannot_gain_state_admission(patch):
    terminal,learning=fixture();learning.update(patch)
    learning['sha256']=_hash({k:v for k,v in learning.items() if k!='sha256'})
    with pytest.raises(JRANoBetLearningError,match='PROJECTION_BINDING'):
        project(terminal,learning)

def test_unverified_capture_or_backdated_state_is_rejected():
    terminal,learning=fixture()
    with pytest.raises(JRANoBetLearningError,match='CAPTURE_NOT_VERIFIED'):
        build_no_bet_review_state(terminal,learning,effective_time=EFFECTIVE)
    with pytest.raises(JRANoBetLearningError,match='EFFECTIVE_TIME'):
        build_no_bet_review_state(terminal,learning,effective_time='2026-10-10T12:59:00+09:00',official_capture_verified=True)

def test_existing_shadow_consumer_obeys_time_and_same_race_exclusion_without_numeric_activation():
    from jra_role_learning_shadow import intake
    terminal,learning=fixture();state=project(terminal,learning)['state']
    def consume(race,source):
        return intake([state],race_id=race,source_freeze=source,
                      observed_at='2026-10-10T13:20:00+09:00',cutoff='2026-10-10T13:25:00+09:00')
    accepted=consume('KM-JRA-TKY-20261010-R06','2026-10-10T13:15:00+09:00')
    assert len(accepted['accepted'])==1 and accepted['production_effect']=='NONE'
    assert accepted['scope']=='SHADOW_ONLY'
    assert consume(RACE,'2026-10-10T13:15:00+09:00')['excluded'][0]['reason']=='SAME_RACE_LEAKAGE'
    assert consume('KM-JRA-TKY-20261010-R06','2026-10-10T13:00:00+09:00')['excluded'][0]['reason']=='NOT_AVAILABLE_BEFORE_SOURCE'

def test_persistence_uses_existing_layout_and_reuses_identical_records_without_overwrite(tmp_path):
    terminal,learning=fixture();eid=RACE+'-LIVE-R1'
    kwargs=dict(execution_id=eid,effective_time=EFFECTIVE,official_capture_verified=True)
    out=persist_no_bet_review_state(tmp_path,terminal,learning,**kwargs)
    files=sorted(tmp_path.rglob('*.json'));assert len(files)==3
    before={p:p.read_bytes() for p in files}
    kwargs['effective_time']='2026-10-10T13:30:00+09:00'
    assert persist_no_bet_review_state(tmp_path,terminal,learning,**kwargs)==out
    assert out['state']['effective_time']==EFFECTIVE
    assert before=={p:p.read_bytes() for p in files}
    assert not (tmp_path/'runtime/final_artifacts').exists()

def test_projection_conflict_and_existing_final_hold_before_other_canonical_writes(tmp_path):
    terminal,learning=fixture();eid=RACE+'-LIVE-R1'
    for label,relative in [('conflict',f'runtime/learning_states/{RACE}.json'),
                           ('final',f'runtime/final_artifacts/{RACE}.json')]:
        root=tmp_path/label;p=root/relative;p.parent.mkdir(parents=True);p.write_text('{}')
        with pytest.raises(JRANoBetLearningError):
            persist_no_bet_review_state(root,terminal,learning,execution_id=eid,effective_time=EFFECTIVE,official_capture_verified=True)
        assert list(root.rglob('*.json'))==[p] and p.read_text()=='{}'


def test_existing_state_is_not_trusted_or_retimed_for_a_different_result_basis(tmp_path):
    terminal,learning=fixture();kwargs=dict(execution_id=RACE+'-LIVE-R1',effective_time=EFFECTIVE,official_capture_verified=True)
    persist_no_bet_review_state(tmp_path,terminal,learning,**kwargs)
    before={p:p.read_bytes() for p in tmp_path.rglob('*.json')}
    different=deepcopy(learning);different['post_race_official_snapshot_sha256']='b'*64
    different['sha256']=_hash({k:v for k,v in different.items() if k!='sha256'})
    kwargs['effective_time']='2026-10-10T13:30:00+09:00'
    with pytest.raises(JRANoBetLearningError,match='IMMUTABLE_CONFLICT'):
        persist_no_bet_review_state(tmp_path,terminal,different,**kwargs)
    kwargs['effective_time']='2026-10-10T13:04:00+09:00'
    with pytest.raises(JRANoBetLearningError,match='EFFECTIVE_TIME'):
        persist_no_bet_review_state(tmp_path,terminal,learning,**kwargs)
    assert before=={p:p.read_bytes() for p in tmp_path.rglob('*.json')}
    p=tmp_path/f'runtime/learning_states/{RACE}.json';state=json.loads(p.read_text());state['sha256']='f'*64
    p.write_text(json.dumps(state));kwargs['effective_time']='2026-10-10T13:30:00+09:00'
    with pytest.raises(JRANoBetLearningError,match='IMMUTABLE_CONFLICT'):
        persist_no_bet_review_state(tmp_path,terminal,learning,**kwargs)


def test_missing_state_is_created_at_new_actual_time_not_old_capture_time(tmp_path):
    terminal,learning=fixture();kwargs=dict(execution_id=RACE+'-LIVE-R1',effective_time=EFFECTIVE,official_capture_verified=True)
    old=persist_no_bet_review_state(tmp_path,terminal,learning,**kwargs)
    path=tmp_path/f'runtime/learning_states/{RACE}.json';path.unlink()
    kwargs['effective_time']='2026-10-10T13:30:00+09:00'
    now=persist_no_bet_review_state(tmp_path,terminal,learning,**kwargs)
    assert now['review']==old['review']
    assert now['state']['effective_time']==kwargs['effective_time']
    assert now['state']['effective_time']!=learning['post_race_official_acquired_at']


def test_late_final_after_rebase_stops_the_existing_push_step(tmp_path,monkeypatch):
    import os,subprocess,sys
    require_no_bet_final_absent(tmp_path,[RACE])
    folder=tmp_path/'runtime_out/states';folder.mkdir(parents=True)
    (folder/(RACE+'-LIVE-R1.json')).write_text(json.dumps({'race_id':RACE}))
    (tmp_path/'runtime_out/learning').mkdir()
    bindir=tmp_path/'bin';bindir.mkdir();fake=bindir/'git'
    fake.write_text('#!'+sys.executable+'\n'+
        "from pathlib import Path\nimport sys\nargs=sys.argv[1:]\n"+
        "with open('git_calls','a') as f:f.write(' '.join(args)+'\\n')\n"+
        "if args[:2]==['diff','--cached']:raise SystemExit(1)\n"+
        "if args[:2]==['pull','--rebase']:\n"+
        " p=Path('runtime/final_artifacts')/"+repr(RACE+'.json')+";p.parent.mkdir(parents=True,exist_ok=True);p.write_text('{}')\n")
    fake.chmod(0o755)
    text=(ROOT/'.github/workflows/km-jra-no-bet-postresult-learning.yml').read_text()
    body=text.split('      - name: Persist immutable zero-bet Learning, exclude from PFS and OOS\n',1)[1].split('        run: |\n',1)[1]
    script='\n'.join(line[10:] for line in body.splitlines())
    env=dict(os.environ,PATH=str(bindir)+os.pathsep+os.environ['PATH'],PYTHONPATH=os.pathsep.join(sys.path))
    result=subprocess.run(['bash','-c',script],cwd=tmp_path,env=env,capture_output=True,text=True)
    assert result.returncode!=0 and 'SIGNED_FINAL_BRANCH_EXISTS' in result.stderr
    calls=(tmp_path/'git_calls').read_text().splitlines()
    assert 'pull --rebase origin main' in calls and not any(x.startswith('push ') for x in calls)


def test_no_bet_cannot_dilute_capital_pfs_or_accuracy_denominators():
    from family_pfs_owner_scorecard import build_owner_scorecard
    terminal,learning=fixture();review=project(terminal,learning)['review']
    financial={'race_id':'KM-JRA-TKY-20261010-R04',
        'capital':{'investment':100,'return':50,'pfs':50,'hit':True,'hit_but_loss':True},
        'failure_localization':{'first_material_failure':'CAPITAL_EFFICIENCY'}}
    before=deepcopy(review)
    assert build_owner_scorecard([financial,review])==build_owner_scorecard([financial])
    empty=build_owner_scorecard([review])['aggregate']
    assert empty['race_count']==0 and empty['pfs'] is None and empty['hit_but_loss_rate'] is None
    assert review==before
    # This repair does not silently reinterpret the frozen other-family path.
    for family in ('LOCAL','BAN'):
        other=deepcopy(review);other['race_id']=other['race_id'].replace('JRA',family)
        assert build_owner_scorecard([other])['aggregate']['race_count']==1


def test_shadow_acceptance_of_no_bet_context_never_adds_a_numeric_learning_ticket():
    from jra_role_learning_shadow import build_shadow,digest
    terminal,learning=fixture();state=project(terminal,learning)['state']
    rid='KM-JRA-TKY-20261031-R06';cutoff='2026-10-31T13:25:00+09:00'
    source={'family_id':'JRA','race_id':rid,'source_freeze_at':'2026-10-31T13:15:00+09:00',
            'prediction_cutoff':cutoff}
    q={'race_id':rid,'prediction_cutoff':cutoff,'source_snapshot':source,'source_snapshot_sha256':'c'*64,
       'static_computed_at':'2026-10-31T13:15:30+09:00',
       'current_authority_manifest':'KM-FAMILY-CURRENT-AUTHORITY-20261012-R51',
       'runners':[{'runner_id':str(no),'evidence_features':{
           key:{'category':'POSITIVE','evidence_refs':['fixture']}
           for key in ('course_geometry_fit','recent_form')}} for no in (1,2,3)],
       'pair_dispositions':[{'head':3,'second':2,'status':'PURCHASE'}]}
    f={'race_id':rid,'prediction_cutoff':cutoff,'source_snapshot_sha256':'c'*64,
       'final_freeze_timestamp':'2026-10-31T13:16:00+09:00','krs_run_receipt':{'receipt_sha256':'d'*64},
       'static_prediction':{'ranking':[3,2,1],'roles':{'1':['P2'],'2':['P3'],'3':['W']}},
       'final_ticket':{'tickets':[{'bet_type':'EXACTA','selection':[3,2],'stake':100}]},
       'krs_prediction_utility':{'race_id':rid,
         'role_proposals':[{'horse_no':1,'proposal':'ADD_W_SHADOW'}],
         'ordered_pair_proposals':[{'head':1,'second':2}],
         'pair_third_proposals':[{'head':1,'second':2,'third':3}]}}
    f['sha256']=digest(f)
    def shadow(states):return build_shadow(q,f,states=states,observed_at='2026-10-31T13:20:00+09:00')
    before=deepcopy(state);accepted=shadow([state])
    assert accepted['learning_intake']['accepted'][0]['reference_metrics']['pfs'] is None
    assert accepted['learning_applied_to_arm'] is None and accepted['production_effect']=='NONE'
    assert accepted['arms']['LEARNING_ON']==shadow([])['arms']['LEARNING_ON']
    assert accepted['arms']['LEARNING_ON']['added_ticket_count']==0 and state==before
    # Positive control: this exact synthetic proposal is capable of changing
    # Shadow when a genuine role-failure context is deliberately supplied.
    role_failure=deepcopy(state);role_failure['reference_metrics']['first_material_failure']='PREDICTION_ROLE_W'
    role_failure['sha256']=digest({k:v for k,v in role_failure.items() if k!='sha256'})
    assert shadow([role_failure])['arms']['LEARNING_ON']['added_ticket_count']>0


@pytest.mark.parametrize('fault',['oidc','official_hash','verified_bytes_changed'])
def test_existing_worker_requires_real_verification_before_persisting_projection(tmp_path,monkeypatch,fault):
    import subprocess
    terminal,result=build_input();eid=RACE+'-LIVE-R1'
    for folder,obj in [('runtime/jra_no_bet_terminals',terminal),('runtime_out/capture',{
        'race_id':RACE,'execution_id':eid,'race_no':5,
        'original_prediction_cutoff':'2026-10-10T12:18:00+09:00',
        'result_capture_timestamp':'2026-10-10T13:00:00+09:00',
        'source_snapshot':{'snapshot_sha256':'a'*64},'official_result_detail':result})]:
        p=tmp_path/folder/(eid+'.json');p.parent.mkdir(parents=True,exist_ok=True)
        if fault=='official_hash' and folder=='runtime_out/capture':obj['official_result_detail']['sha256']='b'*64
        p.write_text(json.dumps(obj))
    def verify(*args,**kwargs):
        if fault=='oidc':raise subprocess.CalledProcessError(1,args[0])
        if fault=='verified_bytes_changed' and Path(args[0][3]).parent.name=='jra_no_bet_terminals':
            changed=tmp_path/'runtime_out/capture'/(eid+'.json')
            value=json.loads(changed.read_text());value['result_capture_timestamp']='2026-10-10T13:00:02+09:00'
            changed.write_text(json.dumps(value))
        return verified_oidc_fixture(args[0])[0]
    monkeypatch.setattr(subprocess,'run',verify)
    monkeypatch.chdir(tmp_path);monkeypatch.setenv('GITHUB_REPOSITORY','fixture/offline')
    monkeypatch.setenv('GITHUB_OUTPUT',str(tmp_path/'output'));monkeypatch.setenv('RACE_ID_FILTER',RACE)
    monkeypatch.setenv('GITHUB_SHA','1'*40)
    text=(ROOT/'.github/workflows/km-jra-no-bet-postresult-learning.yml').read_text()
    bodies=list(re.finditer(r"(?m)^          python - <<'PY'\n(.*?)(?m:^          PY)$",text,re.S))
    exec(compile('\n'.join(line[10:] for line in bodies[1][1].splitlines()),'<offline-existing-worker>','exec'),{})
    assert (tmp_path/'output').read_text()=='learned=false\n'
    for folder in ('jra_no_bet_learning','reviews_auto','learning_states','final_artifacts'):
        assert not (tmp_path/'runtime'/folder).exists()


@pytest.mark.parametrize('fault',['workflow','ref','self_hosted','unknown_code','subject_hash','missing_witness'])
def test_cli_origin_metadata_must_match_existing_main_hosted_workflows(tmp_path,monkeypatch,fault):
    import subprocess
    path=tmp_path/'terminal.json';path.write_text('{}')
    def verify(command,**kwargs):
        assert command[command.index('--repo')+1]=='b03la013-max/keibametrics-runtime'
        assert command[command.index('--signer-workflow')+1].endswith('/km-jra-formal-single-entry.yml')
        assert command[command.index('--source-ref')+1]=='refs/heads/main'
        assert '--deny-self-hosted-runners' in command
        _,value=verified_oidc_fixture(command);result=value['verificationResult'];cert=result['signature']['certificate']
        if fault=='workflow':cert['subjectAlternativeName']=cert['subjectAlternativeName'].replace('formal-single-entry','source-first-runner')
        if fault=='ref':cert['sourceRepositoryRef']='refs/heads/untrusted'
        if fault=='self_hosted':cert['runnerEnvironment']='self-hosted'
        if fault=='unknown_code':cert.pop('sourceRepositoryDigest')
        if fault=='subject_hash':result['statement']['subject'][0]['digest']['sha256']='f'*64
        if fault=='missing_witness':result['verifiedTimestamps']=[]
        return SimpleNamespace(stdout=json.dumps([value]))
    monkeypatch.setattr(subprocess,'run',verify)
    with pytest.raises(JRANoBetLearningError,match='ORIGIN_OR_WITNESS_UNKNOWN'):
        verify_no_bet_oidc(path,kind='terminal',not_before='2026-10-10T12:10:00+09:00',not_after='2026-10-10T12:18:00+09:00')


def test_capture_and_past_terminal_keep_their_distinct_verified_code_origins(tmp_path,monkeypatch):
    import subprocess
    commands=[];path=tmp_path/'artifact.json';path.write_text('{}')
    def verify(command,**kwargs):commands.append(command);return verified_oidc_fixture(command)[0]
    monkeypatch.setattr(subprocess,'run',verify)
    capture=verify_no_bet_oidc(path,kind='capture',source_digest='1'*40,
        not_before='2026-10-10T13:00:00+09:00',not_after='2026-10-10T13:02:00+09:00')
    terminal=verify_no_bet_oidc(path,kind='terminal',
        not_before='2026-10-10T12:10:00+09:00',not_after='2026-10-10T12:18:00+09:00')
    assert capture['source_digest']=='1'*40 and terminal['source_digest']=='2'*40
    assert commands[0][commands[0].index('--source-digest')+1]=='1'*40
    assert capture['workflow']=='km-jra-no-bet-postresult-learning.yml'
    assert terminal['workflow']=='km-jra-formal-single-entry.yml'
    with pytest.raises(JRANoBetLearningError,match='ORIGIN_REQUIRED'):
        verify_no_bet_oidc(path,kind='capture',not_before=EFFECTIVE,not_after=EFFECTIVE)


@pytest.mark.parametrize('fault',['canonical_write','output_write','invalid_result'])
def test_partial_canonical_write_never_gets_published_with_another_success(tmp_path,monkeypatch,fault):
    import subprocess,jra_shadow_checkpoint
    terminal,result=build_input();second=RACE.replace('R05','R06')
    for rid,rn in ((RACE,5),(second,6)):
        t=deepcopy(terminal);t['race_id']=rid;t['source_execution_id']=rid+'-LIVE-R1'
        t['sha256']=_hash({k:v for k,v in t.items() if k!='sha256'})
        official=deepcopy(result);official['race_no']=rn
        if fault=='invalid_result' and rid==RACE:official['sha256']='f'*64
        captured={'race_id':rid,'execution_id':rid+'-LIVE-R1','race_no':rn,
            'original_prediction_cutoff':'2026-10-10T12:18:00+09:00',
            'result_capture_timestamp':'2026-10-10T13:00:00+09:00',
            'source_snapshot':{'snapshot_sha256':'a'*64},'official_result_detail':official}
        for folder,value in (('runtime/jra_no_bet_terminals',t),('runtime_out/capture',captured)):
            p=tmp_path/folder/(rid+'-LIVE-R1.json');p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text(json.dumps(value))
    writes=[];original=jra_shadow_checkpoint.write_once
    def writer(path,value):
        writes.append(str(path))
        if fault=='canonical_write' and path.name==RACE+'-AUTO.json':
            raise OSError('OFFLINE_INJECTED_IO_FAILURE_AFTER_FIRST_CANONICAL_WRITE')
        return original(path,value)
    monkeypatch.setattr(jra_shadow_checkpoint,'write_once',writer)
    write_text=Path.write_text
    def output_writer(path,*args,**kwargs):
        if fault=='output_write' and str(path)==f'runtime_out/reviews/{RACE}-LIVE-R1.json':
            raise OSError('OFFLINE_INJECTED_ATTESTATION_SUBJECT_WRITE_FAILURE')
        return write_text(path,*args,**kwargs)
    monkeypatch.setattr(Path,'write_text',output_writer)
    monkeypatch.setattr(subprocess,'run',lambda command,**kwargs:verified_oidc_fixture(command)[0])
    monkeypatch.chdir(tmp_path);monkeypatch.setenv('GITHUB_REPOSITORY','fixture/offline')
    monkeypatch.setenv('GITHUB_OUTPUT',str(tmp_path/'output'));monkeypatch.setenv('GITHUB_SHA','1'*40)
    monkeypatch.setenv('RACE_ID_FILTER','')
    text=(ROOT/'.github/workflows/km-jra-no-bet-postresult-learning.yml').read_text()
    body=list(re.finditer(r"(?m)^          python - <<'PY'\n(.*?)(?m:^          PY)$",text,re.S))[1][1]
    code=compile('\n'.join(line[10:] for line in body.splitlines()),'<offline-two-race-worker>','exec')
    if fault in ('canonical_write','output_write'):
        with pytest.raises(RuntimeError,match='(CANONICAL_WRITE_FAILED|OUTPUT_WRITE_FAILED)'):exec(code,{})
        assert (tmp_path/f'runtime/jra_no_bet_learning/{RACE}-LIVE-R1.json').exists()
        assert not (tmp_path/'output').exists() # no learned=true / no persist step
        assert not any(second in p for p in writes)
        assert (tmp_path/f'runtime/learning_states/{RACE}.json').exists()==(fault=='output_write')
    else:
        exec(code,{})
        assert (tmp_path/'output').read_text().startswith('learned=true\n')
        assert (tmp_path/f'runtime/learning_states/{second}.json').exists()
        assert not any(RACE in p for p in writes) # validation failure remains Race-local


@pytest.mark.parametrize('fault',['valid','unverified_learning','tampered_hash','expired'])
def test_existing_attested_learning_backfills_only_views_without_recapture_or_original_rewrite(tmp_path,monkeypatch,fault):
    import subprocess,shutil
    from datetime import datetime,timezone
    import jra_same_day_results
    terminal,result=build_input();learning=run(terminal,result);eid=RACE+'-LIVE-R1'
    if fault=='tampered_hash':learning['sha256']='f'*64
    original=json.dumps(learning,ensure_ascii=False,indent=4)+'\n\n'
    files={f'runtime/jra_no_bet_terminals/{eid}.json':terminal,
           f'runtime/jra_formal_intents/{eid}.json':{'race_id':RACE,
               'prediction_cutoff':'2026-10-10T12:18:00+09:00','scheduled_post_at':'2026-10-10T12:25:00+09:00'}}
    for path,value in files.items():
        p=tmp_path/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value))
    learning_path=tmp_path/f'runtime/jra_no_bet_learning/{eid}.json'
    learning_path.parent.mkdir(parents=True);learning_path.write_text(original)
    before=learning_path.read_bytes();calls=[]
    def no_recapture(*args,**kwargs):raise AssertionError('EXISTING_LEARNING_MUST_NOT_RECAPTURE_OFFICIAL_SOURCE')
    monkeypatch.setattr(jra_same_day_results,'_open_day',no_recapture)
    monkeypatch.setattr(jra_same_day_results,'_fetch_race',no_recapture)
    class Clock(datetime):
        @classmethod
        def now(cls,tz=None):return cls(2026,10,20 if fault=='expired' else 10,4,30,tzinfo=timezone.utc)
    monkeypatch.setattr(__import__('datetime'),'datetime',Clock)
    def verify(command,**kwargs):
        calls.append(command)
        if fault=='unverified_learning' and Path(command[3]).parent.name=='jra_no_bet_learning':
            raise subprocess.CalledProcessError(1,command)
        return verified_oidc_fixture(command)[0]
    monkeypatch.setattr(subprocess,'run',verify)
    monkeypatch.chdir(tmp_path);monkeypatch.setenv('GITHUB_REPOSITORY','b03la013-max/keibametrics-runtime')
    monkeypatch.setenv('GITHUB_SHA','1'*40);monkeypatch.setenv('GITHUB_OUTPUT',str(tmp_path/'output'))
    monkeypatch.setenv('RACE_ID_FILTER',RACE)
    text=(ROOT/'.github/workflows/km-jra-no-bet-postresult-learning.yml').read_text()
    bodies=list(re.finditer(r"(?m)^          python - <<'PY'\n(.*?)(?m:^          PY)$",text,re.S))
    def execute(i):exec(compile('\n'.join(line[10:] for line in bodies[i][1].splitlines()),'<offline-existing-record-worker>','exec'),{})
    execute(0);execute(1)
    assert learning_path.read_bytes()==before
    assert not (tmp_path/'runtime_out/capture').exists() and not (tmp_path/'runtime_out/learning').exists()
    assert not (tmp_path/'runtime/final_artifacts').exists()
    if fault=='valid':
        state=json.loads((tmp_path/f'runtime/learning_states/{RACE}.json').read_text())
        review=json.loads((tmp_path/f'runtime/reviews_auto/{RACE}-AUTO.json').read_text())
        assert state['source_no_bet_result_sha256']==learning['sha256']
        assert state['effective_time']=='2026-10-10T04:30:00+00:00'
        assert state['effective_time']!=learning['post_race_official_acquired_at']
        assert review['source_evidence']['official_oidc_proofs']['learning']['source_digest']=='3'*40
        assert review['capital']['pfs'] is None and review['capital']['investment']==0
        assert not review['signed_final_verified'] and state['production_change_authorized'] is False
        output=(tmp_path/'output').read_text();assert 'learned=true\n' in output
        subjects=output.split('subjects<<KM_NO_BET_SUBJECTS\n')[1].split('\nKM_NO_BET_SUBJECTS')[0].splitlines()
        assert subjects==[f'runtime_out/reviews/{eid}.json',f'runtime_out/states/{eid}.json']
        assert len(calls)==2 and all('runtime_out/capture' not in c[3] for c in calls)
        # A later normal worker sees complete views and does no repeated work.
        shutil.rmtree(tmp_path/'runtime_out');(tmp_path/'output').write_text('');calls.clear()
        execute(0);execute(1)
        assert calls==[] and 'learned=false' in (tmp_path/'output').read_text()
    else:
        assert not (tmp_path/'runtime/reviews_auto').exists()
        assert not (tmp_path/'runtime/learning_states').exists()
        assert 'learned=false' in (tmp_path/'output').read_text()
        if fault=='expired':assert calls==[]
