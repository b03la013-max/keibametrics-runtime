# 2026-11-18 OHI_01 詳細反省（自動・実購入なし）

- 公式着順：12-6-8-5-2（上位3頭 [12, 6, 8]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 4／2着 2／3着 1；W False・P2 True・P3 False
- Top3捕捉 2／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 470／損益 -230／PFS 67.1%
- 参照：{"revision": "OHI_01.r2", "ticket_sha256": "13a7c9b072897f314e53e6272d8df51de6fc818ca8c87975e25c8f0c0185c34b", "frozen_at": "2026-11-18T13:45:08.197043+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 8／2着 3／3着 5；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "f273901b7e1a6e905a2501c5fda43a77b93d928ec45323c3885a189af534a89b", "result_receipt_sha256": "34c3c98e018a4b78c753356cb39777be536f73a6c60431608bf96395dd44ca4c", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "8fe8cdeed658cc1966b786a52c7cefe8dc782ea34a883b7913ecfef0f4108da6", "signed_final_ticket_count": 144, "signed_final_total_investment": 14400, "signed_final_settlement": {"invest": 14400, "refund": 0, "effective_invest": 14400, "payout": 0, "pfs": 0.0}}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 6, "TPI-L": 5, "SRI-L": 6, "T3I-L": 10, "HPI-L": 6}, "ruled_neutral_share": 0.107} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（ヤマメセイリュウ）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 8, "second_pre_rank": 3, "third_pre_rank": 5, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [12, 6, 8], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CON |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": true, "ordered_exact_ticket_co |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 8, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `06b5a3e3b07535f7`／Learning State `9ef413847d9a`</sub>
