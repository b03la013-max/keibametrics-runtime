"""Independent verifications stay complete and merge in stable path order."""
import json
from pathlib import Path
import sys
import threading
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
import jra_pedigree_corpus as corpus


def test_parallel_verifies_every_input_with_bounded_concurrency(monkeypatch,tmp_path):
    directory=tmp_path/'runtime/pedigree_corpus';directory.mkdir(parents=True)
    for i in range(12):
        (directory/f'{i:02d}.json').write_text(json.dumps({'horses':[{'sire':'TARGET'}]}))
    seen=[];active=0;maximum=0;lock=threading.Lock()
    def verify(path,**kw):
        nonlocal active,maximum
        with lock:active+=1;maximum=max(maximum,active);seen.append(path.name)
        time.sleep(.01)
        with lock:active-=1
        return None  # Untrusted inputs remain rejected, never evidence.
    monkeypatch.setenv('GH_TOKEN','TEST-NOT-A-CREDENTIAL')
    monkeypatch.setattr(corpus,'_verified_harvest',verify)
    result=corpus.build_corpus(tmp_path,prediction_cutoff='2026-10-12T12:50:00+09:00',
        race_date='2026-10-12',exclude_race_id='TEST',required_sires={'TARGET'})
    assert len(seen)==12 and len(set(seen))==12 and 1<maximum<=4
    assert result['rejected_untrusted_inputs']==12 and result['horse_count']==0
