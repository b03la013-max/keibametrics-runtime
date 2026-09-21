from __future__ import annotations

import argparse
import json
from pathlib import Path

from jra_evidence_to_base_candidate import attach_candidate_ledger_to_request, load_mapping
from jra_index_provenance_builder import materialize_index_provenance

REQUIRED = ["HPI","SSI","CFI","RFI","BVI","JTI","CSI","TRI","BWI","GCI","PRI","KGI","VMI",
            "DCR","TPI","ZAI_WIN","ZAI_PLACE","SRI","F3S","T3I"]


def materialize_full_numerical(request, mapping):
    request = attach_candidate_ledger_to_request(request, mapping)
    request = materialize_index_provenance(request)

    required_count = len(request.get("runners", [])) * len(REQUIRED)
    calculated_count = 0
    for runner in request.get("runners", []):
        canonical = runner.get("canonical_components") or {}
        missing = [name for name in REQUIRED if name not in canonical]
        if missing:
            raise ValueError(f"CANDIDATE_CANONICAL_COMPONENTS_MISSING:{runner.get('runner_id')}:{missing}")
        for name in REQUIRED:
            spec = canonical[name]
            if not isinstance(spec.get("value"), (int, float)):
                raise ValueError(f"CANDIDATE_VALUE_INVALID:{runner.get('runner_id')}:{name}")
            if not spec.get("rule_id") or not spec.get("mapping_version"):
                raise ValueError(f"CANDIDATE_PROVENANCE_INVALID:{runner.get('runner_id')}:{name}")
            if not spec.get("evidence_refs") or not spec.get("source_fact"):
                raise ValueError(f"CANDIDATE_EVIDENCE_INVALID:{runner.get('runner_id')}:{name}")
            calculated_count += 1

    request["candidate_full_numerical_summary"] = {
        "required_count": required_count,
        "calculated_count": calculated_count,
        "ruled_hold_count": 0,
        "not_applicable_count": 0,
        "unresolved_count": 0,
        "full_numerical_complete": calculated_count == required_count,
        "authority": mapping["mapping_id"],
        "production_authority": False,
    }
    return request


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("request_json")
    parser.add_argument("--mapping", default="mapping/jra_base_index_evidence_mapping_v0.1_candidate_20260921.json")
    parser.add_argument("--out")
    args = parser.parse_args()

    mapping = load_mapping(args.mapping)
    with open(args.request_json, encoding="utf-8") as f:
        request = json.load(f)

    result = materialize_full_numerical(request, mapping)
    text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
