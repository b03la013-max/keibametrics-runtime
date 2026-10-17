"""Offline Work browser snapshot -> private Blood-B sidecar + existing JRA BVI.

No credentials, network acquisition, new numerical rule, or paid-data upload.
Blood-B rows never enter the official pedigree corpus or feature compiler.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlparse, parse_qs, urljoin
from bs4 import BeautifulSoup

from jra_bloodb_mac_collector import BloodBError, namekey, utc_time
from jra_bloodb_mac_automation import load_official
from jra_pedigree_corpus import _verified_source, _attested
from jra_source_to_evidence_features import compile_source_to_features
from jra_evidence_to_base_production import load_mapping, evaluate_partial_production_base_indices

PROFILE = "BLOODB-WORK-OFFLINE-SNAPSHOT-BVI-BRIDGE-v1"
VENUES = {"01": ("SPP", "札幌"), "02": ("HKD", "函館"),
          "03": ("FKS", "福島"), "04": ("NGT", "新潟"),
          "05": ("TKY", "東京"), "06": ("NKY", "中山"),
          "07": ("CHK", "中京"), "08": ("KYO", "京都"),
          "09": ("HSN", "阪神"), "10": ("KKR", "小倉")}


def snapshot_from_collection(records: list[dict]) -> dict:
    """Adapt private collected main-page tables, preserving original time/links.

    Results and retrospectively fetched horse profiles are never forecast inputs.
    Repeated identical main captures are deduplicated; conflicting captures block.
    """
    races = {}
    for record in records:
        if record.get("kind") != "main":
            continue
        rows = []
        for table in record.get("data", {}).get("tables", []):
            for cells in table:
                if not isinstance(cells, list):
                    raise BloodBError("BLOODB_COLLECTION_CELL_SCHEMA_INVALID")
                links = [link for cell in cells for link in cell.get("links", [])]
                if any(urlparse(link.get("url", "")).path == "/hinfo" for link in links):
                    rows.append({"cells": [cell.get("text") for cell in cells], "links": links})
        race = {"source": record.get("url"), "captured_at": record.get("observed_at"), "rows": rows}
        snapshot_rows(race)
        key = race["source"]
        if key in races:
            if races[key]["rows"] != race["rows"]:
                raise BloodBError("BLOODB_COLLECTION_CONFLICTING_MAIN_CAPTURE")
            if utc_time(races[key]["captured_at"]) <= utc_time(race["captured_at"]):
                continue
        races[key] = race
    if not races:
        raise BloodBError("BLOODB_COLLECTION_MAIN_PAGES_REQUIRED")
    return {"races": list(races.values())}


def evaluate_private_capture(directory: Path, *, root: Path, source_path: Path) -> dict:
    """Connect local Mac collector output to the unchanged official calculator."""
    diagnostic = json.loads((directory / "diagnostic.json").read_text(encoding="utf-8"))
    raw = (directory / "subscriber_page.html").read_bytes()
    if hashlib.sha256(raw).hexdigest() != diagnostic.get("raw_sha256"):
        raise BloodBError("BLOODB_CAPTURE_HTML_HASH_MISMATCH")
    url = diagnostic["origin_url"]
    soup = BeautifulSoup(raw.decode("utf-8"), "html.parser")
    rows = []
    for row in soup.select("tr"):
        cells = row.find_all(["td", "th"], recursive=False)
        links = [{"text": a.get_text(" ", strip=True), "url": urljoin(url, a["href"])}
                 for cell in cells for a in cell.find_all("a", href=True)]
        if any(urlparse(a["url"]).path == "/hinfo" for a in links):
            rows.append({"cells": [c.get_text("\n", strip=True) for c in cells], "links": links})
    return evaluate_race({"source": url, "captured_at": diagnostic["captured_at"], "rows": rows},
                         root=root, source_path=source_path)


def snapshot_rows(race: dict) -> list[dict]:
    """Strict observed 25-cell main table. Preserve abbreviated display names."""
    p = urlparse(race.get("source", ""))
    query = parse_qs(p.query)
    code = query.get("rcode", [""])[0]
    if (p.scheme != "https" or p.netloc != "www.blood-b.com" or p.path != "/main.php"
            or p.fragment or set(query) != {"rcode"} or not re.fullmatch(r"\d{16}", code)):
        raise BloodBError("BLOODB_SNAPSHOT_URL_INVALID")
    utc_time(race.get("captured_at"))
    rows = []
    seen_names, seen_numbers, seen_ids = set(), set(), set()
    for row in race.get("rows", []):
        links = [a for a in row.get("links", []) if urlparse(a.get("url", "")).path == "/hinfo"]
        if not links:
            continue
        c = row.get("cells", [])
        if len(c) != 25 or len(links) != 1 or not all(isinstance(x, str) for x in c):
            raise BloodBError("BLOODB_SNAPSHOT_ROW_SCHEMA_INVALID")
        no, name = namekey(c[0]), namekey(c[1])
        hurl = urlparse(links[0]["url"])
        hid = parse_qs(hurl.query).get("hcode", [""])[0]
        if (not re.fullmatch(r"[1-9]|1[0-8]", no) or not name
                or namekey(links[0].get("text")) != name
                or hurl.scheme != "https" or hurl.netloc != "www.blood-b.com"
                or not re.fullmatch(r"\d{10}", hid)
                or no in seen_numbers or name in seen_names or hid in seen_ids):
            raise BloodBError("BLOODB_SNAPSHOT_IDENTITY_INVALID_OR_DUPLICATE")
        seen_names.add(name); seen_numbers.add(no); seen_ids.add(hid)
        rows.append({"horse_no": no, "horse_name": name, "bloodb_horse_id": hid,
                     "sire_display_and_line": c[14], "damsire_display_and_line": c[15],
                     "grandmaternal_lines": c[16],
                     "observed_labels": {"血統評価": c[5], "血統タイプ": c[8:12],
                                         "相対指数": c[4], "人気ランク": c[2]},
                     "production_authority": False})
    if not 2 <= len(rows) <= 18:
        raise BloodBError("BLOODB_SNAPSHOT_UNIVERSE_INVALID")
    return rows


def evaluate_race(race: dict, *, root: Path, source_path: Path | None = None) -> dict:
    observations = snapshot_rows(race)
    result = {"profile": PROFILE, "source_url": race["source"],
              "captured_at": race["captured_at"], "runner_count": len(observations),
              "bloodb_observations": observations, "bvi_authority": False,
              "static_prediction_authority": False, "oos_increment": 0}
    if source_path is None:
        result.update(status="BLOCKED", reason="MATCHING_SIGNED_JRA_SOURCE_MISSING")
        result["bvi"] = {r["horse_no"]: {"status": "BLOCKED", "value": None,
                           "reason": result["reason"]} for r in observations}
        return result
    checked = _verified_source(source_path)
    if checked is None:
        raise BloodBError("JRA_SOURCE_CRYPTO_OR_SNAPSHOT_INVALID")
    art = json.loads(source_path.read_text(encoding="utf-8"))["artifact"]
    ctx = art.get("source_race_context") or {}
    code = parse_qs(urlparse(race["source"]).query)["rcode"][0]
    if code[8:10] not in VENUES:
        raise BloodBError("BLOODB_SNAPSHOT_VENUE_NOT_SUPPORTED")
    vid, venue = VENUES[code[8:10]]
    day = f"{code[:4]}-{code[4:6]}-{code[6:8]}"
    if (ctx.get("race_date") != day or ctx.get("venue_id") != vid
            or int(ctx.get("race_no") or 0) != int(code[-2:])):
        raise BloodBError("BLOODB_SNAPSHOT_SOURCE_RACE_MISMATCH")
    spec = {"signed_source_envelope_path": str(source_path), "race_id": art["race_id"],
            "race_date": day, "race_no": int(code[-2:]), "venue": venue,
            "prediction_cutoff": art["prediction_cutoff"]}
    official, binding = load_official(spec)
    if {(str(r["horse_no"]), namekey(r["horse_name"])) for r in observations} != {
            (str(r["horse_no"]), namekey(r.get("horse_name") or r.get("name"))) for r in official}:
        raise BloodBError("BLOODB_SNAPSHOT_OFFICIAL_UNIVERSE_MISMATCH")
    at = utc_time(race["captured_at"])
    if not utc_time(art["source_freeze_at"]) <= at < utc_time(art["prediction_cutoff"]):
        raise BloodBError("BLOODB_SNAPSHOT_TEMPORAL_BINDING_INVALID")
    mapping = load_mapping(root / "mapping/jra_base_index_evidence_mapping_v1.0_20260921.json")
    request = [{"runner_id": str(r["horse_no"]), "name": r.get("horse_name") or r["name"]} for r in official]
    # Never merge the observed Blood-B labels into generated JRA features.
    compiled = compile_source_to_features(art, request, mapping)
    runners = []
    for r in request:
        item = compiled["runners"][r["runner_id"]]
        runners.append(dict(r, **item["factual_runner_updates"],
                            evidence_features=item["generated_production_features"]))
    partial = evaluate_partial_production_base_indices(art["race_id"], runners, mapping)
    result["bvi"] = {rid: row["indices"]["BVI"] for rid, row in partial["runners"].items()}
    result["mapping_id"] = mapping["mapping_id"]
    result["pedigree_corpus_manifest"] = compiled["pedigree_corpus_manifest"]
    result["source_binding"] = binding
    result["independent_source_oidc_verified"] = _attested(source_path)
    complete = all(x["status"] == "CALCULATED" for x in result["bvi"].values())
    result["status"] = "CALCULATED_DIAGNOSTIC" if complete else "PARTIAL_DIAGNOSTIC"
    result["production_gate_reason"] = "REQUIRES_CANONICAL_FORMAL_SOURCE_GATE_AND_FULL20_CLOSURE"
    return result


def evaluate_snapshot(snapshot: dict, *, root: Path, source_index: dict | None = None) -> dict:
    races = snapshot.get("races")
    if not isinstance(races, list) or not races:
        raise BloodBError("BLOODB_SNAPSHOT_RACES_REQUIRED")
    output, seen = [], set()
    for race in races:
        url = race.get("source")
        if url in seen:
            raise BloodBError("BLOODB_SNAPSHOT_DUPLICATE_RACE")
        seen.add(url)
        code = parse_qs(urlparse(url).query).get("rcode", [""])[0]
        # Validate before attempting SOURCE selection, including unsupported venues.
        snapshot_rows(race)
        if code[8:10] not in VENUES:
            raise BloodBError("BLOODB_SNAPSHOT_VENUE_NOT_SUPPORTED")
        vid = VENUES[code[8:10]][0]
        paths = sorted((root / "runtime/executions").glob(
            f"KM-JRA-{vid}-{code[:8]}-R{code[-2:]}*/SOURCE/runs/*/source_receipt_envelope.json"))
        if source_index is not None and code in source_index:
            paths = [Path(source_index[code])]
        if len(paths) > 1:
            raise BloodBError("BLOODB_SOURCE_SELECTION_AMBIGUOUS")
        output.append(evaluate_race(race, root=root, source_path=paths[0] if paths else None))
    cells = [c for r in output for c in r["bvi"].values()]
    return {"profile": PROFILE, "race_count": len(output), "runner_count": len(cells),
            "calculated_bvi_count": sum(c["status"] == "CALCULATED" for c in cells),
            "blocked_bvi_count": sum(c["status"] != "CALCULATED" for c in cells),
            "bvi_authority": False, "races": output}
