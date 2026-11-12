"""Synthetic KAW SOURCE regression. No provider requests or official signature."""
from copy import deepcopy
from datetime import datetime
import hashlib

import pytest

from runtime import execution_store
from runtime.local_nar_evidence_candidate import parse_race_card
from runtime.local_production_static_owner import bind_official_numerical_context
from runtime.local_physical import nankan_kaw_source as source
from runtime.urw_nankan_reference_source import ORIGIN, CALENDAR, ROBOTS, TERMS, NankanError
from test_urw_nankan_reference_source import (
    CAL, DAY, DAY_ID, current_odds_page, current_receipt, detailed_card, program,
)

KAW_DAY_ID = "20261022210704"
REQUEST = {
    "family_id": "LOCAL", "venue_id": "KAW", "race_id": "KM-LOCAL-KAW-20261022-R01-LIVE-R1",
    "race_date": DAY, "race_no": 1, "prediction_cutoff": DAY + "T12:18:00+09:00",
    "scheduled_post_at": DAY + "T12:20:00+09:00",
}
FREEZE = datetime.fromisoformat(DAY + "T12:11:00+09:00")


def as_kaw(raw):
    return raw.decode().replace("浦和競馬", "川崎競馬").replace(DAY_ID, KAW_DAY_ID).encode()


def pages():
    card = as_kaw(detailed_card()).replace("ダ1,300m".encode(), "馬場：良 ダ1,300m".encode())
    for number in (1, 2):
        number_cell = f'<td class="umaban">{number}</td>'.encode()
        card = card.replace(number_cell, f'<td class="waku">{number}</td>'.encode() + number_cell)
    changes = (
        '<meta charset="UTF-8"><section class="nk23_c-block01"><header>2026年10月22日'
        '<h3 class="nk23_c-block01__info__title">川崎競馬</h3></header>'
        '<p class="nk23_c-text02">本日開催に変更情報がありません</p></section>'
        '<section class="nk23_c-block01"><header>2026年10月22日'
        '<h3 class="nk23_c-block01__info__title">浦和競馬</h3></header>'
        '<li class="nk23_c-block01__list__item" id="01">別場の変更</li></section>'
    ).encode()
    return {
        CALENDAR: CAL + as_kaw(CAL),
        ORIGIN + f"/program/{KAW_DAY_ID}.do": as_kaw(program()),
        ORIGIN + f"/uma_shosai/{KAW_DAY_ID}01.do": card,
        ORIGIN + f"/odds/{KAW_DAY_ID}0101.do": as_kaw(current_odds_page()),
        source.CHANGES: changes,
    }


def fixture_access_policy(fetched_at):
    return {"robots_url": ROBOTS, "terms_url": TERMS, "status": 200,
            "robots_sha256": "a" * 64, "checked_at": fetched_at}


def acquire(raws=None):
    raws = pages() if raws is None else raws
    requested = []

    def get(url):
        requested.append(url)
        raw = raws[url]
        receipt = current_receipt(raw, url)
        return {**receipt, "source_policy": fixture_access_policy(receipt["fetched_at"])}, raw

    artifact = source.acquire(REQUEST, get, now=lambda: FREEZE)
    assert requested == list(raws)
    return artifact


def test_kaw_manifest_preserves_provider_bytes_and_feeds_evidence():
    artifact = acquire()
    assert artifact["provider"] == "NANKAN_OFFICIAL"
    assert artifact["provider_race_id"] == KAW_DAY_ID + "01"
    assert [r["runner_id"] for r in artifact["official_runner_universe"]["runners"]] == ["1", "2"]
    assert [s["raw_sha256"] for s in artifact["sources"]] == [
        hashlib.sha256(raw).hexdigest() for raw in pages().values()
    ]
    assert parse_race_card(artifact)["1"]["odds"] == 1.7
    assert parse_race_card(artifact)["1"]["current_body_weight"] == 481
    request = bind_official_numerical_context(REQUEST, artifact)
    assert request["race"]["distance"] == 1300
    assert request["race"]["class"] == "C3"
    from runtime.local_race_entry import assess, materialize_production
    numerical = materialize_production(artifact, {**request, "runners": artifact["official_runner_universe"]["runners"]},
                                       assess()["required_indices"])
    assert numerical["strict_full_numerical_ready"] is True
    assert numerical["numeric_coverage"]["numeric_value_count"] == 58
    with pytest.raises(execution_store.ExecutionStoreError, match="PRIVATE_SOURCE_PUBLIC_STORAGE_FORBIDDEN"):
        execution_store.require_public_storage(artifact)


