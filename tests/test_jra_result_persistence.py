"""Publication recovery only; opaque signed bytes never reissued or selected by side."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools import persist_local_checkpoints as store


def git(cwd, *args):
    return subprocess.run(['git', *args], cwd=cwd, check=True, text=True,
                          capture_output=True).stdout.strip()


def repository(tmp_path):
    remote=tmp_path/'remote.git';remote.mkdir()
    git(remote,'init','--bare','--initial-branch=main')
    a=tmp_path/'worker';b=tmp_path/'peer'
    git(tmp_path,'clone',str(remote),str(a))
    for path in (a,):
        git(path,'config','user.name','fixture');git(path,'config','user.email','fixture@example.invalid')
    (a/'baseline').write_text('unchanged')
    git(a,'add','.');git(a,'commit','-m','baseline');git(a,'push','origin','HEAD:main')
    git(tmp_path,'clone',str(remote),str(b))
    git(b,'config','user.name','fixture');git(b,'config','user.email','fixture@example.invalid')
    return remote,a,b


def commit(path, name, body):
    f=path/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(body)
    git(path,'add',name);git(path,'commit','-m','fixture '+name)


def test_real_push_race_retries_without_changing_receipt_or_other_race(tmp_path,monkeypatch):
    remote,a,b=repository(tmp_path)
    receipt='runtime/reviews_auto/RACE_A.json';opaque=b'{"signed_response":"opaque original bytes"}\n'
    commit(a,receipt,opaque)
    original=store.git;calls=[]
    def race(*args,cwd):
        calls.append(args)
        if args[0]=='push' and sum(x[0]=='push' for x in calls)==1:
            # Real non-fast-forward rejection after this worker has rebased.
            commit(b,'runtime/reviews_auto/RACE_B.json',b'other race\n')
            git(b,'push','origin','HEAD:main')
        return original(*args,cwd=cwd)
    monkeypatch.setattr(store,'git',race);monkeypatch.setattr(store.time,'sleep',lambda _:None)
    store.persist(cwd=a,branch='main',attempts=3,refresh=lambda _:None)
    assert sum(x[0]=='push' for x in calls)==2
    assert git(remote,'show','main:'+receipt)==opaque.decode().strip()
    assert git(remote,'show','main:runtime/reviews_auto/RACE_B.json')=='other race'
    assert not any('--force' in arg for args in calls for arg in args)


def test_conflicting_immutable_receipt_fails_closed_without_side_selection(tmp_path):
    remote,a,b=repository(tmp_path)
    name='runtime/reviews_auto/SAME_RACE.json'
    commit(a,name,b'worker original\n');commit(b,name,b'peer different\n')
    git(b,'push','origin','HEAD:main')
    with pytest.raises(RuntimeError,match='IMMUTABLE_OR_UNKNOWN_CONFLICT'):
        store.persist(cwd=a,branch='main',attempts=1,refresh=lambda _:pytest.fail('must not rebuild receipt'))
    assert git(remote,'show','main:'+name)=='peer different'
    assert (a/name).read_bytes()==b'worker original\n'


def test_jra_snapshot_conflict_rebuilds_merged_records(tmp_path,monkeypatch):
    remote,a,b=repository(tmp_path)
    view='runtime/krs_oos_status.json'
    commit(a,view,b'{"stale":"worker"}\n')
    commit(a,'runtime/krs_oos_measurements/A.json',b'{"race_id":"A"}\n')
    commit(b,view,b'{"stale":"peer"}\n')
    commit(b,'runtime/krs_oos_measurements/B.json',b'{"race_id":"B"}\n')
    git(b,'push','origin','HEAD:main')
    refreshed=[]
    def refresh(paths):
        refreshed.append(set(paths))
        # Both per-race records must exist before the disposable view is rebuilt.
        ids=sorted(json.loads(p.read_text())['race_id'] for p in (a/'runtime/krs_oos_measurements').glob('*.json'))
        assert ids==['A','B']
        (a/view).write_text(json.dumps({'race_ids':ids}))
    monkeypatch.setattr(store.time,'sleep',lambda _:None)
    store.persist(cwd=a,branch='main',attempts=2,refresh=refresh,
                  snapshots=store.SNAPSHOTS | store.JRA_RESULT_SNAPSHOTS)
    assert view in refreshed[0]
    assert json.loads(git(remote,'show','main:'+view))=={'race_ids':['A','B']}


def test_real_role_rescue_aggregate_conflict_rebuilds_both_races(tmp_path,monkeypatch):
    """The Oct 24 failed RESULT saver must merge records, not choose a view."""
    remote,a,b=repository(tmp_path)
    view='runtime/role_rescue_shadow_status.json'
    for root,rid,eligible in ((a,'A',True),(b,'B',False)):
        record={'race_id':rid,'sha256':rid*64,'policy_fingerprint':'unchanged-policy','oos_eligible':eligible}
        commit(root,view,json.dumps({'stale':rid}).encode())
        commit(root,f'runtime/role_rescue_shadow_results/{rid}.json',json.dumps(record).encode())
    git(b,'push','origin','HEAD:main')
    monkeypatch.chdir(a)
    monkeypatch.setattr(store.time,'sleep',lambda _:None)
    store.persist(cwd=a,branch='main',attempts=2,
                  snapshots=store.SNAPSHOTS | store.JRA_RESULT_SNAPSHOTS)
    result=json.loads(git(remote,'show','main:'+view))
    assert result['distinct_races']==2 and result['forward_oos_verified_races']==0
    assert result['legacy_recorded_eligible_races']==1  # Saved legacy claim is not a registered new cohort.
    assert [r['race_id'] for r in result['results']]==['A','B']
    assert result['automatic_promotion'] is False


def test_role_rescue_per_race_conflict_remains_immutable(tmp_path):
    remote,a,b=repository(tmp_path)
    name='runtime/role_rescue_shadow_results/SAME_RACE.json'
    commit(a,name,b'{"signed_lineage":"first"}\n')
    commit(b,name,b'{"signed_lineage":"different"}\n')
    git(b,'push','origin','HEAD:main')
    with pytest.raises(RuntimeError,match='IMMUTABLE_OR_UNKNOWN_CONFLICT'):
        store.persist(cwd=a,branch='main',attempts=1,refresh=lambda _:pytest.fail('immutable record'),
                      snapshots=store.SNAPSHOTS | store.JRA_RESULT_SNAPSHOTS)
    assert (a/name).read_bytes()==b'{"signed_lineage":"first"}\n'


def test_retry_exhaustion_keeps_local_commit_and_does_not_claim_success(tmp_path,monkeypatch):
    _,a,_=repository(tmp_path)
    commit(a,'runtime/reviews_auto/A.json',b'retained\n');head=git(a,'rev-parse','HEAD')
    original=store.git
    def reject(*args,cwd):
        if args[0]=='push':
            return subprocess.CompletedProcess(args,1,'','transient rejection')
        return original(*args,cwd=cwd)
    monkeypatch.setattr(store,'git',reject);monkeypatch.setattr(store.time,'sleep',lambda _:None)
    with pytest.raises(RuntimeError,match='PUSH_RETRY_EXHAUSTED'):
        store.persist(cwd=a,branch='main',attempts=2,refresh=lambda _:None)
    assert git(a,'rev-parse','HEAD')==head
    assert (a/'runtime/reviews_auto/A.json').read_bytes()==b'retained\n'


def test_verified_result_is_checkpointed_before_review_and_uploaded_on_failure():
    text=Path('.github/workflows/km-formal-result-runner.yml').read_text()
    assert text.index('assert vcode<300') < text.index('result_receipt_envelope.json') < text.index('review=build_post_result_review')
    assert 'python tools/persist_local_checkpoints.py --branch main --jra-result' in text
    assert 'if: always()' in text and 'path: runtime_out/result_checkpoint/' in text
    assert text.index('("learning_state.json",learning,existing_learning)') < text.index('oos=build_oos_measurement')
    assert 'checkpoint_inventory.json' in text


def _production_closed_loop_code():
    """Execute the actual workflow block after RESULT receipt verification, offline."""
    import textwrap
    text=(Path(__file__).resolve().parents[1]/'.github/workflows/km-formal-result-runner.yml').read_text()
    start=text.index('          candidate_only=str(')
    end=text.index('          # Source-derived Candidate closed loop.',start)
    return compile(textwrap.dedent(text[start:end]),'<actual-result-workflow>','exec')


@pytest.mark.parametrize('failure',['malformed_json','lineage','settlement','save','replace','none'])
def test_optional_mec_failure_preserves_real_production_review_and_learning(tmp_path,monkeypatch,failure):
    import builtins,copy,os
    root=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(root/'runtime'))
    from post_result_learning import build_post_result_review,build_learning_state
    from krs_oos_promotion_gate import build_oos_measurement
    from race_day_fast_reflection import build_fast_reflection
    from mec_r4_shadow import build_mec_r4_shadow,settle_mec_r4_shadow
    rid='KM-JRA-TKY-20261018-R11'
    final_raw=(root/'runtime/final_artifacts'/f'{rid}.json').read_bytes()
    result_raw=(root/'runtime/results'/f'{rid}.json').read_bytes()
    final=json.loads(final_raw);result=json.loads(result_raw)
    expected_review=build_post_result_review(result,final)
    stamp='2026-10-18T14:00:00+00:00'
    expected_learning=build_learning_state(expected_review,effective_time=stamp)
    final_path=tmp_path/'runtime/final_artifacts'/f'{rid}.json'
    final_path.parent.mkdir(parents=True);final_path.write_bytes(final_raw)
    shadow_path=tmp_path/'runtime/mec_shadow_artifacts'/f'{rid}.json'
    shadow_path.parent.mkdir(parents=True)
    shadow=build_mec_r4_shadow(final)
    if failure=='lineage':shadow['source_immutable_final_sha256']='wrong-final'
    shadow_raw=b'{' if failure=='malformed_json' else json.dumps(shadow).encode()
    shadow_path.write_bytes(shadow_raw)
    def settle(s,p):
        if failure=='settlement':raise ValueError('injected shadow settlement failure')
        return settle_mec_r4_shadow(s,p)
    saved=tmp_path/'runtime/mec_shadow_results'/f'{rid}.json'
    saved.parent.mkdir(parents=True);old_saved=b'{"previous_research_result":"unchanged"}\n';saved.write_bytes(old_saved)
    original_dump=json.dump;original_replace=os.replace
    def dumping(value,fh,*args,**kwargs):
        if failure=='save' and '.mec-' in str(getattr(fh,'name','')):
            fh.write('{"partial":');raise OSError('injected partial shadow write failure')
        return original_dump(value,fh,*args,**kwargs)
    def replacing(src,dst):
        if failure=='replace':raise OSError('injected atomic replace failure')
        return original_replace(src,dst)
    monkeypatch.chdir(tmp_path);monkeypatch.setattr(json,'dump',dumping);monkeypatch.setattr(os,'replace',replacing)
    env=dict(json=json,os=os,p=copy.deepcopy(result),settle_mec_r4_shadow=settle,
             build_post_result_review=build_post_result_review,
             build_learning_state=lambda r,**kw:build_learning_state(r,effective_time=stamp),
             build_oos_measurement=build_oos_measurement,build_fast_reflection=build_fast_reflection)
    exec(_production_closed_loop_code(),env)
    assert env['review']==expected_review and env['learning']==expected_learning
    checkpoint=tmp_path/'runtime_out/result_checkpoint'
    assert json.loads((checkpoint/'learning_state.json').read_text())==expected_learning
    assert json.loads((checkpoint/'post_result_review.json').read_text())==expected_review
    assert (checkpoint/'final_artifact.json').read_bytes()==final_raw
    assert env['p']==result and final_path.read_bytes()==final_raw
    assert shadow_path.read_bytes()==shadow_raw
    diagnostic=env['mec_shadow_diagnostic']
    assert diagnostic['status']==('SETTLED' if failure=='none' else 'HOLD')
    assert diagnostic['production_effect']=='NONE'
    if failure!='none':
        assert env['shadow_settlement'] is None and diagnostic['reason']
        assert saved.read_bytes()==old_saved
    else:assert env['shadow_settlement']==settle_mec_r4_shadow(shadow,result)
    assert not list(saved.parent.glob('.mec-*.tmp'))
    workflow=(root/'.github/workflows/km-formal-result-runner.yml').read_text()
    assert '"mec_r4_shadow_diagnostic":mec_shadow_diagnostic' in workflow


def test_mec_tracker_failure_is_isolated_from_production_pfs():
    import textwrap
    root=Path(__file__).resolve().parents[1]
    text=(root/'.github/workflows/km-formal-result-runner.yml').read_text()
    start=text.index('              try:\n                  mec_r4_oos=write_mec_r4_oos_status()')
    end=text.index('\n          else:',start)
    called=[]
    def fail():raise ValueError('invalid research result')
    env=dict(write_mec_r4_oos_status=fail,write_pfs_grand_review=lambda:called.append('PRODUCTION') or {'sha256':'stable'})
    exec(textwrap.dedent(text[start:end]),env)
    assert env['mec_r4_oos']['status']=='HOLD' and called==['PRODUCTION']
    assert env['pfs_grand']=={'sha256':'stable'}
