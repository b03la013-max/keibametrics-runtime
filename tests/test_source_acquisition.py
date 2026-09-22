import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"/"local_physical"))

from source_acquisition import (
    SOURCE_PROFILE,
    _merge_evidence,
    sha_obj,
    snapshot_from_bytes,
    validate_public_url,
    verify_source_artifact,
)


def _artifact(snapshot, normalized):
    art={
        "schema":"KM-SOURCE-SNAPSHOT-v1",
        "profile":SOURCE_PROFILE,
        "race_id":"LOCAL-TEST-R1",
        "prediction_cutoff":"2026-09-23T03:00:00+09:00",
        "source_freeze_at":"2026-09-23T02:01:00+09:00",
        "required_source_manifest":[],
        "required_source_manifest_sha256":sha_obj([]),
        "sources":[snapshot],
        "raw_source_bundle_sha256":"TEST",
        "normalized_evidence":normalized,
        "normalized_evidence_sha256":sha_obj(normalized),
        "conflicts":[],
        "missing_required_sources":[],
        "stale_sources":[],
        "post_cutoff_sources":[],
        "formal_ready":True,
        "errors":[],
    }
    art["source_snapshot_sha256"]=sha_obj({k:v for k,v in art.items() if k!="source_snapshot_sha256"})
    return art


def test_snapshot_hash_and_required_extraction_roundtrip():
    raw=b"<html><head><title>NAR Test Race</title></head><body>weight 486</body></html>"
    spec={
        "source_id":"nar-race-card",
        "url":"https://www.keiba.go.jp/",
        "source_class":"OFFICIAL_RACE_CARD",
        "authority":"NAR",
        "priority":100,
        "official":True,
        "required":True,
        "extract":[
            {"field":"page_title","type":"regex","pattern":r"<title>\s*(.*?)\s*</title>","group":1,"cast":"str","required":True},
            {"field":"horse_weight","type":"regex","pattern":r"weight\s+(\d+)","group":1,"cast":"int","required":True},
        ],
    }
    snap,errs=snapshot_from_bytes(
        spec,raw,final_url=spec["url"],status_code=200,
        headers={"content-type":"text/html; charset=utf-8"},
        fetched_at="2026-09-23T02:00:00+09:00",
        prediction_cutoff="2026-09-23T03:00:00+09:00",
    )
    assert errs==[]
    assert snap["cutoff_relation"]=="PRE_CUTOFF"
    assert snap["extracted_evidence"]["page_title"]=="NAR Test Race"
    assert snap["extracted_evidence"]["horse_weight"]==486

    normalized,conflicts,merge_errors=_merge_evidence([snap])
    assert conflicts==[]
    assert merge_errors==[]
    art=_artifact(snap,normalized)
    valid,verify_errors=verify_source_artifact(art)
    assert valid is True
    assert verify_errors==[]


def test_post_cutoff_required_source_is_fail_closed():
    spec={
        "source_id":"odds",
        "url":"https://www.keiba.go.jp/",
        "source_class":"ODDS",
        "authority":"NAR",
        "official":True,
        "required":True,
    }
    snap,errs=snapshot_from_bytes(
        spec,b"ok",final_url=spec["url"],status_code=200,
        headers={"content-type":"text/plain"},
        fetched_at="2026-09-23T03:01:00+09:00",
        prediction_cutoff="2026-09-23T03:00:00+09:00",
    )
    assert snap["cutoff_relation"]=="POST_CUTOFF"
    assert any(x.startswith("SOURCE_POST_CUTOFF") for x in errs)


def test_equal_priority_conflict_is_unresolved():
    a={
        "source_id":"a","http_status":200,"authority_priority":100,"authority":"OFFICIAL-A",
        "snapshot_sha256":"sha-a","fetched_at":"2026-09-23T02:00:00+09:00","cutoff_relation":"PRE_CUTOFF",
        "extracted_evidence":{"track_condition":"good"},
    }
    b={
        "source_id":"b","http_status":200,"authority_priority":100,"authority":"OFFICIAL-B",
        "snapshot_sha256":"sha-b","fetched_at":"2026-09-23T02:00:00+09:00","cutoff_relation":"PRE_CUTOFF",
        "extracted_evidence":{"track_condition":"sloppy"},
    }
    normalized,conflicts,errors=_merge_evidence([a,b])
    assert "track_condition" not in normalized
    assert conflicts[0]["status"]=="UNRESOLVED_EQUAL_PRIORITY"
    assert errors==["SOURCE_CONFLICT_UNRESOLVED:track_condition"]


def test_non_https_and_unapproved_hosts_are_rejected_before_fetch():
    try:
        validate_public_url("http://www.keiba.go.jp/")
        raise AssertionError("http must be rejected")
    except ValueError as e:
        assert "SOURCE_HTTPS_REQUIRED" in str(e)

    try:
        validate_public_url("https://127.0.0.1/")
        raise AssertionError("loopback host must be rejected")
    except ValueError as e:
        assert "SOURCE_HOST_NOT_ALLOWED" in str(e)


def test_optional_http_failure_is_recorded_but_not_formal_blocking():
    spec={
        "source_id":"optional-result",
        "url":"https://www.keiba.go.jp/",
        "source_class":"OFFICIAL_SAME_DAY_RACE_RESULT_PASSING_ORDER",
        "authority":"NAR",
        "official":True,
        "required":False,
    }
    snap,errs=snapshot_from_bytes(
        spec,b"not found",final_url=spec["url"],status_code=404,
        headers={"content-type":"text/plain"},
        fetched_at="2026-09-23T02:00:00+09:00",
        prediction_cutoff="2026-09-23T03:00:00+09:00",
    )
    assert snap["http_status"]==404
    assert errs==[]
