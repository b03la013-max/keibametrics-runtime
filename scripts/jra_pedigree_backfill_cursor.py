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

def advance(obj: dict, *, exhausted: bool = False) -> dict:
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
        day = _previous_weekend(day)
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
    args=ap.parse_args()
    obj=json.loads(args.cursor.read_text())
    if args.next:
        obj=advance(obj,exhausted=args.exhausted)
        args.cursor.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(obj,ensure_ascii=False))

if __name__=="__main__":main()
