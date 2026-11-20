# 2026-11-20 SON_08 詳細反省（自動・実購入なし）

- 公式着順：1-3-5-4-7（上位3頭 [1, 3, 5]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 1／2着 6／3着 9；W True・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 390／損益 -310／PFS 55.7%
- 参照：{"revision": "SON_08.r2", "ticket_sha256": "9bcac5a6ea144a7fad7274ace37872caaddf3bbbcc116ccbf285891f2954442b", "frozen_at": "2026-11-20T13:26:12.074142+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 3／3着 7；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 10890／損益 4890／PFS 181.5%
- 参照：{"final_receipt_sha256": "1e26669e59af236b4892a9a066bc62f3401916022c434e9da34419b2b0d411d1", "result_receipt_sha256": "b3e1a2cfe7d1f2f3ae2c6d423febc8c55601b3061c6f1567e62982f99dbfe1db", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "0438c33aa7aa7b7dbfd06dccf37406cb72d3fbf4eb374056c8ce7f3dc263b802", "signed_final_ticket_count": 120, "signed_final_total_investment": 12000, "signed_final_settlement": {"invest": 12000, "refund": 0, "effective_invest": 12000, "payout": 10890, "pfs": 90.8}, "effective_revision": "REVISION_2", "source_at": "2026-11-20T05:03:38.206123+00:00", "source_receipt_sha256": "85ad02caf18f97564236bb3a335d841fb3956b2c574c2544d3e2018a6b9dff23", "signed_final_at": "2026-11-20T05:03:45.774650+00:00", "delivered_ticket_sha256": "142fe18433982d5e2c6790f1f57035c3a93a01af5f8c4a13ded9dd580f5175ca", "settled_ticket_sha256": "1e26669e59af236b4892a9a066bc62f3401916022c434e9da34419b2b0d411d1"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 1, "HPI-L": 1}, "ruled_neutral_share": 0.115} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 3, "third_pre_rank": 7, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [1, 3, 5], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_CONFIRMED",  |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_cov |
| CAPITAL | OK | {"pfs": 181.5, "profit_loss": 4890, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `1f9f5a7cc2c401cd`／Learning State `d7382241ee6e`</sub>
