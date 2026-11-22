# 2026-11-22 MIZ_09 詳細反省（自動・実購入なし）

- 公式着順：1-7-4-8-6（上位3頭 [1, 7, 4]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 1／2着 3／3着 11；W True・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 800／返還 0／払戻 670／損益 -130／PFS 83.8%
- 参照：{"revision": "MIZ_09.r2", "ticket_sha256": "8891da4b92e9b05da7d01da2161e9466c279bad0816fca7c8f1b382bb9626c02", "frozen_at": "2026-11-22T15:55:16.165936+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 1／3着 11；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 490／損益 -5510／PFS 8.2%
- 参照：{"final_receipt_sha256": "19665cf1a04e24b688e6095133e89bdfa52f8b72c61d81d4e571ccb84c93a23c", "result_receipt_sha256": "59c334421e88013230c1704a5c45e60435ce339d1f8a9e6744129b887e73ffa7", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "911defdc5d0767d48830fd9e5e727c0d2ec492c75885a53e64d39f18c48dab32", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 16020, "pfs": 102.7}, "effective_revision": "REVISION_2", "source_at": "2026-11-22T07:32:13.180764+00:00", "source_receipt_sha256": "cab887bc2e2330f52d94453e59bf4f40ff3ca1035253e7648b5b4e05ec1c06b2", "signed_final_at": "2026-11-22T07:32:25.854538+00:00", "delivered_ticket_sha256": "48bc9b5bcc5738311f588776f506ce1a2de3f15b86025a089f146bd2f266048f", "settled_ticket_sha256": "19665cf1a04e24b688e6095133e89bdfa52f8b72c61d81d4e571ccb84c93a23c"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 2, "T3I-L": 4, "HPI-L": 1}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 1, "third_pre_rank": 11, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [1, 7, 4], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 8.2, "profit_loss": -5510, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 8.2, "tickets": 60, "payout": 490} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `f8403b50c45b39b3`／Learning State `fe284d0dfb44`</sub>
