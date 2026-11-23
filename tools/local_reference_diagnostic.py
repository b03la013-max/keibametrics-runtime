"""Read an immutable LOCAL ordinal reference against a diagnostic result cohort."""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re


def _timestamp(value: str) -> datetime:
    try:
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise ValueError("RESULT_TIMESTAMP_INVALID") from exc
    if stamp.utcoffset() is None:
        raise ValueError("RESULT_TIMESTAMP_INVALID")
    return stamp


def evaluate(reference: Path | None, cohort: dict) -> dict:
    """Evaluate the supplied point forecasts without creating tickets or OOS credit."""
    if cohort["classification"] != "POSTRESULT_DIAGNOSTIC":
        raise ValueError("DIAGNOSTIC_CLASSIFICATION_REQUIRED")
    races = cohort["races"]
    if not races:
        raise ValueError("RESULT_COHORT_EMPTY")
    if any(type(race["race_no"]) is not int or race["race_no"] < 1 for race in races):
        raise ValueError("RESULT_RACE_ID_INVALID")
    if len({race["race_no"] for race in races}) != len(races):
        raise ValueError("RESULT_RACE_DUPLICATE")
    ranks = {race["race_no"]: race["predicted_order"] for race in races}
    for race in races:
        for order in (race["predicted_order"], race["actual_order"]):
            if not isinstance(order, list) or any(type(horse) is not int or horse < 1 for horse in order):
                raise ValueError("RESULT_RUNNER_ID_INVALID")
    if reference is not None:
        raw = reference.read_bytes()
        if hashlib.sha256(raw).hexdigest() != cohort["reference_sha256"]:
            raise ValueError("REFERENCE_SHA_MISMATCH")
        sections = re.split(r"^## (\d+)R｜[^\n]*\n", raw.decode(), flags=re.M)
        parsed = {}
        for index in range(1, len(sections), 2):
            number = int(sections[index])
            rows = re.findall(r"^\| (\d+) \| (\d+) [^|]+ \|", sections[index + 1], re.M)
            if number in parsed or [int(row[0]) for row in rows] != list(range(1, len(rows) + 1)):
                raise ValueError("REFERENCE_RANKS_INVALID")
            parsed[number] = [int(row[1]) for row in rows]
        if parsed != ranks:
            raise ValueError("REFERENCE_RANKS_MISMATCH")
    output = []
    observed = _timestamp(cohort["result_observed_at"]) if cohort.get("result_observed_at") is not None else None
    for race in races:
        if any(race.get(field) for field in ("cancelled", "excluded", "did_not_finish", "dead_heat", "race_abandoned")):
            raise ValueError("RESULT_NOT_STRICT_ORDINAL")
        # Check supplied clocks. A missing publication time remains unknown.
        frozen = _timestamp(race["effective_freeze"]) if race.get("effective_freeze") is not None else None
        published = _timestamp(race["result_publication_time"]) if race.get("result_publication_time") is not None else None
        if ((frozen is not None and observed is not None and frozen >= observed)
                or (frozen is not None and published is not None and frozen >= published)
                or (published is not None and observed is not None and published > observed)):
            raise ValueError("RESULT_TIME_ORDER_INVALID")
        predicted = ranks[race["race_no"]]
        actual = race["actual_order"]
        if (len(predicted) != len(set(predicted)) or len(actual) != len(set(actual)) or len(actual) < 3
                or set(actual) != set(predicted)):
            raise ValueError("RESULT_RUNNER_SET_MISMATCH")
        top = actual[:3]
        matched = [predicted[index] == top[index] for index in range(3)]
        pair = predicted[:2] == top[:2]
        positions = [predicted.index(horse) + 1 for horse in top]
        if positions[0] > 3:
            failure = "REFERENCE_MAIN_CANDIDATE_DISCOVERY"
        elif not matched[0]:
            failure = "REFERENCE_WINNER_ROLE"
        elif not matched[1]:
            failure = "REFERENCE_P2_ROLE"
        elif not matched[2]:
            failure = "REFERENCE_P3_ROLE"
        else:
            failure = "NONE"
        n = len(actual)
        squared = sum((predicted.index(horse) - index) ** 2 for index, horse in enumerate(actual))
        output.append({
            "race_no": race["race_no"], "predicted_top3": predicted[:3], "actual_top3": top,
            "actual_top3_reference_ranks": positions, "position_matches": matched,
            "top3_capture": len(set(predicted[:3]) & set(top)),
            "top3_set_match": set(predicted[:3]) == set(top), "ordered_pair_match": pair,
            "third_after_correct_pair": matched[2] if pair else None,
            "exact_order_match": predicted[:3] == top,
            "spearman_full_order": round(1 - 6 * squared / (n * (n * n - 1)), 9),
            "first_reference_failure": failure,
        })
    return {
        "classification": "POSTRESULT_DIAGNOSTIC", "reference_sha256": cohort["reference_sha256"],
        "original_reference_bytes_verified": reference is not None,
        "race_count": len(output), "runner_count": sum(map(len, ranks.values())),
        "position_matches": [sum(row["position_matches"][i] for row in output) for i in range(3)],
        "top3_capture": sum(row["top3_capture"] for row in output),
        "top3_set_matches": sum(row["top3_set_match"] for row in output),
        "ordered_pair_matches": sum(row["ordered_pair_match"] for row in output),
        "exact_order_matches": sum(row["exact_order_match"] for row in output),
        "reference_pfs": None, "formal_pfs": None, "actual_purchase_pfs": "UNKNOWN",
        "new_oos_credit": 0, "rows": output,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--cohort", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(evaluate(args.reference, json.loads(args.cohort.read_bytes())),
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
