"""Parse the confirmed NANKAN result bound to a frozen KAW SOURCE."""
from __future__ import annotations

import base64
import gzip
import hashlib
import io
from itertools import permutations
import re
import unicodedata

from runtime import urw_nankan_reference_source as nankan
from runtime.local_physical import nankan_kaw_source
from runtime.local_physical.source_acquisition import _html_tables, _html_text, sha_obj, snapshot_from_bytes

PROVIDER = nankan_kaw_source.PROVIDER
PAYOUT_TYPES = {"馬単": "EXACTA", "三連複": "TRIO", "三連単": "TRIFECTA"}
REFUND_STATUSES = {"取消", "出走取消", "除外", "競走除外"}
NONFINISH_STATUSES = {"中止", "競走中止", "失格"}


def _require(condition, code):
    if not condition:
        raise nankan.NankanError(code)


def spec_from_source(artifact):
    context = artifact["source_race_context"]
    provider_id = artifact.get("provider_race_id", "")
    prefix = context["race_date"].replace("-", "") + "21"
    _require(artifact.get("provider") == PROVIDER
             and artifact.get("source_manifest_profile") == nankan_kaw_source.PROFILE
             and context.get("venue_id") == "KAW"
             and re.fullmatch(re.escape(prefix) + r"\d{4}" + f'{context["race_no"]:02d}', provider_id)
             and artifact.get("provider_day_id") == provider_id[:-2],
             "NANKAN_RESULT_FROZEN_SOURCE_IDENTITY")
    return {"source_id": f"NANKAN-{provider_id}-RESULT", "url": f"{nankan.ORIGIN}/result/{provider_id}.do",
            "authority": PROVIDER, "official": True, "priority": 100, "extract": [],
            "source_class": "OFFICIAL_SAME_DAY_RACE_RESULT_PASSING_ORDER"}


def capture(spec, get):
    meta, raw = get(spec["url"])
    _require(meta.get("url") == spec["url"] and meta.get("provider") == PROVIDER
             and meta.get("http_status") == 200 and 0 < len(raw) <= nankan.MAX_BYTES
             and hashlib.sha256(raw).hexdigest() == meta.get("raw_sha256"),
             "NANKAN_RESULT_CAPTURE_IDENTITY")
    snapshot, errors = snapshot_from_bytes(
        spec, raw, final_url=meta["url"], status_code=200, fetched_at=meta["fetched_at"],
        headers={"content-type": "text/html"}, gzip_mtime=0,
    )
    snapshot["source_access_policy"] = meta["source_policy"]
    snapshot["snapshot_sha256"] = sha_obj({k: v for k, v in snapshot.items() if k != "snapshot_sha256"})
    return snapshot, errors


def _compact(text):
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", text))


def _official_raw(snapshot, spec):
    _require(snapshot.get("official") is True and snapshot.get("http_status") == 200
             and snapshot.get("authority") == PROVIDER and snapshot.get("source_id") == spec["source_id"]
             and snapshot.get("requested_url") == snapshot.get("final_url") == spec["url"]
             and snapshot.get("snapshot_sha256") == sha_obj(
                 {k: v for k, v in snapshot.items() if k != "snapshot_sha256"}),
             "NANKAN_RESULT_SNAPSHOT_IDENTITY")
    policy = snapshot.get("source_access_policy") or {}
    robots_status = policy.get("status")
    _require(policy.get("robots_url") == nankan.ROBOTS and policy.get("terms_url") == nankan.TERMS
             and ((robots_status == 200 and re.fullmatch(r"[0-9a-f]{64}", policy.get("robots_sha256") or ""))
                  or (robots_status == 404 and policy.get("robots_sha256") is None))
             and nankan_kaw_source._time(policy.get("checked_at", "")) <=
             nankan_kaw_source._time(snapshot["fetched_at"]), "NANKAN_RESULT_POLICY_EVIDENCE")
    packed = snapshot.get("raw_gzip_b64", "")
    _require(0 < len(packed) <= 2 * nankan.MAX_BYTES, "NANKAN_RESULT_RAW_SIZE")
    with gzip.GzipFile(fileobj=io.BytesIO(base64.b64decode(packed, validate=True))) as stream:
        raw = stream.read(nankan.MAX_BYTES + 1)
    _require(0 < len(raw) <= nankan.MAX_BYTES and len(raw) == snapshot.get("byte_count")
             and hashlib.sha256(raw).hexdigest() == snapshot.get("raw_sha256"), "NANKAN_RESULT_RAW_DIGEST")
    return raw


