"""Mac collector tests run on Linux without a subscriber, browser or paid HTML."""
from __future__ import annotations
from datetime import datetime,timedelta,timezone
import hashlib
import json
from pathlib import Path
import pytest
from runtime.jra_keibabook_mac_collector import (
    BookCollectorError, capture_race, process_queue, _url, _race_id,
    make_launchd_plist, _assert_expected_url
)

RACE="202604000309"
DAY="2026-10-11"
OFFICIAL=[{"runner_id":str(i),"name":"馬"+str(i)} for i in (1,2)]

def html(kind):
    if kind=="ability":
        return "<table>" + "".join(
           f'<tr><td class="umaban">{i}</td><td class="bamei">'
           f'<p><a>父</a></p><p><a>馬{i}</a></p><p><span>母</span></p><p><span>母父</span></p></td>'
           f'<td class="zensou"><div class="inner"><p><a href="/cyuou/seiseki/202604000101">9･20</a></p>'
           '<p>1400芝</p><p>S72</p><p>記録</p></div></td></tr>' for i in (1,2))+"</table>"
    if kind=="workout":
        return "<table>"+"".join(
           f'<tr><td class="umaban">{i}</td><td class="kbamei">馬{i}</td>'
           '<td class="tanpyo">好調</td></tr><tr></tr>' for i in (1,2))+"</table>"
    return "<table>"+"".join(
           f'<tr><td class="umaban">{i}</td><td><a href="/db/uma/1234567">馬{i}</a></td></tr>'
           '<tr><td class="danwa">順調</td></tr>' for i in (1,2))+"</table>"

class Response:
    status=200

class Page:
    def __init__(self,ctx):
        self.ctx=ctx
        self.url=""
    def goto(self,url,**_):
        kind=next(k for k in ("ability","workout","stable") if _url(k,RACE)==url)
        self.url=self.ctx.override_url or url
        self.ctx.history.append(kind)
        self.kind=kind
        return Response()
    def wait_for_selector(self,*_,**__):
        return None
    def content(self):
        return self.ctx.contents.get(self.kind,html(self.kind))
    def close(self):
        pass

class Context:
    def __init__(self):
        self.history=[]
        self.override_url=None
        self.contents={}
    def new_page(self):
        return Page(self)


def future():
    return (datetime.now(timezone.utc)+timedelta(minutes=40)).isoformat()

def test_three_signedoff_pages_collected_locally_with_original_hashes(tmp_path):
    out=tmp_path/"secret"
    context=Context()
    result=capture_race(context,book_race_id=RACE,race_date=DAY,
                        prediction_cutoff=future(),official=OFFICIAL,output_dir=out)
    assert context.history==["ability","workout","stable"]
    assert result["runner_count"]==2
    assert result["capture_temporal_mode"]=="PRE_RACE_FACT_INTAKE"
    assert not result["production_authority"] and not result["signed_source"]
    assert result["oos_increment"]==0
    assert result["available_feature_counts"]["workout_capability"]==2
    assert result["available_feature_counts"]["stable_readiness"]==2
    folder=out/RACE
    manifest=json.loads((folder/"manifest.json").read_text())
    for row in manifest:
        assert hashlib.sha256((folder/row["file"]).read_bytes()).hexdigest()==row["sha256"]
        assert row["capture_method"]=="PLAYWRIGHT_AUTHENTICATED_RENDERED_DOM"
    assert (folder/"intake.json").exists()
    assert (folder/"diagnostic_evaluations.json").exists()
    assert folder.stat().st_mode & 0o077 == 0
    assert (folder/"ability.html").stat().st_mode & 0o077 == 0
    with pytest.raises(BookCollectorError,match="IMMUTABLE_ALREADY_EXISTS"):
        capture_race(Context(),book_race_id=RACE,race_date=DAY,
                     prediction_cutoff=future(),official=OFFICIAL,output_dir=out)


