"""R15 read-only NAR official MOBILE alternative source accessibility probe.

Uses existing SOURCE ACL, HTTPS, DNS SSRF protection, robots policy, timeout
and original Raw SHA. NO special User-Agent, proxy override, robots bypass or
new Production official source route is enabled. Source is in-memory only.
Success would be an observed mobile response, not the desktop table format,
29-index materialization or a signed full SOURCE.
"""
from __future__ import annotations
from datetime import datetime,timezone
import argparse,json
from pathlib import Path
from urllib.parse import urlencode

PROFILE="KM-FNB-R15-NAR-MOBILE-ALTERNATIVE-READONLY-v1"
DATE="2026-11-02"

def spec(race_no):
    if type(race_no) is not int or not 1<=race_no<=12:
        raise ValueError("R15_RACE_NO_INVALID")
    url="https://sp.keiba.go.jp/KeibaWebSP/TodayRaceInfo/S_DebaTable?"+urlencode({
        "k_babaCode":"19","k_raceDate":DATE.replace("-","/"),
        "k_raceNo":str(race_no)})
    return {"source_id":f"NAR-FNB-20261102-R{race_no:02d}-OFFICIAL-MOBILE-CANDIDATE",
            "source_class":"OFFICIAL_MOBILE_CARD_RESEARCH_ONLY",
            "authority":"NAR_OFFICIAL","official":True,
            "priority":100,"required":True,
            "url":url,"max_bytes":600000,"timeout_seconds":12,
            "extract":[{"field":"html_text","type":"html_text","required":True}]}

def probe(race_no, *,fetch=None,now=None):
    from runtime.local_physical.source_acquisition import fetch_source
    from runtime.local_race_day_dispatcher import raw_html
    stamp=now or datetime.now(timezone.utc)
    if stamp.tzinfo is None:
        raise ValueError("R15_ASOF_TIMEZONE_REQUIRED")
    result={"profile":PROFILE,"race_no":race_no,"date":DATE,
            "observation_at":stamp.isoformat(),
            "classification":"OFFICIAL_MOBILE_SOURCE_READ_ONLY_NONPRODUCTION_CANDIDATE",
            "provider_host":"sp.keiba.go.jp",
            "robots_bypass":False,"source_acl_bypass":False,
            "production_source_registry_changed":False,
            "signed_source_verified":False,
            "full_29_index_calculated":False,
            "raw_exported_to_public_github":False,"recipient_delivery_ack":False}
    try:
        fetcher=fetch or fetch_source
        card,errs=fetcher(spec(race_no),"")
        if errs:
            return {**result,"status":"NAR_MOBILE_OBSERVATION_HOLD",
                    "source_error_codes":[str(e).split(":")[0][:90] for e in errs[:8]],
                    "http_status":card.get("http_status")}
        raw_html(card)
        extracted=card.get("extracted_evidence") or {}
        text=extracted.get("html_text")
        if (not isinstance(text,str) or
                "船橋" not in text or
                not any(day in text for day in ("2026年11月2日","2026/11/02",
                                                "2026年11月02日"))):
            raise ValueError("R15_MOBILE_OFFICIAL_CARD_DATE_OR_VENUE_UNKNOWN")
        return {**result,"status":"NAR_MOBILE_ORIGINAL_BYTES_OBSERVED_NO_FORMAL_ADMISSION",
                "http_status":card.get("http_status"),
                "raw_sha256":card.get("raw_sha256"),
                "snapshot_sha256":card.get("snapshot_sha256"),
                "source_id":card.get("source_id"),
                "fetched_at":card.get("fetched_at")}
    except Exception as exc:
        return {**result,"status":"NAR_MOBILE_OBSERVATION_HOLD",
                "source_error_type":type(exc).__name__,
                "source_error_code":str(exc).split(":")[0][:90]}

def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument("--race-no",type=int,required=True)
    parser.add_argument("--output",required=True)
    args=parser.parse_args(argv)
    report=probe(args.race_no)
    out=Path(args.output)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n",
                   encoding="utf-8")
    print(json.dumps({"status":report["status"],"race_no":args.race_no,
                     "error_code":report.get("source_error_code"),
                     "http_status":report.get("http_status"),
                     "production_source_changed":False,
                     "raw_exported":False},ensure_ascii=False))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