def test_kaw_source_reparses_raw_instead_of_trusting_rehashed_summary():
    artifact = deepcopy(acquire())
    artifact["parsed_nankan_facts"]["1"]["current_body_weight"] = 999
    artifact["source_snapshot_sha256"] = source.sha_obj(
        {k: v for k, v in artifact.items() if k != "source_snapshot_sha256"})
    with pytest.raises(NankanError, match="NANKAN_KAW_DERIVED_SOURCE_CHANGED"):
        source.verify(artifact)


@pytest.mark.parametrize("case, message", [
    ("venue", "NANKAN_PROGRAM_VENUE_BODY_REQUIRED"),
    ("odds", "NANKAN_KAW_BETTING_MEMBERSHIP_UNKNOWN"),
    ("changes", "NANKAN_KAW_TARGET_CHANGES_UNKNOWN"),
    ("cancelled", "NANKAN_KAW_CANCELLATION_CONFLICT"),
])
def test_kaw_source_holds_on_incomplete_or_conflicting_official_observations(case, message):
    raws = pages()
    if case == "venue":
        raws[ORIGIN + f"/program/{KAW_DAY_ID}.do"] = as_kaw(program()).replace(
            "川崎競馬".encode(), "浦和競馬".encode())
    elif case in {"odds", "cancelled"}:
        raws[ORIGIN + f"/odds/{KAW_DAY_ID}0101.do"] = as_kaw(current_odds_page(
            unknown=case == "odds", cancelled=case == "cancelled"))
    else:
        raws[source.CHANGES] = raws[source.CHANGES].replace("本日開催に変更情報がありません".encode(), b"")
    with pytest.raises(NankanError, match=message):
        acquire(raws)


def test_expired_kaw_intent_cannot_fetch_a_provider():
    with pytest.raises(NankanError, match="NANKAN_KAW_CUTOFF_PASSED"):
        source.acquire(REQUEST, lambda url: pytest.fail(url),
                       now=lambda: datetime.fromisoformat(REQUEST["prediction_cutoff"]))


