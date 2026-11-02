"""R21: actual normal LOCAL chat CLI dispatch, synthetic receipts only.

No source, owner or official prediction generated in tests.
"""
import json
import sys
from pathlib import Path

from runtime import local_race_entry as entry
from runtime import local_fnb_r20_chat_completion as private

def _argv(monkeypatch, query, tmp_path, *, has_private_root=False, display=False):
    args=["local_race_entry","--query",query,
          "--output",str(tmp_path/"public-output"),
          "--run-id","R21-RESEARCH"]
    if has_private_root:
        args.extend(["--private-root",str(tmp_path/"private")])
    if display:
        args.append("--display")
    monkeypatch.setattr(sys,"argv",args)

def test_fnb6r_main_no_private_actor_is_explicit_hold(monkeypatch,tmp_path,capsys):
    _argv(monkeypatch,"船橋6Rのケイバメトリクス調査願います",tmp_path)
    code=entry.main()
    payload=json.loads(capsys.readouterr().out)
    assert code==2
    assert payload["status"]=="EXECUTION_HOLD_NOT_NO_BET"
    assert payload["reason"]=="FNB_PRIVATE_WORK_ROOT_NOT_CONNECTED"
    assert not (tmp_path/"public-output").exists()

def test_fnb_r20_is_called_from_normal_chat_entry(monkeypatch,tmp_path,capsys):
    _argv(monkeypatch,"2026年11月2日 船橋6R",tmp_path,has_private_root=True)
    called=[]
    def fake_complete(query, root, **kwargs):
        called.append((query,root,kwargs))
        return {"status":"EXECUTION_HOLD_NOT_NO_BET",
                "reason":"PRIVATE_WORK_BUNDLE_NOT_PREPARED"}
    monkeypatch.setattr(private,"complete",fake_complete)
    assert entry.main()==2
    output=json.loads(capsys.readouterr().out)
    assert output["reason"]=="PRIVATE_WORK_BUNDLE_NOT_PREPARED"
    assert len(called)==1
    assert called[0][0]=="2026年11月2日 船橋6R"
    assert called[0][1]==(tmp_path/"private")
    assert not (tmp_path/"public-output").exists()

def test_fnb_explicit_private_full_display(monkeypatch,tmp_path,capsys):
    _argv(monkeypatch,"船橋7R",tmp_path,has_private_root=True,display=True)
    def fake_complete(*a,**kw):
        return {"status":"VERIFIED_FROZEN_PRIVATE_BODY_READY_TO_RENDER",
                "body":"SYNTHETIC COMPLETE SIX METHODS\n",
                "recipient_delivery_ack":False}
    monkeypatch.setattr(private,"complete",fake_complete)
    assert entry.main()==0
    assert capsys.readouterr().out=="SYNTHETIC COMPLETE SIX METHODS\n"
    assert not (tmp_path/"public-output").exists()

def test_fnb_mixed_venue_fails_closed_without_urw(monkeypatch,tmp_path,capsys):
    _argv(monkeypatch,"船橋6R 浦和6R",tmp_path,has_private_root=True)
    assert entry.main()==2
    payload=json.loads(capsys.readouterr().out)
    assert payload["status"]=="EXECUTION_HOLD_NOT_NO_BET"
    assert payload["reason"]=="FNB_CHAT_EXACTLY_ONE_RACE_REQUIRED"

def test_urw_chat_intent_remains_urw():
    from datetime import datetime,timezone
    intent=entry.resolve_chat_intent(
      "2026-11-02 浦和6Rのケイバメトリクス調査",
      now=datetime(2026,11,2,tzinfo=timezone.utc))
    assert intent["venue_id"]=="URW"
    assert intent["race_no"]==6
