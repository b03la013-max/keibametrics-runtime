"""FNB R10 gateway observation: never POST, deploy, sign or dispatch."""
from pathlib import Path
import json

from runtime.local_fnb_r10_gateway_readonly_health import inspect

ROOT=Path(__file__).resolve().parents[1]


def test_r10_gateway_readonly_success_or_explicit_compatibility_mismatch():
    health=json.loads((ROOT/"evidence/family_audit_20261016/runtime_health.json").read_text())
    calls=[]
    def get(url,**kwargs):
        calls.append((url,kwargs))
        return 200,health
    observed=inspect(getter=get)
    assert len(calls)==1
    assert calls[0][0].endswith("/health")
    assert calls[0][1]=={"method":"GET","timeout":8,"attempts":1}
    assert observed["status"] in ("HEALTH_COMPATIBILITY_PASS",
                                  "HEALTH_COMPATIBILITY_FAIL")
    assert observed["new_runtime_post_count"]==0
    assert observed["new_deployment"] is False
    assert observed["formal_fnb_scope_authorized"] is False
    assert observed["user_delivery_ack"] is False


def test_r10_gateway_http_failure_and_network_exception_are_not_pass():
    for probe in (
        lambda u,**kw:(503,{"error":"unavailable"}),
        lambda u,**kw:(_ for _ in ()).throw(TimeoutError("redacted")),
    ):
        r=inspect(getter=probe)
        assert r["runtime_compatibility_verified"] is False
        assert r["status"] in ("HEALTH_HTTP_NOT_OK","UNVERIFIED_UNREACHABLE")
        assert r["new_actor_created"] is False
