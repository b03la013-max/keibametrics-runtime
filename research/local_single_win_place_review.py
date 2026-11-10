"""Read-only WIN/PLACE PFS study from actual recorded frozen settlements.

No ticket creation, real purchase inference, numerical-policy changes or OOS
registration. Runs independently of hash-frozen runtime/pfs_grand_review.py.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

PROFILE = "KM-LOCAL-SINGLE-WIN-PLACE-OBSERVATION-v1-20261111"
SINGLE_TYPES = ("WIN", "PLACE")


def _number(x):
    if isinstance(x, bool):
        return None
    try:
        y = float(x)
    except (ValueError, TypeError, OverflowError):
        return None
    return y if math.isfinite(y) else None


def _first_present(obj, *keys):
    if not isinstance(obj, dict):
        return None
    for key in keys:
        if key in obj and obj[key] is not None:
            return obj[key]
    return None


def _type_details(settlement):
    raw = settlement.get("bet_type_summary") or settlement.get("by_bet_type") or []
    if isinstance(raw, dict):
        raw = [dict(value, bet_type=key) for key, value in raw.items()
               if isinstance(value, dict)]
    if not isinstance(raw, list):
        return []
    return [row for row in raw if isinstance(row, dict)]


def _aggregate(rows):
    inv = sum(row["investment"] for row in rows)
    ret = sum(row["return"] for row in rows)
    return {
        "settled_race_count": len(rows),
        "investment": round(inv, 2),
        "return": round(ret, 2),
        "profit_loss": round(ret-inv, 2),
        "pfs_pct": round(ret/inv*100, 8) if inv else None,
        "profitable_race_count": sum(row["return"] > row["investment"] for row in rows),
        "hit_race_count": sum(row["return"] > 0 for row in rows),
        "hit_but_loss_count": sum(0 < row["return"] < row["investment"] for row in rows),
    }


def _tail_check(rows, percent):
    candidates = [r for r in rows if r["investment"] > 0]
    removed = int(len(candidates)*percent/100)
    if removed < 1 or 2*removed >= len(candidates):
        return {"status": "INSUFFICIENT_SAMPLE",
                "sample_races": len(candidates), "removed_each_side": 0,
                "aggregate": None}
    ranked = sorted(candidates, key=lambda r: (r["return"]/r["investment"], r["race_id"]))
    selected = ranked[removed:-removed]
    return {"status": "RESEARCH_AUDIT_NOT_PREDICTIVE_PROOF",
            "sample_races": len(candidates), "removed_each_side": removed,
            "aggregate": _aggregate(selected)}


def _catalog(result_dir):
    by_race = {}
    root = Path(result_dir)
    for path in sorted(root.glob("*.json")) if root.is_dir() else []:
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, UnicodeError):
            continue
        if not isinstance(obj, dict):
            continue
        rid = obj.get("race_id")
        if not isinstance(rid, str) or not rid:
            continue
        by_race.setdefault(rid, []).append((path.name, obj))
    return by_race


def build_report(canonical_rows, *, result_dir="runtime/results"):
    """Use existing frozen Formal canonical totals, but re-read raw type rows.

    The original PFS reader loses zero payouts when parsing some bet-type
    summaries. Never modify that hash-frozen production source in place.
    No prestart certificate is invented from a human-readable status label.
    """
    catalog = _catalog(result_dir)
    arms = {name: [] for name in SINGLE_TYPES}
    held = []
    qualifying = []
    selected = []
    for record in canonical_rows:
        if (record.get("formal_class") != "FORMAL_PRE_RACE"
                or not str(record.get("pfs_authority") or "").upper().startswith("FROZEN")):
            continue
        qualifying.append(record["race_id"])
        rid = record["race_id"]
        sources = catalog.get(rid, [])
        if not sources:
            continue  # No proof of a WIN or PLACE recommendation.
        if len(sources) != 1:
            held.append({"race_id": rid, "reason": "DUPLICATE_RESULT_SOURCE"})
            continue
        filename, source = sources[0]
        s = source.get("settlement") or {}
        if s.get("status") not in ("SETTLED", "COMPLETE"):
            held.append({"race_id": rid, "reason": "SETTLEMENT_NOT_FINAL"})
            continue
        if (not str(s.get("pfs_authority") or "").upper().startswith("FROZEN")
                or source.get("formal_grade") not in ("FORMAL-PRE-RACE", "FORMAL-PRE-RACE / FULL_FORMAL_E2E_PASS")):
            held.append({"race_id": rid, "reason": "FROZEN_PRESTART_TYPE_SOURCE_UNPROVEN"})
            continue
        gross = _number(record.get("investment"))
        gross_return = _number(record.get("return"))
        if gross is None or gross_return is None or gross < 0 or gross_return < 0:
            held.append({"race_id": rid, "reason": "CANONICAL_MONEY_INVALID"})
            continue
        seen = set()
        accepted = []
        invalid = False
        for entry in _type_details(s):
            typ = str(entry.get("bet_type") or "").upper()
            if typ not in SINGLE_TYPES:
                continue
            if typ in seen:
                held.append({"race_id": rid, "bet_type": typ, "reason": "DUPLICATE_TYPE_BREAKDOWN"})
                invalid = True
                break
            seen.add(typ)
            inv = _number(entry.get("investment"))
            ret = _number(_first_present(entry, "payout", "return"))
            if (inv is None or ret is None or inv < 0 or ret < 0
                    or inv > gross + 0.01 or ret > gross_return + 0.01):
                held.append({"race_id": rid, "bet_type": typ,
                             "reason": "TYPE_BREAKDOWN_CONTRADICTS_FROZEN_TOTAL"})
                invalid = True
                break
            if inv == 0 and ret:
                held.append({"race_id": rid, "bet_type": typ,
                             "reason": "NONZERO_RETURN_WITH_ZERO_STAKE"})
                invalid = True
                break
            if inv > 0:
                accepted.append((typ, inv, ret))
        if invalid:
            continue  # Do not partially count a broken single-race breakdown.
        if (sum(inv for _, inv, _ in accepted) > gross + 0.01
                or sum(ret for _, _, ret in accepted) > gross_return + 0.01):
            held.append({"race_id": rid, "reason": "COMBINED_SINGLE_TYPES_EXCEED_CANONICAL_TOTAL"})
            continue
        for typ, inv, ret in accepted:
            arms[typ].append({"race_id": rid, "investment": inv, "return": ret,
                              "source_file": filename})
            selected.append(rid)

    types = {}
    for name, rows in arms.items():
        types[name] = {
            "status": "FROZEN_TYPE_OBSERVATION" if rows else "NO_FROZEN_SINGLE_TYPE_DATA",
            "aggregate": _aggregate(rows),
            "upper_and_lower_1pct_removed": _tail_check(rows, 1),
            "upper_and_lower_3pct_removed": _tail_check(rows, 3),
            "observed_race_ids": sorted(r["race_id"] for r in rows),
        }
    report = {
        "profile": PROFILE,
        "status": "NONPRODUCTION / MEASUREMENT_ONLY / NO_AUTO_ADOPTION",
        "prediction_model_change": False, "purchase_inferred": False,
        "official_prestart_receipts_independently_verified": False,
        "qualifying_frozen_formal_races": len(set(qualifying)),
        "races_with_single_type_records": len(set(selected)),
        "held": held, "bet_types": types,
        "limitations": [
            "Requires a separately recorded settled WIN/PLACE type breakdown.",
            "A frozen/formal label alone does not independently verify original signatures.",
            "No bets are generated from rankings, results or closing odds.",
            "WIN and PLACE may count the same race; their investments must not be added as separate all-system recommendations.",
            "1% and 3% tail exclusion is descriptive robustness, not holdout performance.",
        ],
    }
    report["sha256"] = hashlib.sha256(json.dumps(
        report, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()).hexdigest()
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True)
    parser.add_argument("--result-dir", default="runtime/results")
    args = parser.parse_args()
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"runtime"))
    import pfs_grand_review  # Existing Frozen accounting is read-only.
    report = build_report(pfs_grand_review.canonical_records(), result_dir=args.result_dir)
    target = Path(args.out)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "sha256": report["sha256"],
                      "formal_races": report["qualifying_frozen_formal_races"],
                      "races_with_single_type_records": report["races_with_single_type_records"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
