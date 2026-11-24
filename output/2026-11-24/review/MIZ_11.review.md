# 2026-11-24 MIZ_11 詳細反省（自動・実購入なし）

- 公式着順：8-6-5-7-1（上位3頭 [8, 6, 5]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 1／2着 6／3着 4；W True・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "MIZ_11.r2", "ticket_sha256": "9cd8fcff1214288e70b3d7d8dd064872e49fc744a18001082e0e90cac11862d3", "frozen_at": "2026-11-24T16:45:06.283306+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 2／3着 4；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 22280／損益 16280／PFS 371.3%
- 参照：{"final_receipt_sha256": "81e44070711e01e254e56193fe7c08b945a0df72d0392cff7483f4b9ac5874b2", "result_receipt_sha256": "c9051685c8bfb5c9da6a6ae2370eca039e2dd5a9fc4c4077bc1cde4a618f95e8", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "ada9085e30f47501f10a4177930e241ed85fb6199e08e8ebad28b80c481cdbe8", "signed_final_ticket_count": 144, "signed_final_total_investment": 14400, "signed_final_settlement": {"invest": 14400, "refund": 0, "effective_invest": 14400, "payout": 18870, "pfs": 131.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-24T08:22:18.737602+00:00", "source_receipt_sha256": "1316df992c4f6d8463b27d5626d3bc3c7fca6a7c8763132dc70b84d45174969f", "signed_final_at": "2026-11-24T08:22:33.645826+00:00", "delivered_ticket_sha256": "c76b85a387b5b31fc7354201685d668f11f17b4d454fbdf4a874a834083b25d7", "settled_ticket_sha256": "81e44070711e01e254e56193fe7c08b945a0df72d0392cff7483f4b9ac5874b2"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 2, "T3I-L": 1, "HPI-L": 1}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 2, "third_pre_rank": 4, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [8, 6, 5], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | OK | {"pfs": 371.3, "profit_loss": 16280, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `2392bd41b7a5d1a7`／Learning State `1ca13236c359`</sub>
