"""Mac Blood-B subscriber last-mile readiness report.

Offline, private, read-only. NEVER opens paid site or prints paid contents,
DataBuyer IDs, cookies, horse-level ratings or paths into private profile.
This is an engineering gate, not evidence of consent, signoff or production.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import platform
import sys

REPO=Path(__file__).resolve().parents[1]
CURRENT_PROFILE="BLOODB-MAC-LAST-MILE-READINESS-v1.0"
SOURCE_FILES=(
  "runtime/jra_bloodb_mac_collector.py",
  "runtime/jra_bloodb_mac_automation.py",
  "runtime/jra_bloodb_mac_probe.py",
  "runtime/jra_bloodb_mac_acceptance.py",
  "scripts/jra_bloodb_signed_source_queue_sync.py",
)
HOME=Path.home()/".keibametrics"

def _private(path:Path)->bool:
    try:
        return not path.is_symlink() and path.stat().st_mode & 0o077 == 0
    except OSError:
        return False

def readiness(*, repo:Path=REPO, home:Path=HOME, now=None,
              os_name:str|None=None)->dict:
    now=now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("TIMEZONE_REQUIRED")
    repo=repo.expanduser().resolve()
    home=home.expanduser().resolve()
    system=os_name if os_name is not None else platform.system()
    missing=[name for name in SOURCE_FILES if not (repo/name).is_file()]
    packages={name:importlib.util.find_spec(name) is not None
              for name in ("bs4","playwright","cryptography")}
    queue=home/"bloodb_queue.json"
    exists=queue.is_file() and _private(queue) and _private(home)
    eligible=0
    expired=0
    unbound=0
    signed_source_unreadable=0
    local_captures=0
    captures_audited=0
    capture_integrity_failed=0
    queue_schema_ok=False
    if exists:
        try:
            rows=json.loads(queue.read_text(encoding="utf-8"))
            if not isinstance(rows,list) or len(rows)>80:
                raise ValueError("QUEUE_SHAPE")
            seen=set()
            from datetime import datetime
            for x in rows:
                if not isinstance(x,dict) or not isinstance(x.get("race_id"),str):
                    raise ValueError("QUEUE_ROW")
                race=x["race_id"]
                if race in seen:
                    raise ValueError("QUEUE_DUPLICATE")
                seen.add(race)
                raw=x["prediction_cutoff"]
                t=datetime.fromisoformat(raw.replace("Z","+00:00"))
                if t.tzinfo is None:
                    raise ValueError("QUEUE_CUTOFF_TZ")
                if t>now:
                    eligible+=1
                    source=x.get("signed_source_envelope_path")
                    if not source:
                        unbound+=1
                    elif not Path(source).is_file():
                        signed_source_unreadable+=1
                else:
                    expired+=1
                directory=home/"private_bloodb"/race
                if directory.is_dir() and _private(directory):
                    local_captures+=1
            queue_schema_ok=True
            # Intentionally not importing local-paid acceptance without an
            # explicit named race, to keep this command cheap and offline.
        except (OSError,ValueError,TypeError,KeyError):
            queue_schema_ok=False
            eligible=expired=unbound=signed_source_unreadable=local_captures=0
    profile=home/"browser_bloodb"
    has_profile=profile.is_dir() and _private(profile) and _private(home)
    agent=Path.home()/"Library/LaunchAgents/jp.keibametrics.bloodb-collector.plist"
    has_agent=agent.is_file() and _private(agent)
    blockers=[]
    if system!="Darwin": blockers.append("NOT_MACOS_EXECUTION_HOST")
    if missing: blockers.append("REPOSITORY_CODE_NOT_INSTALLED")
    if not all(packages.values()): blockers.append("LOCAL_DEPENDENCIES_MISSING")
    if not has_profile: blockers.append("LOCAL_SUBSCRIBER_PROFILE_NOT_INITIALIZED")
    if not queue_schema_ok: blockers.append("PRIVATE_SIGNED_QUEUE_UNAVAILABLE")
    if queue_schema_ok and eligible==0: blockers.append("NO_FUTURE_SOURCE_BOUND_RACE_IN_QUEUE")
    if unbound or signed_source_unreadable: blockers.append("FUTURE_QUEUE_SOURCE_NOT_ACCESSIBLE")
    if not has_agent: blockers.append("LOCAL_LAUNCHD_AGENT_NOT_INSTALLED")
    # These cannot be truthfully verified by a locally authored Boolean.
    blockers += ["PROVIDER_AUTOMATION_PERMISSION_NOT_INDEPENDENTLY_VERIFIED",
                 "REAL_SUBSCRIBER_DOM_ACCEPTANCE_NOT_OBSERVED"]
    return {
      "profile":CURRENT_PROFILE,
      "status":"BLOCKED_UNTIL_USER_MAC_LIVE_ACCEPTANCE",
      "mac_os":system=="Darwin",
      "repository_complete":not missing,
      "missing_code_count":len(missing),
      "dependencies_present":packages,
      "private_profile_dir_present":has_profile,
      "profile_login_validity":"NOT_CHECKED_OFFLINE",
      "private_queue_valid":queue_schema_ok,
      "eligible_future_queue_count":eligible,
      "expired_queue_count":expired,
      "unsigned_future_queue_count":unbound,
      "source_file_missing_count":signed_source_unreadable,
      "local_paid_capture_directory_count":local_captures,
      "launch_agent_file_present":has_agent,
      "provider_permission_independent_proof":False,
      "live_member_dom_acceptance_run":False,
      "production_authority":False,"bvi_population_authority":False,
      "signed_final":False,"oos_increment":0,
      "paid_content_exported":False,
      "blockers":blockers,
      "next_step":"ON_USER_MAC: LOG_IN; VERIFY_PROVIDER_PERMISSION; INSPECT/PROBE REAL FUTURE RACE; LIVE ACCEPTANCE",
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo",type=Path,default=REPO)
    ap.add_argument("--home",type=Path,default=HOME)
    a=ap.parse_args()
    print(json.dumps(readiness(repo=a.repo,home=a.home),ensure_ascii=False,sort_keys=True,indent=2))
if __name__=="__main__":
    main()
