# 2026-11-17 OHI_03 詳細反省（自動・実購入なし）

- 公式着順：4-2-5-3-8（上位3頭 [4, 2, 5]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：third_in_P3

## PAPER

- 1着の事前順位 8／2着 1／3着 2；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 140／損益 -560／PFS 20.0%
- 参照：{"revision": "OHI_03.r2", "ticket_sha256": "e25383ae8197acf57a92c9873c213a0cbd72b2e209cc51b6a9527ec78c55f8c2", "frozen_at": "2026-11-17T14:50:09.023195+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 4／2着 7／3着 8；W False・P2 False・P3 True
- Top3捕捉 0／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "810f01c9b63fb4acdd09f7f98b390df2afe67d10fb2a9f1bb69fa4acb5f8d9aa", "result_receipt_sha256": "71465094a3f4ec0d053d07fdfb4611dca61d117195e6aa0c2c2ea3ba9aaf9134", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "0d05d5d0adea15c97f9d5c22d3602ecd171d6ac922d8f519ab33e377a0479618", "signed_final_ticket_count": 105, "signed_final_total_investment": 10500, "signed_final_settlement": {"invest": 10500, "refund": 0, "effective_invest": 10500, "payout": 0, "pfs": 0.0}}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 4, "SRI-L": 4, "T3I-L": 3, "HPI-L": 5}, "ruled_neutral_share": 0.414} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（クロームタッチ）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 4, "second_pre_rank": 7, "third_pre_rank": 8, "winner_in_W": false, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [4, 2, 5], "rescues": [], "supports": [], "misses": ["WINNER_ROLE_NOT_KRS_SUPPORTED", |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 4, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | {"ruled_neutral_share": 0.414} | ruled-neutral share falls below 15% without source changes | per-venue observation rate in forward_summary | CALCULATED share |

<sub>review sha256 `2aa597d660b4ebce`／Learning State `c48960e112b0`</sub>
