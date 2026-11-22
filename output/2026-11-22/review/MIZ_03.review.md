# 2026-11-22 MIZ_03 詳細反省（自動・実購入なし）

- 公式着順：3-4-8-10-5（上位3頭 [3, 4, 8]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 1／2着 2／3着 3；W True・P2 True・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 800／返還 0／払戻 3870／損益 3070／PFS 483.8%
- 参照：{"revision": "MIZ_03.r2", "ticket_sha256": "24dc79c97cdc32d120d75e6c4670de222ab01498def8710a605e8cf90b5dfe75", "frozen_at": "2026-11-22T12:25:16.387190+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 5／3着 2；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 9150／損益 3150／PFS 152.5%
- 参照：{"final_receipt_sha256": "ca88d09e8af49a1402571d9d7aa5112d5c5c121e1ebdca7a97171bbe5524b9f4", "result_receipt_sha256": "1b228fdb9f234e04adfd9185e42c23d655df6017175767864067db3becafaa0a", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "a260e5118354219dc1aeadda12e4f76d60530856d607da3e9c6f8e1fc8b3f9ca", "signed_final_ticket_count": 144, "signed_final_total_investment": 14400, "signed_final_settlement": {"invest": 14400, "refund": 0, "effective_invest": 14400, "payout": 6950, "pfs": 48.3}, "effective_revision": "REVISION_2", "source_at": "2026-11-22T04:02:09.135605+00:00", "source_receipt_sha256": "91eb652439539500642004cf698d67e827759f1a901fe0941f60b4c431148ba8", "signed_final_at": "2026-11-22T04:02:21.355746+00:00", "delivered_ticket_sha256": "b4b7031a64ce63f07dc8a5ee68a12f0087e87100fcf941d40c86f3120677feee", "settled_ticket_sha256": "ca88d09e8af49a1402571d9d7aa5112d5c5c121e1ebdca7a97171bbe5524b9f4"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 2, "T3I-L": 5, "HPI-L": 1}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（メイショウオタモイ）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 5, "third_pre_rank": 2, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [3, 4, 8], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | OK | {"pfs": 152.5, "profit_loss": 3150, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `7d70b745396043b8`／Learning State `87bd2cf3e033`</sub>
