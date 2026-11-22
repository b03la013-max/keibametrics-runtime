# 2026-11-22 MIZ_07 詳細反省（自動・実購入なし）

- 公式着順：8-4-6-2-7（上位3頭 [8, 4, 6]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 2／2着 5／3着 8；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "MIZ_07.r2", "ticket_sha256": "018b8716fbd332dbab7d932a19664b0cffa55b5aebf82a4d18a9d73a5f0d773b", "frozen_at": "2026-11-22T14:40:15.717308+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 3／2着 4／3着 5；W True・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 6230／損益 230／PFS 103.8%
- 参照：{"final_receipt_sha256": "e98d15085bbcfd656c89d5754e9e551f83c3340bfd594d9a0b4bd401d51d0122", "result_receipt_sha256": "4f33c629514b94e2deb4e2cd5cee1e144122892d802d048c444083ecb907e350", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "ff8c8e297085638a056ca6227a46ea08b2276445f7e29bcde792ec7e1b3df404", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 12650, "pfs": 95.8}, "effective_revision": "REVISION_2", "source_at": "2026-11-22T06:17:15.576367+00:00", "source_receipt_sha256": "19471f8188b8ed576e365007c8889a687e63299ebdc7fcffb0e4f5d2e27df270", "signed_final_at": "2026-11-22T06:17:27.286763+00:00", "delivered_ticket_sha256": "ffcc8b9d8329990a737924ec512ef65ea95293a8c2870ffc876567394b518f92", "settled_ticket_sha256": "e98d15085bbcfd656c89d5754e9e551f83c3340bfd594d9a0b4bd401d51d0122"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 3, "T3I-L": 6, "HPI-L": 1}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 3, "second_pre_rank": 4, "third_pre_rank": 5, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [8, 4, 6], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | OK | {"pfs": 103.8, "profit_loss": 230, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `0eb7689cc3da6eb3`／Learning State `4bfdff99b40b`</sub>
