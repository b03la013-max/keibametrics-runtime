# 2026-11-28 SAG_08 詳細反省（自動・実購入なし）

- 公式着順：7-4-9-1-10（上位3頭 [7, 4, 9]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 6／2着 1／3着 4；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 800／返還 0／払戻 0／損益 -800／PFS 0.0%
- 参照：{"revision": "SAG_08.r2", "ticket_sha256": "672a1a1714cc42554e6f3b37c956c1833afadd4dc7d1fdacdbf693bdb308f836", "frozen_at": "2026-11-28T17:50:15.944131+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 6／2着 1／3着 4；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 420／損益 -5580／PFS 7.0%
- 参照：{"final_receipt_sha256": "cbbd33fa00f443a88eef87991615bee4a9162493be6cdded92dbae437d28b53d", "result_receipt_sha256": "adf44910ce7f072970592e707bd3526a929f0a9612745b36c496570d72ac7d08", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "83aab3c52759331e09aa850206ff85dbe719e38ec9229ab0f48691b40ecaff15", "signed_final_ticket_count": 144, "signed_final_total_investment": 14400, "signed_final_settlement": {"invest": 14400, "refund": 0, "effective_invest": 14400, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_1", "source_at": "2026-11-28T08:52:47.198136+00:00", "source_receipt_sha256": "ab35ed0d992b48e69ea63e2811f76f88aa7c8033b79fb5d559341361985847e2", "signed_final_at": "2026-11-28T08:52:59.908344+00:00", "delivered_ticket_sha256": "c3039c565dfe32d8f3a9577791054511a6bd9dfa985b6abf2180c992c2cc9032", "settled_ticket_sha256": "cbbd33fa00f443a88eef87991615bee4a9162493be6cdded92dbae437d28b53d"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 4, "TPI-L": 3, "SRI-L": 5, "T3I-L": 5, "HPI-L": 1}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（フリージングフォグ）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 6, "second_pre_rank": 1, "third_pre_rank": 4, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [7, 4, 9], "rescues": ["WINNER_ROLE_RESCUE", "ORDERED_PAIR_RESCUE", "PAIR |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 7.0, "profit_loss": -5580, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 6, "alternative_signals_that_had_winner_top": ["HPI-L ranked the winner #1"]} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P1:HIT_BUT_LOSS | P1 | {"pfs": 7.0, "tickets": 60, "payout": 420} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `c8fb165049f3ffcf`／Learning State `f5eb35fb2cce`</sub>
