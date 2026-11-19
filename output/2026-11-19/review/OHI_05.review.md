# 2026-11-19 OHI_05 詳細反省（自動・実購入なし）

- 公式着順：9-7-3-4-8（上位3頭 [9, 7, 3]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 1／2着 5／3着 2；W True・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 170／損益 -530／PFS 24.3%
- 参照：{"revision": "OHI_05.r2", "ticket_sha256": "7e25df24112eb7384a4392c0cb2e84857606dd90a2ce8b7130e07ff14beade00", "frozen_at": "2026-11-19T15:55:01.924919+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 3／3着 1；W True・P2 True・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 7420／損益 1420／PFS 123.7%
- 参照：{"final_receipt_sha256": "cb0020f498f4e7be75ed6d6d1e5e84be4351b33234e73cc077d5e1f4300174d6", "result_receipt_sha256": "cc28d015fd979443a26ca2799f9f0b5180adefe79ddb5cb9458efad0e229f54f", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "e8a09948e8ca0cc2f69c702d67f00b9f7329f84a7e2a37866eb5cc4d3dbeccd3", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 7420, "pfs": 56.2}, "effective_revision": "REVISION_1", "source_at": null, "signed_final_at": "2026-11-19T06:57:32.015110+00:00", "delivered_ticket_sha256": "2edbbfff8ed98258dbc4d8a2e07800675d84d2f9c31c492486ab33e50d7e13e9", "settled_ticket_sha256": "cb0020f498f4e7be75ed6d6d1e5e84be4351b33234e73cc077d5e1f4300174d6"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 2, "T3I-L": 5, "HPI-L": 2}, "ruled_neutral_share": 0.11} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 3, "third_pre_rank": 1, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [9, 7, 3], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | OK | {"pfs": 123.7, "profit_loss": 1420, "hit_but_loss": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `7f83fbc3a9a8f0ad`／Learning State `9131ed3c1e26`</sub>
