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
    store.persist(cwd=a,branch='main',attempts=2,refresh=refresh)
    assert view in refreshed[0]
    assert json.loads(git(remote,'show','main:'+view))=={'race_ids':['A','B']}


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
    assert 'python tools/persist_local_checkpoints.py --branch main' in text
    assert 'if: always()' in text and 'path: runtime_out/result_checkpoint/' in text
