# 2026-11-22 SAG_02 詳細反省（自動・実購入なし）

- 公式着順：5-2-6-7-11（上位3頭 [5, 2, 6]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 4／2着 6／3着 5；W False・P2 False・P3 False
- Top3捕捉 0／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "SAG_02.r2", "ticket_sha256": "b1e05bf9d5c8cf0bb477df0fc76250f29278496c129f55213bd9594cd21f34ff", "frozen_at": "2026-11-22T15:05:03.409652+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 3／2着 6／3着 5；W True・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 9870／損益 3870／PFS 164.5%
- 参照：{"final_receipt_sha256": "793b02ab46c7a679349e2fab7f40a1cba78e13b938367117d40a2e436b9183fd", "result_receipt_sha256": "a41c1cb2bc3cd44a610098e2e2a9605ae9a9eccfa9bb67d28089abaa52e3a5be", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "52224a60721c822dbe81b19e66eea2dfa5fdac5e18d36937ed141b2dd218c418", "signed_final_ticket_count": 144, "signed_final_total_investment": 14400, "signed_final_settlement": {"invest": 14400, "refund": 0, "effective_invest": 14400, "payout": 24820, "pfs": 172.4}, "effective_revision": "REVISION_1", "source_at": "2026-11-22T06:08:05.791045+00:00", "source_receipt_sha256": "66ea666c33fdb51928fb824fc23fcb693222e71632560131475bfb86d31651b9", "signed_final_at": "2026-11-22T06:08:17.881263+00:00", "delivered_ticket_sha256": "2d399d888b4689c232cfd976eee1987054ff09f8daae7415479cbf7f47230e17", "settled_ticket_sha256": "793b02ab46c7a679349e2fab7f40a1cba78e13b938367117d40a2e436b9183fd"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 3, "SRI-L": 3, "T3I-L": 3, "HPI-L": 2}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 3, "second_pre_rank": 6, "third_pre_rank": 5, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [5, 2, 6], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_CONFIRMED",  |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | OK | {"pfs": 164.5, "profit_loss": 3870, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `959e929e4eda52c6`／Learning State `2729ab02f2a8`</sub>
