"""Bounded, resumable pedigree backfill cursor. Only after validated official harvest."""
from __future__ import annotations
import argparse
from datetime import date,timedelta
import json
from pathlib import Path

DEFAULT = Path("runtime/pedigree_backfill_cursor.json")

def _previous_weekend(day: date) -> date:
    x = day-timedelta(days=1)
    while x.weekday() not in (5,6):
        x -= timedelta(days=1)
    return x

def advance(obj: dict, *, exhausted: bool = False, previous_official_date=None,
            require_official_calendar=False) -> dict:
    if obj.get("status") not in ("ACTIVE","COMPLETE"):
        raise ValueError("BACKFILL_STATE_INVALID")
    if obj["status"] == "COMPLETE":
        return obj
    day = date.fromisoformat(obj["date"])
    slot = int(obj["start_race"])
    width = int(obj["race_batch_size"])
    if not (0 <= slot < 36 and 1 <= width <= 6):
        raise ValueError("BACKFILL_SLOT_INVALID")
    result = dict(obj)
    if exhausted or slot+width >= 36:
        if previous_official_date:
            previous=date.fromisoformat(previous_official_date)
            if previous>=day:raise ValueError('BACKFILL_OFFICIAL_PREVIOUS_DATE_NOT_EARLIER')
            day=previous
        elif require_official_calendar:
            result['calendar_resolution_status']='PENDING_OFFICIAL_PREVIOUS_DATE; NO_WEEKDAY_GUESS'
            return result
        else:
            day = _previous_weekend(day)  # legacy offline fixture/API compatibility only
        result["date"] = day.isoformat()
        result["start_race"] = 0
    else:
        result["start_race"] = slot+width
    result["completed_batch_count"] = int(obj.get("completed_batch_count",0))+1
    if day < date.fromisoformat(obj["earliest_date"]):
        result["status"] = "COMPLETE"
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--cursor",type=Path,default=DEFAULT)
    ap.add_argument("--next",action="store_true")
    ap.add_argument("--exhausted",action="store_true")
    ap.add_argument('--official-calendar',action='store_true')
    args=ap.parse_args()
    obj=json.loads(args.cursor.read_text())
    if args.next:
        previous=None
        transition=args.exhausted or int(obj['start_race'])+int(obj['race_batch_size'])>=36
        if args.official_calendar and transition:
            try:
                import sys
                sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'runtime/jra_source_runtime'))
                from jra_pedigree_harvest import _Client,previous_official_race_date
                previous=previous_official_race_date(_Client(delay=1.3,stop_on_access_denied=True),obj['date'])
            except Exception as exc:
                obj={**obj,'calendar_resolution_error':f'{type(exc).__name__}:{exc}'[:180]}
        obj=advance(obj,exhausted=args.exhausted,previous_official_date=previous,
                    require_official_calendar=args.official_calendar)
        args.cursor.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(obj,ensure_ascii=False))

if __name__=="__main__":main()