@pytest.mark.parametrize(
    ("labels", "refund", "expected_refund", "expected_trifecta"),
    [
        (["1", "2", "3", "4", "4", "競走中止"], "", [], 1),
        (["1", "2", "3", "3", "競走除外", "競走中止"], "返還馬番：5番", [5], 2),
    ],
)
def test_confirmed_result_and_settlement(labels, refund, expected_refund, expected_trifecta):
    from runtime.local_physical import nankan_kaw_result as result
    from runtime.urw_nankan_reference_source import url_scope

    artifact = acquire()
    runners = [{"horse_no": h, "runner_id": str(h), "name": f"Fixture-{h}"} for h in range(1, 7)]
    for field in ("declared_runner_universe", "active_runner_universe"):
        artifact[field]["runners"] = runners
    spec = result.spec_from_source(artifact)
    assert url_scope(spec["url"]).path == f"/result/{KAW_DAY_ID}01.do"
    with pytest.raises(NankanError, match="NANKAN_URL_SCOPE_HOLD"):
        url_scope(spec["url"].replace(KAW_DAY_ID, DAY_ID))
    rows = "".join(f"<tr><td>{label}</td><td>{h}</td><td>Fixture-{h}</td></tr>"
                   for h, label in enumerate(labels, 1))
    second_win = ("<tr><td>1-2-4</td><td>1,400</td><td>3</td>"
                  "<td>1-2-4</td><td>2,500</td><td>3</td></tr>") if expected_trifecta == 2 else ""
    html = (f"<p>1R 2026年10月22日 第7回 川崎競馬 第4日</p>"
            f"<table><tr><th>着</th><th>馬番</th><th>馬名</th></tr>{rows}</table>"
            "<table><tr><th colspan='3'>馬単</th></tr><tr><th>組番</th><th>金額</th><th>人気</th></tr>"
            "<tr><td>1-2</td><td>540</td><td>2</td></tr></table>"
            "<table><tr><th colspan='3'>三連複</th><th colspan='3'>三連単</th></tr>"
            "<tr><th>組番</th><th>金額</th><th>人気</th><th>組番</th><th>金額</th><th>人気</th></tr>"
            "<tr><td>1-2-3</td><td>1,000</td><td>1</td><td>1-2-3</td><td>2,000</td><td>2</td></tr>"
            f"{second_win}</table><p>{refund}</p>")

    def snapshot(body):
        raw = body.encode()
        observed = DAY + "T12:26:00+09:00"
        data, errors = result.capture(spec, lambda url: ({
            "url": url, "http_status": 200, "provider": result.PROVIDER, "fetched_at": observed,
            "raw_sha256": hashlib.sha256(raw).hexdigest(), "source_policy": fixture_access_policy(observed),
        }, raw))
        assert errors == []
        return data

    data = snapshot(html)
    parsed = result.parse(data, artifact)
    assert parsed["refunded_runners"] == expected_refund
    assert parsed["nonfinishers"] == [6]
    assert sum(row["bet_type"] == "TRIFECTA" for row in parsed["payout_rows"]) == expected_trifecta
    with pytest.raises(NankanError, match="NANKAN_RESULT_PAGE_RACE_IDENTITY"):
        result.parse(snapshot(html.replace("第4日", "第5日")), artifact)
    with pytest.raises(NankanError, match="NANKAN_RESULT_PAYOUT_SELECTIONS"):
        result.parse(snapshot(html.replace("<td>1-2</td>", "<td>2-1</td>")), artifact)
    with pytest.raises(NankanError, match="NANKAN_RESULT_SNAPSHOT_IDENTITY"):
        result.parse({**data, "authority": "NAR_OFFICIAL"}, artifact)
    if expected_refund:
        with pytest.raises(NankanError, match="NANKAN_RESULT_REFUND_NOT_CONFIRMED"):
            result.parse(snapshot(html.replace(refund, "")), artifact)

    final = {"receipt": {"race_id": REQUEST["race_id"]}, "receipt_sha256": "fixture-final",
             "artifact": {"final_ticket": {"tickets": [
                 {"bet_type": "EXACTA", "selection": [1, 2], "stake": 100},
                 {"bet_type": "TRIO", "selection": [3, 1, 2], "stake": 200},
                 {"bet_type": "TRIFECTA", "selection": [1, 2, 4], "stake": 100},
                 {"bet_type": "TRIFECTA", "selection": [1, 2, 5], "stake": 100},
             ]}}}
    req = {"race_id": REQUEST["race_id"], "official_outcome": parsed, "source": spec["url"],
           "result_available_at": data["fetched_at"],
           "official_snapshot_sha256": data["snapshot_sha256"],
           "official_result_verification_ref": spec["url"] + "#sha256=" + data["raw_sha256"],
           "finish_order": [runner for group in parsed["finish_groups"] for runner in group]}
    payload, by_type = execution_store.build_local_result_payload(req, final)
    amounts = payload["settlement"]
    assert (amounts["investment"], amounts["refund"], amounts["effective_investment"], amounts["payout"]) == (
        (500, 100, 400, 5040) if expected_refund else (500, 0, 500, 2540))
    assert by_type["TRIO"]["return"] == 2000
    if expected_refund:
        assert by_type["TRIFECTA"]["refund"] == 100
        assert by_type["TRIFECTA"]["payout"] == 2500
