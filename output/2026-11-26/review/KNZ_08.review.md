# 2026-11-26 KNZ_08 詳細反省（自動・実購入なし）

- 公式着順：1-4-6-3-2（上位3頭 [1, 4, 6]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 1／2着 7／3着 6；W True・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 3940／損益 3240／PFS 562.9%
- 参照：{"revision": "KNZ_08.r2", "ticket_sha256": "aa0b52023d23568e17132e6d31dc25398d5048a40a6c8ef336aa7778d7755f5f", "frozen_at": "2026-11-26T17:30:12.160796+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 6／3着 7；W True・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 2740／損益 -3260／PFS 45.7%
- 参照：{"final_receipt_sha256": "dd9d9907f23fb629940d4ef77d4141eddb66c430fd564d8fdec2d3278f3c82d2", "result_receipt_sha256": "8f6a8137cc72b4e7a1e08b14d2d5fc018e2cdb626fb5ba2d37eb4b5cbd5d6c1e", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "98746b1d0ab502e7dca97e34bf6c099ce9257ab00c1df0b09bafb0b68a757108", "signed_final_ticket_count": 90, "signed_final_total_investment": 9000, "signed_final_settlement": {"invest": 9000, "refund": 0, "effective_invest": 9000, "payout": 78530, "pfs": 872.6}, "effective_revision": "REVISION_2", "source_at": "2026-11-26T09:07:20.870304+00:00", "source_receipt_sha256": "59874f51ae666d6efb4918e22f58363f736eb0b661cc834a9f892816d120c79b", "signed_final_at": "2026-11-26T09:07:31.283045+00:00", "delivered_ticket_sha256": "967e2a2e4a6cdfdfebd857181ad211d45919cbce2afc93aa4a0b1856c35694d7", "settled_ticket_sha256": "dd9d9907f23fb629940d4ef77d4141eddb66c430fd564d8fdec2d3278f3c82d2"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 2, "T3I-L": 4, "HPI-L": 1}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 6, "third_pre_rank": 7, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [1, 4, 6], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "ORDERED_PAIR_CONFIRM |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 45.7, "profit_loss": -3260, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 45.7, "tickets": 60, "payout": 2740} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `e6e6f5e47f4a9949`／Learning State `95999a497a11`</sub>
