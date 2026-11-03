"""Archived raw-card history for an explicit private identity hypothesis.

Matching name/parents/sex-age does not establish a current permanent horse ID
or a birthdate. This loader records the observed old official anchor separately
and grants no SOURCE, numerical Consumer, model, or OOS authority.
"""
from __future__ import annotations

import base64
from copy import deepcopy
from datetime import date, datetime, timezone, timedelta
import gzip
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unicodedata
from urllib.parse import parse_qs, urljoin, urlsplit

from runtime import local_base63_source_witness as witness
from runtime.local_nar_evidence_candidate import parse_race_card
from runtime.local_physical.source_acquisition import _decode, _html_tables, verify_source_artifact

PROFILE = "KM-FNB-ARCHIVE-COMPOSITE-IDENTITY-HYPOTHESIS-v1"
STATUS = "PRIVATE_COMPOSITE_IDENTITY_HYPOTHESIS_NOT_CURRENT_ID_VERIFIED"
JST = timezone(timedelta(hours=9))


def normalize(value):
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", str(value or "")))


def composite_key(name, sire, dam, damsire, sex_age):
    return tuple(map(normalize, (name, sire, dam, damsire, sex_age)))


def _stamp(value):
    value = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if value.tzinfo is None:
        raise ValueError("ARCHIVE_COMPOSITE_AWARE_ASOF_REQUIRED")
    return value


def _hash(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False).encode()).hexdigest()


