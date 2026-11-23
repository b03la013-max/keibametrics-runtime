# 2026-11-23 SAG_04 詳細反省（自動・実購入なし）

- 公式着順：6-2-5-10-8（上位3頭 [6, 2, 5]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 1／2着 3／3着 6；W True・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "SAG_04.r2", "ticket_sha256": "e78a50016f9cd1273aa279235a16a6e89a46d72f3794d9064cac33eea8a08e35", "frozen_at": "2026-11-23T16:21:14.240122+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 3／3着 8；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 1150／損益 -4850／PFS 19.2%
- 参照：{"final_receipt_sha256": "c1a92571f89415e90e4f447774215af03bf20d1ddd517eb475fc9b6a746993d4", "result_receipt_sha256": "02c853f8e4ed50166ed76bbd2c4c78b8a718cf732b6b4b66bc6ab5ba29f15888", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "cf1ccb927d7d08cc2087c435ae705e7e3c69882650f34d05c36ab4d83c12a967", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 4810, "pfs": 36.4}, "effective_revision": "REVISION_2", "source_at": "2026-11-23T07:57:22.476504+00:00", "source_receipt_sha256": "fb978557ffa25f052c6c9d0a67ab0cf3844f1dd1de22d1f87e020891066eb547", "signed_final_at": "2026-11-23T07:57:34.307552+00:00", "delivered_ticket_sha256": "06282b57b6d0bbf39d82cae4539071cb7b67d9a958801f04653f5a49bc1f91ce", "settled_ticket_sha256": "c1a92571f89415e90e4f447774215af03bf20d1ddd517eb475fc9b6a746993d4"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 2, "T3I-L": 3, "HPI-L": 2}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 3, "third_pre_rank": 8, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [6, 2, 5], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 19.2, "profit_loss": -4850, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 19.2, "tickets": 60, "payout": 1150} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `abd2e6dce015b951`／Learning State `8be246676ed6`</sub>
