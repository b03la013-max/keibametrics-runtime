"""Owner-captured BLOOD BIAS + TSL facts -> per-race supplemental evidence packs.

Owner decision 2026-11-14 15:16 JST (上濵さん, Owner):
  * BLOOD BIAS (blood-b.com, Owner's member session) is the primary pedigree
    source and is weighted in ZAI (BVI 15%, JRA-ZAI-v1.1).
  * TSL (jra.k-ba.net, odds theory) is adopted one tier lower, through VMI
    external_index_support (VMI 5% in ZAI, JRA-ZAI-v1.1).
  * Raw captures stay in the private evidence repository; the public pack
    carries only the registered band category, the private capture digest and
    the horse number/name already public on the official card.

The pack is the existing KM-JRA-SUPPLEMENTAL-EVIDENCE-PACK-v1.0 contract, so
apply_supplemental_evidence_pack keeps every existing guard (cutoff, registry,
universe, conflict, result-derived).
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
from pathlib import Path

PROFILE = "KM-JRA-SUPPLEMENTAL-EVIDENCE-PACK-v1.0-20260926"
VENUE_BY_BB = {"01": "SPP", "02": "HKD", "03": "FKS", "04": "NGT", "05": "TKY",
               "06": "NKY", "07": "CHK", "08": "KYO", "09": "HSN", "10": "KKR"}
VENUE_BY_TSL = VENUE_BY_BB

RULES = {
    "sire_track_signal": "KM-JRA-BLOODB-SIRE-COURSE-RANK-BAND-v1",
    "pedigree_class": "KM-JRA-BLOODB-SIRE-GENERATION-RANK-BAND-v1",
    "pedigree_distance": "KM-JRA-BLOODB-SIRE-DISTANCE-TYPE-RANK-BAND-v1",
    "expert_support": "KM-JRA-BLOODB-PEDIGREE-EVALUATION-MARK-v1",
    "external_index_support": "KM-JRA-TSL-MARK-BAND-v1",
}
TSL_MARK = {"◎": "VERY_STRONG", "○": "STRONG", "▲": "POSITIVE", "☆": "POSITIVE",
            "△": "NEUTRAL", "×": "MIXED"}
BLOODB_EVAL = {"血": "VERY_STRONG", "注": "STRONG"}


def sha(x) -> str:
    return hashlib.sha256(json.dumps(x, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def rank_band(value):
    """Sire ranking position (1 = best). Blank / non-numeric = no observation."""
    s = str(value or "").strip()
    if not re.fullmatch(r"\d{1,3}", s) or int(s) < 1:
        return None
    r = int(s)
    if r <= 3:
        return "EXCEPTIONAL"
    if r <= 10:
        return "VERY_STRONG"
    if r <= 20:
        return "STRONG"
    if r <= 35:
        return "POSITIVE"
    if r <= 55:
        return "NEUTRAL"
    if r <= 75:
        return "MIXED"
    return "CAUTION"


def distance_type(surface: str, distance: int):
    """BLOOD BIAS category: p speed / s standard / t stamina (site help2)."""
    if surface == "芝":
        return "P" if distance <= 1400 else "S" if distance <= 1800 else "T"
    if surface in ("ダ", "W"):
        return "P" if distance <= 1300 else "S" if distance <= 1700 else "T"
    return None


def race_id_from_rcode(rcode: str) -> str:
    # YYYYMMDD VV KK DD RR  (blood-b rcode, e.g. 2026111505050411)
    if not re.fullmatch(r"\d{16}", rcode):
        raise ValueError("BLOODB_RCODE_INVALID:" + rcode)
    return f"KM-JRA-{VENUE_BY_BB[rcode[8:10]]}-{rcode[:8]}-R{int(rcode[14:16]):02d}"


def race_id_from_tsl(date8: str, url: str) -> str:
    m = re.search(r"/(\d{8})/(\d{2})\d{8}/(\d{2})/", url)
    if not m or m.group(1) != date8:
        raise ValueError("TSL_URL_INVALID:" + url)
    return f"KM-JRA-{VENUE_BY_TSL[m.group(2)]}-{date8}-R{int(m.group(3)):02d}"


def _feature(cat, rule, src, fact):
    return {"category": cat, "rule_id": rule, "evidence_refs": [f"SUPP:{src}"],
            "source_fact": fact, "result_derived": False}


def bloodb_features(race: dict, src_id: str):
    course = race.get("course") or ""
    m = re.search(r"(芝|ダ|W|障)(\d{3,4})", course)
    cat = distance_type(m.group(1), int(m.group(2))) if m else None
    out = {}
    for h in race.get("horses") or []:
        no = str(int(h["no"]))
        f = {}
        b = rank_band(h.get("CR"))
        if b:
            f["sire_track_signal"] = _feature(b, RULES["sire_track_signal"], src_id,
                                              f"BLOOD BIAS CR(コース別サイアーランキング) band={b} ({no}番)")
        b = rank_band(h.get("GR"))
        if b:
            f["pedigree_class"] = _feature(b, RULES["pedigree_class"], src_id,
                                           f"BLOOD BIAS GR(世代別サイアーランキング) band={b} ({no}番)")
        if cat:
            b = rank_band(h.get("type_" + cat))
            if b:
                f["pedigree_distance"] = _feature(b, RULES["pedigree_distance"], src_id,
                                                  f"BLOOD BIAS 血統タイプ{cat.lower()} band={b} ({no}番)")
        b = BLOODB_EVAL.get(str(h.get("blood_eval") or "").strip())
        if b:
            f["expert_support"] = _feature(b, RULES["expert_support"], src_id,
                                           f"BLOOD BIAS 血統評価 band={b} ({no}番)")
        if f:
            out[no] = f
    return out


def tsl_features(race: dict, src_id: str):
    out = {}
    for h in race.get("horses") or []:
        no = str(int(h["no"]))
        b = TSL_MARK.get(str(h.get("mark") or "").strip(), "CAUTION")
        out[no] = {"external_index_support": _feature(
            b, RULES["external_index_support"], src_id, f"TSL 印 band={b} ({no}番)")}
    return out


def bloodb_from_compact(compact: dict) -> dict:
    """Browser compact: [rcode, course, "no:CR:GR:W:P:S:T:eval,..."]."""
    races = []
    for rcode, course, rows in compact["races"]:
        horses = []
        for row in [x for x in rows.split(",") if x]:
            p = row.split(":")
            if len(p) != 8:
                raise ValueError("BLOODB_COMPACT_ROW_INVALID:" + rcode)
            horses.append({"no": int(p[0]), "CR": p[1], "GR": p[2], "type_W": p[3], "type_P": p[4],
                           "type_S": p[5], "type_T": p[6], "blood_eval": p[7]})
        races.append({"rcode": rcode, "course": course, "horses": horses})
    return {"captured_at": compact["captured_at"], "races": races}


def build_packs(bloodb: dict | None, tsl: dict | None, *, ingested_at: str):
    """Return {race_id: pack}. Raw bodies never enter a pack, only digests."""
    by_race: dict[str, dict] = {}
    srcs: dict[str, dict] = {}
    if bloodb:
        for race in bloodb.get("races") or []:
            if race.get("error") or not race.get("horses"):
                continue
            if re.search(r"障", race.get("course") or ""):
                continue
            rid = race_id_from_rcode(race["rcode"])
            sid = "BLOODB-" + race["rcode"]
            srcs.setdefault(rid, {})[sid] = {
                "source_id": sid, "authority": "USER_PROVIDED_PRE_RACE",
                "source_class": "OWNER_SUBSCRIPTION_BROWSER_CAPTURE",
                "origin": "https://www.blood-b.com/main.php?rcode=" + race["rcode"],
                "content_sha256": sha(race), "available_at": bloodb["captured_at"],
                "ingested_at": ingested_at, "result_derived": False, "production_use": "ALLOWED",
                "private_store": "keibametrics-evidence-private"}
            for no, f in bloodb_features(race, sid).items():
                by_race.setdefault(rid, {}).setdefault(no, {}).update(f)
    if tsl:
        for race in tsl.get("races") or []:
            if race.get("error") or not race.get("horses"):
                continue
            rid = race_id_from_tsl(tsl["date8"], race["url"])
            sid = f"TSL-{tsl.get('kind', 'first').upper()}-" + rid
            srcs.setdefault(rid, {})[sid] = {
                "source_id": sid, "authority": "USER_PROVIDED_PRE_RACE",
                "source_class": "OWNER_BROWSER_CAPTURE_PUBLIC_INDEX",
                "origin": "https://jra.k-ba.net" + race["url"],
                "content_sha256": sha(race), "available_at": tsl["captured_at"],
                "ingested_at": ingested_at, "result_derived": False, "production_use": "ALLOWED",
                "private_store": "keibametrics-evidence-private"}
            for no, f in tsl_features(race, sid).items():
                by_race.setdefault(rid, {}).setdefault(no, {}).update(f)
    packs = {}
    for rid, feats in by_race.items():
        captured = max(s["available_at"] for s in srcs[rid].values())
        pack = {"profile": PROFILE, "family_id": "JRA", "race_id": rid, "captured_at": captured,
                "sources": sorted(srcs[rid].values(), key=lambda s: s["source_id"]),
                "runner_features": {k: feats[k] for k in sorted(feats, key=int)},
                "owner_decision": "OWNER-2026-11-14-BLOODB-PRIMARY-TSL-SECONDARY"}
        pack["pack_sha256"] = sha(pack)
        packs[rid] = pack
    return packs


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--bloodb")
    ap.add_argument("--tsl")
    ap.add_argument("--out-dir", default="runtime/jra_supplemental_packs")
    a = ap.parse_args(argv)
    load = lambda p: json.loads(Path(p).read_text(encoding="utf-8")) if p else None
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    bb = load(a.bloodb)
    if bb and bb.get("races") and isinstance(bb["races"][0], list):
        bb = bloodb_from_compact(bb)
    packs = build_packs(bb, load(a.tsl), ingested_at=now)
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for rid, pack in packs.items():
        (out / f"{rid}.json").write_text(json.dumps(pack, ensure_ascii=False, indent=1) + "\n",
                                         encoding="utf-8")
    print(json.dumps({"packs": len(packs), "features": sum(
        len(f) for p in packs.values() for f in p["runner_features"].values())}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