def _finish(tables, artifact, text):
    candidates = [table for table in tables if table and {"着", "馬番", "馬名"} <= set(table[0])]
    _require(len(candidates) == 1, "NANKAN_RESULT_FINISH_TABLE")
    head, *rows = candidates[0]
    place, number, name = (head.index(field) for field in ("着", "馬番", "馬名"))
    declared = {int(r["horse_no"]): _compact(r["name"]) for r in artifact["declared_runner_universe"]["runners"]}
    active = {int(r["horse_no"]) for r in artifact["active_runner_universe"]["runners"]}
    groups, stopped, excluded, seen = {}, set(), set(), set()
    individual_stop_labels = 0
    for row in rows:
        _require(len(row) > max(place, number, name) and re.fullmatch(r"[1-9]\d*", row[number]),
                 "NANKAN_RESULT_RUNNER_ROW")
        horse = int(row[number])
        _require(horse not in seen and declared.get(horse) == row[name], "NANKAN_RESULT_RUNNER_IDENTITY")
        seen.add(horse)
        label = row[place]
        if label in REFUND_STATUSES:
            excluded.add(horse)
        elif label in NONFINISH_STATUSES and horse in active:
            stopped.add(horse)
            individual_stop_labels += label == "競走中止"
        elif re.fullmatch(r"[1-9]\d*", label) and horse in active:
            groups.setdefault(int(label), []).append(horse)
        else:
            raise nankan.NankanError("NANKAN_RESULT_RUNNER_STATUS")
    _require(active <= seen and text.count("競走中止") == individual_stop_labels, "NANKAN_RESULT_RUNNER_UNIVERSE")
    finish_groups = []
    position = 1
    for rank, horses in sorted(groups.items()):
        _require(rank == position, "NANKAN_RESULT_FINISH_RANK")
        finish_groups.append(sorted(horses))
        position += len(horses)
    _require(position > 3, "NANKAN_RESULT_FINISH_COUNT")
    refunded = sorted(active & excluded)
    if refunded:
        explicit = re.findall(r"返還(?:馬番|馬券|番号)?[:：]?(\d+(?:[、,・-]\d+)*)(?:番|号)?", text)
        confirmed = {int(x) for item in explicit for x in re.findall(r"\d+", item)}
        _require(confirmed == excluded or confirmed == set(refunded), "NANKAN_RESULT_REFUND_NOT_CONFIRMED")
    return finish_groups, sorted(stopped), refunded


def _payouts(tables, finish_groups):
    orders = [()]
    for group in finish_groups:
        slots = 3 - len(orders[0])
        orders = [order + chosen for order in orders for chosen in permutations(group, min(slots, len(group)))]
        if len(orders[0]) == 3:
            break
    expected = {
        "EXACTA": {x[:2] for x in orders},
        "TRIO": {tuple(sorted(x)) for x in orders},
        "TRIFECTA": set(orders),
    }
    found = {}
    for table in tables:
        if len(table) < 3 or not set(table[0]) & PAYOUT_TYPES.keys():
            continue
        labels, subheads, *rows = table
        column = 0
        for label in labels:
            if label == "備考":
                column += 1
                continue
            _require(subheads[column:column + 3] == ["組番", "金額", "人気"], "NANKAN_RESULT_PAYOUT_COLUMNS")
            if label in PAYOUT_TYPES:
                kind = PAYOUT_TYPES[label]
                _require(kind not in found, "NANKAN_RESULT_DUPLICATE_PAYOUT_TABLE")
                found[kind] = {}
                for row in rows:
                    values = row[column:column + 2]
                    if values == ["-", "-"] or values == ["", ""]:
                        continue
                    _require(len(values) == 2 and re.fullmatch(r"[1-9]\d*(?:-[1-9]\d*){1,2}", values[0])
                             and re.fullmatch(r"[1-9]\d*|[1-9]\d{0,2}(?:,\d{3})+", values[1].removesuffix("円")),
                             "NANKAN_RESULT_PAYOUT_ROW")
                    selection = tuple(map(int, values[0].split("-")))
                    _require(selection not in found[kind], "NANKAN_RESULT_DUPLICATE_PAYOUT")
                    found[kind][selection] = int(values[1].removesuffix("円").replace(",", ""))
            column += 3
    _require(found.keys() == expected.keys()
             and all(found[kind].keys() == selections for kind, selections in expected.items()),
             "NANKAN_RESULT_PAYOUT_SELECTIONS")
    return [{"bet_type": kind, "selection": list(selection), "payout_per_100": amount}
            for kind, entries in sorted(found.items()) for selection, amount in sorted(entries.items())]


def parse(snapshot, artifact):
    spec = spec_from_source(artifact)
    raw = _official_raw(snapshot, spec)
    html = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", "", nankan.decode(raw), flags=re.S | re.I)
    text = _compact(_html_text(html))
    if any(marker in text for marker in ("審議中", "成績未確定", "着順未確定", "払戻未確定", "結果未確定")):
        raise nankan.NankanError("OFFICIAL_RESULT_NOT_FINAL")
    if any(marker in text for marker in ("開催中止", "競走取り止め", "競走取止", "競走は中止", "競走を中止")):
        raise nankan.NankanError("OFFICIAL_RESULT_CANCELLATION_HOLD")
    ctx = artifact["source_race_context"]
    year, month, day = map(int, ctx["race_date"].split("-"))
    provider_id = artifact["provider_race_id"]
    meeting, meeting_day = int(provider_id[10:12]), int(provider_id[12:14])
    identity = f'{ctx["race_no"]}R{year}年{month}月{day}日第{meeting}回川崎競馬第{meeting_day}日'
    _require(re.search(r"(?<!\d)" + re.escape(identity), text), "NANKAN_RESULT_PAGE_RACE_IDENTITY")
    tables = [[[_compact(cell) for cell in row] for row in table] for table in _html_tables(html)]
    finish_groups, stopped, refunded = _finish(tables, artifact, text)
    return {"provider": PROVIDER, "finish_groups": finish_groups, "nonfinishers": stopped,
            "refunded_runners": refunded, "payout_rows": _payouts(tables, finish_groups)}