def test_login_redirect_or_bad_runner_aborts_without_leaking_partial_files(tmp_path):
    context=Context();context.override_url="https://s.keibabook.co.jp/login"
    with pytest.raises(BookCollectorError,match="AUTHENTICATION_OR_PAGE"):
        capture_race(context,book_race_id=RACE,race_date=DAY,
                     prediction_cutoff=future(),official=OFFICIAL,output_dir=tmp_path/"priv")
    assert not list((tmp_path/"priv").iterdir())
    context=Context()
    context.contents["stable"]=html("stable").replace("馬2","別馬")
    with pytest.raises(ValueError,match="UNIVERSE_MISMATCH"):
        capture_race(context,book_race_id=RACE,race_date=DAY,
                     prediction_cutoff=future(),official=OFFICIAL,output_dir=tmp_path/"priv")
    assert not list((tmp_path/"priv").iterdir())


def test_cutoff_is_real_barrier_and_replay_stays_replay(tmp_path):
    past=(datetime.now(timezone.utc)-timedelta(minutes=10)).isoformat()
    with pytest.raises(BookCollectorError,match="CUTOFF_EXPIRED"):
        capture_race(Context(),book_race_id=RACE,race_date=DAY,
                     prediction_cutoff=past,official=OFFICIAL,output_dir=tmp_path/"priv")
    result=capture_race(Context(),book_race_id=RACE,race_date=DAY,
                        prediction_cutoff=past,official=OFFICIAL,
                        output_dir=tmp_path/"priv",replay=True)
    assert result["capture_temporal_mode"]=="REPLAY"
    assert not result["signed_final_issued"]


def test_queue_skips_far_future_and_past_without_browser(monkeypatch,tmp_path):
    queue=tmp_path/"queue.json"
    official=tmp_path/"official.json"
    official.write_text(json.dumps(OFFICIAL))
    far=(datetime.now(timezone.utc)+timedelta(days=1)).isoformat()
    queue.write_text(json.dumps([{
        "book_race_id":RACE,"race_date":DAY,"prediction_cutoff":far,
        "official_runners_path":str(official)
    }]))
    result=process_queue(queue,private_dir=tmp_path/"priv")
    assert result["not_due"]==[RACE]
    assert not result["completed"]
    queue.write_text(json.dumps([{
        "book_race_id":RACE,"race_date":DAY,
        "prediction_cutoff":(datetime.now(timezone.utc)-timedelta(minutes=10)).isoformat(),
        "official_runners_path":str(official)
    }]))
    result=process_queue(queue,private_dir=tmp_path/"priv")
    assert result["past_cutoff"]==[RACE] and not result["completed"]


def test_url_allowlist_and_race_id_mapping_are_exact():
    assert _url("ability",RACE)=="https://s.keibabook.co.jp/cyuou/nouryoku_html_detail/202604000309.html"
    with pytest.raises(BookCollectorError,match="PAGE_MISMATCH"):
        _assert_expected_url("https://s.keibabook.co.jp/cyuou/cyokyo/0/1234",_url("workout",RACE))
    with pytest.raises(BookCollectorError,match="BOOK_RACE_ID_INVALID"):
        _race_id("202504000309",DAY)


def test_mac_scheduler_only_points_to_local_python_private_data(tmp_path):
    repo=Path(__file__).resolve().parents[1]
    plist=make_launchd_plist(repo_root=repo,queue_path=tmp_path/"queue.json",
                            profile=tmp_path/"profile",private_dir=tmp_path/"private")
    assert plist["StartInterval"]==300
    assert plist["ProgramArguments"][1].endswith("jra_keibabook_mac_collector.py")
    assert plist["WorkingDirectory"]==str(repo)
    assert "--queue" in plist["ProgramArguments"]
    with pytest.raises(BookCollectorError,match="INTERVAL_INVALID"):
        make_launchd_plist(repo_root=repo,queue_path=tmp_path/"queue.json",
                          profile=tmp_path/"profile",private_dir=tmp_path/"private",
                          interval_seconds=60)
