import hashlib,json,shutil
import pytest
from tools.local_aki_forward_checkpoint import pack,restore,ARCHIVE,MANIFEST,BASE

def seed(root):
    p=root/BASE/'external/KM-LOCAL-AKI-FORWARD-TEST/abc/forward_evaluation.json'
    p.parent.mkdir(parents=True);p.write_text('{"result":"saved"}\n')
    return p

def test_restart_byte_identical_and_repeat_pack(tmp_path):
    original=tmp_path/'a';p=seed(original);pack(original)
    before=(original/ARCHIVE).read_bytes();pack(original)
    assert before==(original/ARCHIVE).read_bytes()
    target=tmp_path/'b'
    for n in [ARCHIVE,MANIFEST]:
        (target/n).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original/n,target/n)
    assert restore(target)['files']==1
    assert restore(target)['network_calls']==0
    assert (target/p.relative_to(original)).read_bytes()==p.read_bytes()

def test_conflict_rejected_before_restore(tmp_path):
    p=seed(tmp_path);pack(tmp_path);p.write_text('changed')
    with pytest.raises(ValueError,match='IMMUTABLE_CONFLICT'):restore(tmp_path)

def test_tampered_archive_rejected(tmp_path):
    seed(tmp_path);pack(tmp_path);(tmp_path/ARCHIVE).write_bytes(b'wrong')
    with pytest.raises(ValueError,match='DIGEST_INVALID'):restore(tmp_path)

def test_no_checkpoint_is_normal_initial_state(tmp_path):
    assert restore(tmp_path)['status']=='NO_RESULT_CHECKPOINT_YET'
