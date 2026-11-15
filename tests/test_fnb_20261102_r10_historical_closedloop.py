"""FNB R10 historical genuine signed settlement capability acceptance.

Do not use this retrospective October fixture as November forward OOS.
"""
from copy import deepcopy
import pytest

from runtime.local_fnb_r10_historical_closedloop import (
    EID, _audit_tickets, _assert_envelope, inspect_historical)


def test_real_archived_r06_signed_source_final_result_settlement():
    result=inspect_historical()
    assert result["execution_id"]==EID
    assert result["status"]=="RETROSPECTIVE_R06_CRYPTO_AND_FROZEN_SETTLEMENT_VERIFIED"
    assert result["ticket_audit"]["total_tickets"]==59
    assert result["ticket_audit"]["total_stake"]==5900
    assert result["ticket_audit"]["total_payout"]==9320
    assert result["ticket_audit"]["hit_count_per_type"]=={"TRIO":1}
    assert result["settled_pfs_percent"]==157.966102
    assert result["settled_profit_loss"]==3420
    assert result["all_three_stored_ed25519_signatures_verified_with_archived_key"] is True
    assert result["fresh_online_gateway_health_verified"] is False
    assert result["official_result_provider_issuer_independently_queried"] is False
    assert result["actual_purchase_verified"] is False
    assert result["recipient_delivery_ack_verified"] is False
    assert result["new_2026_11_02_formal_prediction"] is False
    assert result["registered_forward_oos_increment"]==0


def test_frozen_ticket_math_ignores_unrelated_unselected_favorites():
    official={"finish_order":[3,8,9],
              "payouts":{"EXACTA":19510,"TRIO":9320,"TRIFECTA":78400}}
    tickets=[
        {"bet_type":"EXACTA","selection":[3,9],"stake":100},
        {"bet_type":"TRIO","selection":[9,3,8],"stake":200},
        {"bet_type":"TRIFECTA","selection":[3,9,8],"stake":100},
    ]
    audit=_audit_tickets(tickets,official)
    assert audit["total_stake"]==400
    assert audit["total_payout"]==18640
    assert audit["hit_count_per_type"]=={"TRIO":1}


@pytest.mark.parametrize("error_case",["negative_stake","duplicate","bad_orientation"])
def test_invalid_ticket_or_wrong_orientation_never_pays_by_set_only(error_case):
    official={"finish_order":[3,8,9],
              "payouts":{"EXACTA":19510,"TRIO":9320,"TRIFECTA":78400}}
    tickets=[{"bet_type":"EXACTA","selection":[3,8],"stake":100}]
    if error_case=="negative_stake":
        tickets[0]["stake"]=-100
        with pytest.raises(ValueError,match="R10_FROZEN_TICKET_CELL_INVALID"):
            _audit_tickets(tickets,official)
    elif error_case=="duplicate":
        tickets.append(deepcopy(tickets[0]))
        with pytest.raises(ValueError,match="R10_DUPLICATE_FROZEN_TICKET"):
            _audit_tickets(tickets,official)
    else:
        tickets[0]["selection"]=[8,3]
        assert _audit_tickets(tickets,official)["total_payout"]==0
