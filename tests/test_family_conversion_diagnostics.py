from __future__ import annotations

import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"))

from family_conversion_diagnostics import (
    PROFILE, build_diagnostics, bind_to_trace, verify_signed_final_binding,
)


def request():
    return {
        "race_id":"LOCAL-TEST-R01",
        "temporal_mode":"FORMAL-PRE-RACE",
        "scheduled_post_at":"2099-01-01T12:00:00+09:00",
        "static_prediction":{"roles":{
            "7":["W","P2","P3"],
            "2":["P2","P3"],
            "6":["P3"],
            "8":["P3"],
            "9":["P2","P3"],
        }},
        "role_registry":[
            {"runner_id":"7","column":"W","status":"CORE","reason":"STATIC_CORE"},
            {"runner_id":"7","column":"P2","status":"CORE","reason":"STATIC_CORE"},
            {"runner_id":"7","column":"P3","status":"CORE","reason":"STATIC_CORE"},
            {"runner_id":"2","column":"P2","status":"CORE","reason":"STATIC_CORE"},
            {"runner_id":"2","column":"P3","status":"CORE","reason":"STATIC_CORE"},
            {"runner_id":"6","column":"P3","status":"PROTECTED","reason":"DIRECT_DISTANCE_PROTECTION"},
            {"runner_id":"8","column":"P3","status":"CORE","reason":"STATIC_CORE"},
            {"runner_id":"9","column":"P2","status":"PROTECTED","reason":"DIRECT_EVIDENCE_PROTECTION"},
            {"runner_id":"9","column":"P3","status":"PROTECTED","reason":"DIRECT_EVIDENCE_PROTECTION"},
        ],
        "pair_dispositions":[
            {"head":"7","second":"2","status":"PURCHASE","reason":"MATERIAL_PAIR"},
        ],
        "third_dispositions":[],
    }


def test_diagnostics_are_nonproduction_and_cover_three_conversion_layers():
    req=request()
    ticket={"tickets":[
        {"bet_type":"EXACTA","selection":[7,2],"stake":100},
        {"bet_type":"TRIFECTA","selection":[7,2,6],"stake":100},
    ]}
    final_package={"roles":req["static_prediction"]["roles"]}
    utility={"summary":[
        {"horse_no":8,"ranks":{"SSR-P3":2}},
        {"horse_no":6,"ranks":{"SSR-P3":9}},
        {"horse_no":9,"ranks":{"SSR-P3":7}},
    ]}
    d=build_diagnostics(
        req,ticket,final_package,utility,
        generated_at="2099-01-01T02:00:00+00:00",basis_sha256="BASIS"
    )
    assert d["profile"]==PROFILE
    assert d["production_effect"]=="NONE"
    assert d["automatic_purchase"] is False
    assert d["existing_common_exact_oos_arms_changed"] is False
    assert d["existing_local_mec_r5_arms_changed"] is False

    winner_ids={x["runner_id"] for x in d["winner_role_migration_candidates"]}
    assert {6,8,9}.issubset(winner_ids)
    assert all(x["purchase_authority"] is False for x in d["winner_role_migration_candidates"])

    residual={(x["head"],x["second"]):x for x in d["pair_residual_candidates"]}
    assert (7,9) in residual
    assert residual[(7,9)]["terminal"]=="PAIR-RESIDUAL"
    assert residual[(7,9)]["automatic_purchase"] is False

    selective={tuple(x["exact"]):x for x in d["selective_exact_candidates"]}
    assert (7,2,8) in selective
    assert "STATIC_P3_CORE" in selective[(7,2,8)]["independent_protection_reasons"]
    assert "KRS_P3_TOP3_REAUDIT" in selective[(7,2,8)]["independent_protection_reasons"]
    # 7>2>6 is already purchased, so it is not a missing-exact diagnostic.
    assert (7,2,6) not in selective
    assert selective[(7,2,8)]["purchase_authority"] is False


def test_signed_final_binding_is_required_and_tamper_fails():
    req=request()
    d=build_diagnostics(
        req,{"tickets":[]},{"roles":req["static_prediction"]["roles"]},{},
        generated_at="2099-01-01T02:00:00+00:00",basis_sha256="BASIS"
    )
    trace=bind_to_trace({},d)
    final={
        "artifact":{"ticket_transport_trace":trace},
        "receipt":{"phase":"FINAL","status":"PASS","artifact_sha256":"FA"},
        "receipt_sha256":"FR",
    }
    att=verify_signed_final_binding(final,d)
    assert att["valid"] is True
    assert att["production_effect"]=="NONE"

    d["winner_role_migration_candidates"].append({"runner_id":99})
    try:
        verify_signed_final_binding(final,d)
        raise AssertionError("tampered diagnostic must fail")
    except AssertionError as e:
        assert "CONTENT_HASH_MISMATCH" in str(e)
