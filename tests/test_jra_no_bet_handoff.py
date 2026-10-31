"""The existing Autopilot must hand zero-stake decisions to its existing worker."""
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys
import subprocess

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime/jra_source_runtime'))
import jra_race_day_autopilot as autopilot

DATE='2026-10-31'
EID='KM-JRA-TKY-20261031-R05-LIVE-R1'
NOW=datetime.fromisoformat('2026-10-31T12:20:00+09:00')

def setup(root, *, final=False):
    for name in ('jra_race_day_plan','jra_no_bet_terminals','jra_formal_intents','final_artifacts'):
        (root/'runtime'/name).mkdir(parents=True,exist_ok=True)
    terminal={'decision':'NO_BET','total_investment':0,'scheduled_post_at':'2026-10-31T12:10:00+09:00'}
    (root/'runtime/jra_no_bet_terminals'/f'{EID}.json').write_text(json.dumps(terminal))
    (root/'runtime/jra_formal_intents'/f'{EID}.json').write_text('{}')
    if final:
        (root/'runtime/final_artifacts/KM-JRA-TKY-20261031-R04.json').write_text(json.dumps({'scheduled_post_at':'2026-10-31T11:40:00+09:00'}))

def state(root):
    return json.loads((root/'runtime/jra_race_day_plan'/f'{DATE}.state.json').read_text())

def test_no_final_still_hands_off_to_existing_zero_stake_workflow(tmp_path, monkeypatch):
    setup(tmp_path);calls=[]
    monkeypatch.setattr(autopilot.subprocess,'run',lambda args,**kwargs:calls.append(args))
    out=autopilot.request_postresult_worker(tmp_path,DATE,NOW,publish=lambda:None)
    assert out=='ACKNOWLEDGED'
    assert calls==[['gh','workflow','run','km-jra-no-bet-postresult-learning.yml','--ref','main']]
    assert state(tmp_path)['_no_bet_postresult_worker']['state']=='ACKNOWLEDGED'

def test_final_worker_recent_claim_does_not_suppress_zero_stake_handoff(tmp_path, monkeypatch):
    setup(tmp_path,final=True);calls=[]
    path=tmp_path/'runtime/jra_race_day_plan'/f'{DATE}.state.json'
    path.write_text(json.dumps({'_postresult_worker':{'requested_at':NOW.isoformat(),'state':'ACKNOWLEDGED'}}))
    monkeypatch.setattr(autopilot.subprocess,'run',lambda args,**kwargs:calls.append(args))
    autopilot.request_postresult_worker(tmp_path,DATE,NOW,publish=lambda:None)
    assert calls==[['gh','workflow','run','km-jra-no-bet-postresult-learning.yml','--ref','main']]

def test_unknown_send_is_throttled_without_retrying_final_or_duplicating(tmp_path,monkeypatch):
    setup(tmp_path);calls=[]
    def failure(args,**kwargs):
        calls.append(args);raise subprocess.TimeoutExpired(args,30)
    monkeypatch.setattr(autopilot.subprocess,'run',failure)
    assert autopilot.request_postresult_worker(tmp_path,DATE,NOW,publish=lambda:None)=='UNKNOWN_NO_IMMEDIATE_RETRY'
    assert autopilot.request_postresult_worker(tmp_path,DATE,NOW+timedelta(minutes=1),publish=lambda:None)=='RECENT_RESULT_WORKER_REQUEST'
    assert len(calls)==1

def test_completed_zero_stake_record_and_pre_result_window_are_not_dispatched(tmp_path,monkeypatch):
    setup(tmp_path);calls=[]
    monkeypatch.setattr(autopilot.subprocess,'run',lambda *args,**kwargs:calls.append(args))
    assert autopilot.request_postresult_worker(tmp_path,DATE,NOW-timedelta(seconds=1),publish=lambda:None)=='NO_DUE_FINAL'
    folder=tmp_path/'runtime/jra_no_bet_learning';folder.mkdir()
    (folder/f'{EID}.json').write_text('{}')
    assert autopilot.request_postresult_worker(tmp_path,DATE,NOW,publish=lambda:None)=='NO_DUE_FINAL'
    assert calls==[]

def test_dispatch_claim_is_published_before_send(tmp_path,monkeypatch):
    setup(tmp_path);events=[]
    def publish():
        assert state(tmp_path)['_no_bet_postresult_worker']['state']=='CLAIMED_NOT_ACKNOWLEDGED'
        events.append('published')
    monkeypatch.setattr(autopilot.subprocess,'run',lambda *args,**kwargs:events.append('sent'))
    autopilot.request_postresult_worker(tmp_path,DATE,NOW,publish=publish)
    assert events==['published','sent']

def test_no_bet_claim_merge_never_overwrites_newer_dispatch(tmp_path):
    new={'requested_at':NOW.isoformat(),'state':'ACKNOWLEDGED'}
    old={'requested_at':(NOW-timedelta(minutes=30)).isoformat(),'state':'CLAIMED_NOT_ACKNOWLEDGED'}
    assert autopilot.merge_dispatch_state({'_no_bet_postresult_worker':new},{'_no_bet_postresult_worker':old})['_no_bet_postresult_worker']==new


def test_corrupt_zero_stake_record_does_not_block_independent_final_worker(tmp_path,monkeypatch):
    setup(tmp_path,final=True);calls=[]
    (tmp_path/'runtime/jra_no_bet_terminals'/f'{EID}.json').write_text('[]')
    monkeypatch.setattr(autopilot.subprocess,'run',lambda args,**kwargs:calls.append(args))
    assert autopilot.request_postresult_worker(tmp_path,DATE,NOW,publish=lambda:None)=='ACKNOWLEDGED'
    assert calls==[['gh','workflow','run','km-jra-production-postresult.yml','--ref','main']]
