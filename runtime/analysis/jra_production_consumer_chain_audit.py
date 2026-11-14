"""Read-only audit: did the signed SOURCE and the Base13/Derived7 values actually
reach the Production Static Owner, KRS and the Signed FINAL for every race?

For every immutable FINAL of one race date this replays, from the stored
artifacts only (no network, no writes outside --out):

C1 SOURCE binding   one SOURCE snapshot SHA across compiler, package, Static,
                    ticket; temporal order source_freeze <= static <= KRS <=
                    FINAL freeze < post.
C2 Active universe  runner set in the index ledger == Active runners of the
                    signed SOURCE checkpoint for the same execution.
C3 Arithmetic       13 Base values + 7 Derived values per runner present and in
                    range; ZAI_WIN / ZAI_PLACE / TPI_base recomputed from the
                    Base values with the registered fixed formula.
C4 Static consumed  Static Owner ranking == ledger ranking == order by ZAI_WIN.
C5 KRS actual       receipt EXECUTED, actual == requested runs, parameter map
                    SHA equals the package's, receipt time inside the window.
C6 FINAL            final receipt PASS, freeze before post.
C7 Observation      Base13 component coverage: required (registered mapping)
                    vs present components, by feature (separate from C3: a
                    calculated cell is not an observed component).

Nothing here changes Production numbers; it only reports.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import glob
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE13 = ["HPI", "SSI", "CFI", "RFI", "BVI", "JTI", "CSI", "TRI", "BWI", "GCI", "PRI", "KGI", "VMI"]
DERIVED = {"DCR": "dcr_score", "TPI": "tpi_final", "ZAI_WIN": "zai_win", "ZAI_PLACE": "zai_place",
           "SRI": "sri", "F3S": "f3s", "T3I": "t3i"}
TOL = 1e-6


def _t(s):
    return dt.datetime.fromisoformat(str(s).replace("Z", "+00:00"))


def zai_win(v):
    return (v["HPI"]*.20 + v["SSI"]*.17 + v["CFI"]*.10 + v["RFI"]*.08 + v["JTI"]*.05 + v["CSI"]*.05
            + v["TRI"]*.05 + v["BWI"]*.05 + v["GCI"]*.08 + v["PRI"]*.12 + v["KGI"]*.05)


def zai_place(v):
    return (v["HPI"]*.16 + v["SSI"]*.14 + v["CFI"]*.10 + v["RFI"]*.14 + v["JTI"]*.05 + v["CSI"]*.06
            + v["TRI"]*.05 + v["BWI"]*.08 + v["GCI"]*.08 + v["PRI"]*.08 + v["KGI"]*.06)


def tpi_base(v):
    return (v["HPI"]*.15 + v["SSI"]*.14 + v["CFI"]*.10 + v["RFI"]*.10 + v["BVI"]*.05 + v["JTI"]*.06
            + v["CSI"]*.05 + v["TRI"]*.07 + v["BWI"]*.06 + v["GCI"]*.08 + v["PRI"]*.08 + v["KGI"]*.06)


def source_active(root, execution_id):
    paths = sorted(glob.glob(str(root / f"runtime/executions/{execution_id}/SOURCE/runs/*/source_receipt_envelope.json")))
    for p in reversed(paths):
        art = json.loads(Path(p).read_text()).get("artifact") or {}
        u = art.get("jra_official_runner_universe") or {}
        runners = u.get("active_runners") or u.get("runners") or []
        nums = {str(r.get("horse_no") if isinstance(r, dict) else r) for r in runners
                if not isinstance(r, dict) or r.get("active", True) is not False}
        snap = (art.get("source_snapshot_sha256") or art.get("snapshot_sha256"))
        if nums:
            return nums, snap, p
    return None, None, None


def audit_final(path, root, mapping):
    d = json.loads(Path(path).read_text())
    rid = d["race_id"]
    pkg = d["final_prediction_package"]
    ip = pkg["index_provenance_replay"]
    sp = d["static_prediction"]
    out = {"race_id": rid, "final_path": str(Path(path).relative_to(root)), "checks": {}, "errors": []}
    c = out["checks"]

    snaps = {"compiler": d.get("evidence_feature_compiler_attestation", {}).get("source_snapshot_sha256"),
             "package": pkg.get("source_snapshot_sha256"),
             "static": sp.get("source_basis_snapshot_sha256"),
             "ticket": (d.get("final_ticket") or {}).get("source_snapshot_sha256")}
    ta = d.get("temporal_audit") or {}
    krs = (d.get("krs_run_receipt") or {}).get("receipt") or {}
    post = _t(d["scheduled_post_at"])
    times = {"source_freeze": ta.get("source_freeze_at"), "static_computed": d.get("static_computed_at"),
             "krs": krs.get("timestamp"), "final_freeze": d.get("final_freeze_timestamp")}
    order_ok = all(times.values()) and (_t(times["source_freeze"]) <= _t(times["static_computed"])
                                        <= _t(times["krs"]) <= _t(times["final_freeze"]) < post)
    c["C1_source_binding"] = len(set(snaps.values())) == 1 and None not in snaps.values() and order_ok
    out["source_snapshot_sha256"] = snaps["package"]
    out["times"] = times

    runners = ip["runners"]
    active, src_snap, src_path = source_active(root, d.get("jra_maturity_binding_verification", {}).get(
        "source_execution_id") or f"{rid}-LIVE-R1")
    c["C2_active_universe"] = active is not None and set(runners) == active
    out["active_count"] = len(runners)
    out["source_active_count"] = len(active) if active else None

    cells = bad = 0
    arith = True
    for k, r in runners.items():
        v = r.get("base_final_values") or {}
        for i in BASE13:
            x = v.get(i)
            if isinstance(x, (int, float)) and 0 <= x <= 100:
                cells += 1
            else:
                bad += 1
        for name, key in DERIVED.items():
            x = r.get(key)
            if isinstance(x, (int, float)):
                cells += 1
            else:
                bad += 1
        try:
            if abs(zai_win(v) - r["zai_win"]) > TOL or abs(zai_place(v) - r["zai_place"]) > TOL \
                    or abs(tpi_base(v) - r["tpi_base"]) > TOL:
                arith = False
        except (KeyError, TypeError):
            arith = False
    c["C3_full20_arithmetic"] = bad == 0 and arith
    out["full20_cells"] = cells
    out["full20_required"] = 20 * len(runners)

    by_zai = sorted(runners, key=lambda k: (-runners[k]["zai_win"], int(k)))
    c["C4_static_consumed"] = sp["ranking"] == ip["static_ranking"] == by_zai and \
        all(runners[k]["static_rank"] == i + 1 for i, k in enumerate(sp["ranking"]))

    c["C5_krs_actual"] = (krs.get("status") == "EXECUTED" and krs.get("actual_run_count") == krs.get("requested_run_count")
                          and (krs.get("actual_run_count") or 0) >= 5000
                          and krs.get("parameter_map_sha256") == pkg.get("engine_parameter_map_sha256")
                          and krs.get("race_id") == rid)
    out["krs"] = {k: krs.get(k) for k in ("actual_run_count", "input_sha256", "output_sha256", "engine_sha256", "mode")}

    fr = (d.get("final_receipt") or {}).get("receipt") or {}
    c["C6_final_prestart"] = fr.get("status") == "PASS" and _t(d["final_freeze_timestamp"]) < post
    out["final_receipt_sha256"] = (d.get("final_receipt") or {}).get("receipt_sha256")

    req = pres = 0
    lost = collections.Counter()
    for r in runners.values():
        for idx, t in r["base_index_trace"].items():
            have = {x["feature"] for x in t.get("components", [])}
            for feat in (mapping.get(t.get("profile"), {}).get(idx) or {}):
                req += 1
                if feat in have:
                    pres += 1
                else:
                    lost[feat] += 1
    out["observation"] = {"required_components": req, "present_components": pres,
                          "missing_by_feature": dict(lost.most_common())}
    out["pass"] = all(c.values())
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True, help="YYYY-MM-DD")
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    root = Path(a.root)
    mapping = json.loads((root / "mapping/jra_base_index_evidence_mapping_v1.0_20260921.json").read_text())["index_profiles"]
    d8 = a.date.replace("-", "")
    rows = [audit_final(p, root, mapping) for p in sorted(glob.glob(str(root / f"runtime/final_artifacts/KM-JRA-*-{d8}-R*.json")))]
    total = collections.Counter()
    miss = collections.Counter()
    for r in rows:
        for k, v in r["checks"].items():
            total[k] += int(bool(v))
        total["horses"] += r["active_count"]
        total["full20_cells"] += r["full20_cells"]
        total["full20_required"] += r["full20_required"]
        total["components_required"] += r["observation"]["required_components"]
        total["components_present"] += r["observation"]["present_components"]
        miss.update(r["observation"]["missing_by_feature"])
    summary = {"date": a.date, "finals": len(rows), "all_checks_pass": sum(r["pass"] for r in rows),
               "totals": dict(total), "top_missing_features": dict(miss.most_common(15)),
               "classification": "READ_ONLY_PRODUCTION_CONSUMER_CHAIN_AUDIT"}
    body = {"summary": summary, "races": rows}
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    text = json.dumps(body, ensure_ascii=False, indent=1, sort_keys=True)
    (out / "consumer_chain_audit.json").write_text(text, encoding="utf-8")
    (out / "consumer_chain_audit.sha256").write_text(hashlib.sha256(text.encode()).hexdigest() + "\n")
    print(json.dumps(summary, ensure_ascii=False))
    for r in rows:
        if not r["pass"]:
            print("FAIL", r["race_id"], {k: v for k, v in r["checks"].items() if not v})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