class _HorseAnchors(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.current = None
        self.anchors = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.current = [dict(attrs).get("href", ""), []]

    def handle_data(self, data):
        if self.current is not None:
            self.current[1].append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self.current is not None:
            self.anchors.append((self.current[0], normalize("".join(self.current[1]))))
            self.current = None


def _observed_id(anchors, name, base_url):
    found = set()
    for href, label in anchors:
        if label != normalize(name):
            continue
        url = urlsplit(urljoin(base_url, href))
        if (url.scheme != "https" or url.hostname not in {"www.keiba.go.jp", "keiba.go.jp"}
                or url.path != "/KeibaWeb/DataRoom/HorseMarkInfo"
                or url.username or url.password or url.port not in (None, 443)):
            continue
        ids = parse_qs(url.query).get("k_lineageLoginCode") or []
        if len(ids) != 1 or not ids[0].isdigit():
            raise ValueError("ARCHIVE_COMPOSITE_HORSE_ANCHOR_AMBIGUOUS")
        found.add(ids[0])
    if len(found) != 1:
        raise ValueError("ARCHIVE_COMPOSITE_ONE_DIRECT_HORSE_ANCHOR_REQUIRED")
    return "NAR:"+next(iter(found))


def _candidate_date(start):
    match = re.fullmatch(r"(\d{2})\.(\d{2})\.(\d{2})", str(start.get("date", "")))
    if not match:
        raise ValueError("ARCHIVE_COMPOSITE_DATED_START_REQUIRED")
    return date(2000+int(match[1]), int(match[2]), int(match[3]))


def _semantic(start):
    # Ignore display spellings and parser diagnostic text; every scoring input
    # is retained. Exact conflicting facts cannot silently overwrite a run.
    keys = ("finish", "field_size", "distance", "surface", "direction", "going",
            "horse_no", "ride_popularity", "ride_body_weight", "ride_jockey",
            "ride_carried_weight", "content_time_seconds", "content_positions",
            "content_final3f", "margin", "race_name", "class_score", "finish_score")
    out = {key: start.get(key) for key in keys}
    for key in ("going", "race_name", "ride_jockey"):
        out[key] = normalize(out[key])
    return out


def _archive_rows(path, as_of, target_year, raw_envelope=None):
    raw_envelope = path.read_bytes() if raw_envelope is None else raw_envelope
    envelope = json.loads(raw_envelope)
    source, receipt = envelope.get("artifact") or {}, envelope.get("receipt") or {}
    if (not envelope.get("signature") or envelope.get("signature_alg") != "Ed25519"
            or not envelope.get("signer_key_id") or _hash(receipt) != envelope.get("receipt_sha256")
            or receipt.get("artifact_sha256") != _hash(source)
            or receipt.get("family") != "LOCAL" or receipt.get("phase") != "SOURCE"
            or receipt.get("status") != "SOURCE_FROZEN" or receipt.get("errors")
            or receipt.get("race_id") != source.get("race_id")):
        raise ValueError("ARCHIVE_COMPOSITE_ENVELOPE_HASH_OR_SIGNATURE_PRESENCE_INVALID")
    okay, errors = verify_source_artifact(source)
    if not okay:
        raise ValueError("ARCHIVE_COMPOSITE_SOURCE_HASH_INVALID:"+",".join(errors))
    cards = [s for s in source.get("sources", []) if s.get("official") is True
             and s.get("source_class") == "OFFICIAL_RACE_CARD_CURRENT_STATE_BODY_WEIGHT"]
    if len(cards) != 1:
        raise ValueError("ARCHIVE_COMPOSITE_ONE_CARD_REQUIRED")
    card = cards[0]
    fetched = _stamp(card["fetched_at"])
    if fetched >= as_of:
        raise ValueError("ARCHIVE_COMPOSITE_CAPTURE_AT_OR_AFTER_ASOF")
    contexts = []
    for field in ("requested_url", "final_url"):
        url = urlsplit(card[field]); query = parse_qs(url.query)
        if (url.scheme != "https" or url.hostname not in {"www.keiba.go.jp", "keiba.go.jp"}
                or url.path != "/KeibaWeb/TodayRaceInfo/DebaTable"):
            raise ValueError("ARCHIVE_COMPOSITE_CARD_URL_SCOPE")
        if any(len(query.get(k, [])) != 1 for k in ("k_raceDate", "k_raceNo", "k_babaCode")):
            raise ValueError("ARCHIVE_COMPOSITE_CARD_RACE_AMBIGUOUS")
        contexts.append((date.fromisoformat(query["k_raceDate"][0].replace("/", "-")),
                         int(query["k_raceNo"][0]), int(query["k_babaCode"][0])))
    if contexts[0] != contexts[1] or contexts[0][0].year != target_year:
        raise ValueError("ARCHIVE_COMPOSITE_YEAR_OR_REDIRECT_IDENTITY_CONFLICT")
    archive_day, number, venue = contexts[0]
    if archive_day > fetched.astimezone(JST).date() or archive_day >= as_of.astimezone(JST).date():
        raise ValueError("ARCHIVE_COMPOSITE_ARCHIVE_DATE_AFTER_AVAILABLE_ASOF")
    raw = gzip.decompress(base64.b64decode(card["raw_gzip_b64"], validate=True))
    if len(raw) > 8_000_000 or len(raw) != card["byte_count"]:
        raise ValueError("ARCHIVE_COMPOSITE_CARD_RAW_SIZE")
    text = _decode(raw, card.get("content_type", ""))
    tables = _html_tables(text)
    carrier = (source.get("normalized_evidence") or {}).get("race_card_tables") or {}
    if (carrier.get("value") != tables or carrier.get("source_id") != card["source_id"]
            or carrier.get("snapshot_sha256") != card["snapshot_sha256"]
            or carrier.get("fetched_at") != card["fetched_at"]):
        raise ValueError("ARCHIVE_COMPOSITE_RAW_TABLE_REPLAY_MISMATCH")
    candidate = parse_race_card(source)
    parser = witness.OriginalTables(); parser.feed(text)
    active = source.get("active_runner_universe") or source.get("official_runner_universe") or {}
    ids = {str(r.get("runner_id") or r.get("horse_no")) for r in active.get("runners", [])}
    if not ids or ids-set(candidate):
        raise ValueError("ARCHIVE_COMPOSITE_ARCHIVED_ACTIVE_SET_INVALID")
    request = {"runners": [{"runner_id": rid, "name": candidate[rid]["name"]} for rid in ids]}
    independent = witness.parse_original_runners(parser, source, request)
    anchors = _HorseAnchors(); anchors.feed(text)
    for rid in sorted(ids, key=int):
        row, independent_row = candidate[rid], independent[rid]
        if (normalize(row["name"]) != normalize(independent_row["name"])
                or normalize(row["sire"]) != normalize(independent_row["sire"])
                or normalize(row["dam"]) != normalize(independent_row["dam"])
                or normalize(row["damsire"]) != normalize(str(independent_row["damsire"]).strip("()（）"))):
            raise ValueError("ARCHIVE_COMPOSITE_INDEPENDENT_LABEL_PARSE_CONFLICT")
        key = composite_key(row["name"], row["sire"], row["dam"], row["damsire"], row["sex_age"])
        if any(not part for part in key) or not re.fullmatch(r"[牡牝セ騸]\d+", key[-1]):
            continue
        observed_id = _observed_id(anchors.anchors, row["name"], card["final_url"])
        paired = []
        for start, decimal in zip(row["starts"], independent_row["history"]):
            when = _candidate_date(start)
            if when != decimal["date"] or start["finish"] != decimal["finish"] or start["distance"] != decimal["distance"]:
                raise ValueError("ARCHIVE_COMPOSITE_INDEPENDENT_HISTORY_CONFLICT")
            if when >= archive_day or when > fetched.astimezone(JST).date() or when >= as_of.astimezone(JST).date():
                raise ValueError("ARCHIVE_COMPOSITE_HISTORY_AFTER_AVAILABLE_DATE")
            paired.append((when, deepcopy(start), deepcopy(decimal)))
        if len(row["starts"]) != len(independent_row["history"]):
            raise ValueError("ARCHIVE_COMPOSITE_INDEPENDENT_HISTORY_COUNT_CONFLICT")
        yield key, observed_id, paired, {"envelope_path": str(path),
            "envelope_sha256": hashlib.sha256(raw_envelope).hexdigest(),
            "receipt_sha256": envelope["receipt_sha256"], "source_id": card["source_id"],
            "snapshot_sha256": card["snapshot_sha256"], "raw_sha256": card["raw_sha256"],
            "fetched_at": card["fetched_at"], "archive_race_date": archive_day.isoformat(),
            "archive_race_no": number, "archive_venue_code": venue,
            "archived_runner_id": rid, "signature_present_not_crypto_verified_here": True}


def build_archive_index(repo_root, envelope_paths, as_of, target_year=2026):
    """Reparse pinned archive envelopes; invalid/ambiguous keys remain HOLD.

    Caller applies the target's exact five-label composite and excludes target
    day history. Return IDs refer only to observed old anchors, never current
    identity verification. Private research use must stay explicitly separate.
    """
    root, cutoff = Path(repo_root).resolve(), _stamp(as_of)
    entries, holds, snapshots, input_manifest = {}, [], set(), []
    blocked = set()
    for supplied in envelope_paths:
        path = Path(supplied)
        if not path.is_absolute(): path = root/path
        if path.is_symlink():
            raise ValueError("ARCHIVE_COMPOSITE_EXISTING_REPOSITORY_ENVELOPE_REQUIRED")
        path = path.resolve()
        if root not in path.parents:
            raise ValueError("ARCHIVE_COMPOSITE_EXISTING_REPOSITORY_ENVELOPE_REQUIRED")
        try:
            raw_envelope = path.read_bytes()
            input_manifest.append({"path": str(path), "repository_relative_path": str(path.relative_to(root)),
                "sha256": hashlib.sha256(raw_envelope).hexdigest(), "bytes": len(raw_envelope)})
            # Validate the complete archive before retaining any of its rows.
            # The manifest hashes the same bytes, not a second mutable read.
            archive_rows = list(_archive_rows(path, cutoff, target_year, raw_envelope))
            for key, observed_id, paired, ref in archive_rows:
                snapshots.add(ref["snapshot_sha256"])
                if key in blocked: continue
                item = entries.setdefault(key, {"archive_identity_status": STATUS,
                    "status": "UNIQUE_ARCHIVED_COMPOSITE_HYPOTHESIS",
                    "archived_observed_id": observed_id, "current_horse_id": None,
                    "birthdate_match_verified": False, "target_year": target_year,
                    "starts": [], "independent_history": [], "source_refs": [], "provenance": [],
                    "formal_source_admitted": False, "signature_cryptographically_verified_here": False,
                    "_events": {}})
                if item["archived_observed_id"] != observed_id:
                    blocked.add(key); entries.pop(key, None)
                    holds.append({"key": list(key), "reason": "ARCHIVE_COMPOSITE_CONFLICTING_OBSERVED_IDS"})
                    continue
                if ref["snapshot_sha256"] not in {x["snapshot_sha256"] for x in item["provenance"]}:
                    item["provenance"].append(ref)
                    item["source_refs"].extend([ref["source_id"], ref["snapshot_sha256"], ref["raw_sha256"]])
                for when, start, independent in paired:
                    event = (when.isoformat(), normalize(start["venue"]))
                    old = item["_events"].get(event)
                    if old is not None and _semantic(old[1]) != _semantic(start):
                        blocked.add(key); entries.pop(key, None)
                        holds.append({"key": list(key), "event": list(event),
                            "reason": "ARCHIVE_COMPOSITE_CONFLICTING_DATED_START_FACTS"})
                        break
                    if old is None:
                        item["_events"][event] = (when, start, independent)
        except (ValueError, KeyError, TypeError, OSError) as exc:
            if not input_manifest or input_manifest[-1]["path"] != str(path):
                input_manifest.append({"path": str(path), "repository_relative_path": str(path.relative_to(root)),
                    "sha256": None, "bytes": None, "read_error": str(exc)})
            holds.append({"path": str(path), "reason": str(exc)})
    for item in entries.values():
        pairs = sorted(item.pop("_events").values(), key=lambda v: v[0], reverse=True)
        item["starts"] = [p[1] for p in pairs]
        item["independent_history"] = [p[2] for p in pairs]
        item["source_refs"] = sorted(set(item["source_refs"]))
    ambiguous = [list(key) for key in sorted(blocked)]
    receipt = {"profile": PROFILE,
        "classification": STATUS, "as_of": cutoff.astimezone(timezone.utc).isoformat(), "target_year": target_year,
        "unique_archive_snapshots": len(snapshots), "composite_entries": len(entries),
        "hold_count": len(holds), "birthdate_matching_claimed": False,
        "current_permanent_ids_inferred": False, "signature_crypto_verified_here": False,
        "source_or_consumer_authority_granted": False, "new_raw_acquisition": 0,
        "input_manifest": input_manifest, "input_manifest_sha256": _hash(input_manifest),
        "holds_sha256": _hash(holds), "ambiguous_keys": ambiguous,
        "ambiguous_keys_sha256": _hash(ambiguous)}
    receipt["sha256"] = _hash(receipt)
    return {"entries": entries, "holds": holds, "ambiguous_keys": ambiguous, "receipt": receipt}
