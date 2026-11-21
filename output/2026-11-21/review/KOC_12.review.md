# 2026-11-21 KOC_12 詳細反省（自動・実購入なし）

- 公式着順：11-4-7-1-5（上位3頭 [11, 4, 7]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：third_in_P3

## PAPER

- 1着の事前順位 6／2着 3／3着 4；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 900／返還 0／払戻 0／損益 -900／PFS 0.0%
- 参照：{"revision": "KOC_12.r2", "ticket_sha256": "4f6a9e25e1933ce6742bd9d69d9b81fdef9d31551fc45b87fa30ab92901384e1", "frozen_at": "2026-11-21T20:05:14.675054+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 6／2着 8／3着 1；W False・P2 False・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "62289e6024f10f4328b1375f6a2afae5426bc7040e9c668e2df9708aae27b909", "result_receipt_sha256": "da7f3b63366c6554aa204316df4180fda6079d04f26e567e1e622da7a553db7b", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "8bf918108572c67e8ddcd6cde0bfc4aa9b578cdf1cbc5b4df749f657e44d5950", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_1", "source_at": "2026-11-21T11:06:37.152731+00:00", "source_receipt_sha256": "4dcd6b2d175d1680f3abb0d99449c2ab14ba2008b3a90569ee9563a3eb775364", "signed_final_at": "2026-11-21T11:06:47.115373+00:00", "delivered_ticket_sha256": "1182da736b7e1b95086c2e2edd6b8fbb54054135802e59c10702db1c26258334", "settled_ticket_sha256": "62289e6024f10f4328b1375f6a2afae5426bc7040e9c668e2df9708aae27b909"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 8, "TPI-L": 7, "SRI-L": 7, "T3I-L": 8, "HPI-L": 6}, "ruled_neutral_share": 0.115} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 6, "second_pre_rank": 8, "third_pre_rank": 1, "winner_in_W": false, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [11, 4, 7], "rescues": ["P2_ROLE_RESCUE"], "supports": ["P3_ROLE_CONFIRME |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 6, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `6b191864375bf77a`／Learning State `633603f61599`</sub>
