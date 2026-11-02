"""FNB R10 read-only observation of the EXISTING canonical LOCAL Gateway.

One bounded GET /health. Does not send SOURCE/FINAL/RESULT, create an actor,
activate a signer, create a deployment, buy a ticket or incur a new service.
No provider URL is accepted from the caller. The local current Gateway config
owns the endpoint. A reachable server that fails bundle/trust compatibility
is an explicit FAIL, not a production ready actor.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from urllib.parse import urlparse

PROFILE="KM-FNB-R10-LOCAL-GATEWAY-READONLY-HEALTH-v1"


def inspect(*, getter=None, now=None):
    from runtime.execution_gateway import (
        family_config, load_gateway, assess_runtime_health, request_json,
    )
    observed=now or datetime.now(timezone.utc)
    if observed.tzinfo is None:
        raise ValueError("HEALTH_OBSERVATION_TIMEZONE_REQUIRED")
    gateway=load_gateway()
    cfg=family_config("LOCAL",gateway)
    endpoint=cfg["external_endpoint"].rstrip("/")
    parsed=urlparse(endpoint)
    if parsed.scheme!="https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("CANONICAL_LOCAL_HEALTH_ENDPOINT_INVALID")
    result={
        "profile":PROFILE,
        "observed_at":observed.isoformat(),
        "canonical_endpoint_origin":endpoint,
        "source_of_endpoint":"profiles/current_execution_gateway.json/families/LOCAL",
        "method":"GET","path":"/health","timeout_seconds":8,
        "attempts":1,"status":"UNVERIFIED_UNREACHABLE",
        "runtime_compatibility_verified":False,
        "observed_http_status":None,"observed_health_sha256":None,
        "expected_signer_key_id":cfg["receipt_signer_key_id"],
        "new_actor_created":False,"new_runtime_post_count":0,
        "new_deployment":False,"new_purchase":False,
        "formal_fnb_scope_authorized":False,
        "user_delivery_ack":False,
    }
    invoke=getter or request_json
    try:
        code,health=invoke(endpoint+"/health",method="GET",timeout=8,attempts=1)
        if type(code) is not int or not isinstance(health,dict):
            raise ValueError("HEALTH_RESPONSE_INVALID")
        result["observed_http_status"]=code
        result["observed_health_sha256"]=hashlib.sha256(
            json.dumps(health,sort_keys=True,ensure_ascii=False,
                       separators=(",",":"),allow_nan=False).encode()).hexdigest()
        if code!=200:
            result.update(status="HEALTH_HTTP_NOT_OK",reason="HTTP_"+str(code))
            return result
        assessed=assess_runtime_health(health,"LOCAL",gateway)
        result.update(status="HEALTH_COMPATIBILITY_PASS" if assessed["status"]=="PASS"
                      else "HEALTH_COMPATIBILITY_FAIL",
                      runtime_compatibility_verified=assessed["status"]=="PASS",
                      assessment_status=assessed["status"],
                      health_errors=assessed.get("errors",[]),
                      health_warnings=assessed.get("warnings",[]),
                      runtime_git_revision_observed=health.get("github_revision"),
                      signer_key_id_observed=health.get("receipt_signer_key_id"),
                      public_key_fingerprint_sha256=hashlib.sha256(
                          __import__("base64").b64decode(health["receipt_public_key_b64"],
                                                        validate=True)).hexdigest()
                          if isinstance(health.get("receipt_public_key_b64"),str)
                          else None)
        return result
    except Exception as exc:
        result["unreachable_reason_class"]=type(exc).__name__
        # Do not copy provider response bodies, credentials, or untrusted errors
        # into the public audit result.
        return result


def main():
    import argparse
    from pathlib import Path
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    args=p.parse_args()
    report=inspect()
    target=Path(args.output)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n",
                      encoding="utf-8")
    print(json.dumps({"status":report["status"],
                      "observed_http_status":report["observed_http_status"],
                      "runtime_compatibility_verified":
                          report["runtime_compatibility_verified"]},ensure_ascii=False))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
