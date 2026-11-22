# 2026-11-22 SAG_07 詳細反省（自動・実購入なし）

- 公式着順：3-6-2-5-7（上位3頭 [3, 6, 2]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_P2**
- 正しく判断できた項目：winner_in_W, third_in_P3, winner_is_ticket_head

## PAPER

- 1着の事前順位 3／2着 8／3着 1；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "SAG_07.r2", "ticket_sha256": "8ef1dc9220b294fdad647785357ff2f4b0f55e3433bf75e55c68b75797c31263", "frozen_at": "2026-11-22T17:50:24.857239+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 3／2着 7／3着 2；W True・P2 False・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 False；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "2c8aee579b2809060e537d3302c82aa8581a2ef617b25ee53923d15fc0d3f6ee", "result_receipt_sha256": "84f6a4c9e84db42ff5ab08ea5250f3b9b130e25106adc2e8d0bf5b554ebbb208", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "c29272c80344042395b48530a5d80da58c5cfb23fcbca97b87882a09b8c959a7", "signed_final_ticket_count": 120, "signed_final_total_investment": 12000, "signed_final_settlement": {"invest": 12000, "refund": 0, "effective_invest": 12000, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-22T09:27:13.247112+00:00", "source_receipt_sha256": "b206212d379f50d9b9572662870649dd61bfd6d69cecce1e5bfa00c215c3d952", "signed_final_at": "2026-11-22T09:27:24.428343+00:00", "delivered_ticket_sha256": "61924cba004ddaec3df1d1c5ecb73276639bb1bd66864e07634bd9706e380cfe", "settled_ticket_sha256": "2c8aee579b2809060e537d3302c82aa8581a2ef617b25ee53923d15fc0d3f6ee"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 4, "TPI-L": 3, "SRI-L": 4, "T3I-L": 4, "HPI-L": 3}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（カシノハンゾウ）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 3, "second_pre_rank": 7, "third_pre_rank": 2, "winner_in_W": true, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [3, 6, 2], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P3_ROLE_CONFIRMED"], |
| TICKET | ISSUE | {"head_local_p2": false, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 7} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `1b66da7185543ab2`／Learning State `3a20e8268c46`</sub>
