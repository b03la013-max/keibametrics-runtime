# 2026-11-20 KSM_04 詳細反省（自動・実購入なし）

- 公式着順：3-1-9-8-6（上位3頭 [3, 1, 9]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 7／2着 2／3着 1；W False・P2 True・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 180／損益 -520／PFS 25.7%
- 参照：{"revision": "KSM_04.r2", "ticket_sha256": "b5dccb184042cc9202ddb15b879430cd1ac56d02a13a50e4975fcd67ff382fa1", "frozen_at": "2026-11-20T11:11:04.341871+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 6／2着 1／3着 2；W False・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "4e0ae1f45af721a7e1739f369163da70104d65f106c2b68236e3e330a7ffccfb", "result_receipt_sha256": "fe5c51d8eec6b93703538038c8a7e3a1dc186524350c9673d6513e98fdba0470", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "c891c87b5b38adec42a8b5cdef6558b971a705b0eb119b8260c88ebf67071186", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-20T02:46:14.058982+00:00", "source_receipt_sha256": "9bb73c6bde148ab90615f09ebf66d2718403fff6250a1fb6d429e324a1d992ae", "signed_final_at": "2026-11-20T02:46:21.851579+00:00", "delivered_ticket_sha256": "409133266cf482c65bae7bcabe78b1b9adc7865c9d0ec0d5207360d7ead1110e", "settled_ticket_sha256": "4e0ae1f45af721a7e1739f369163da70104d65f106c2b68236e3e330a7ffccfb"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 3, "SRI-L": 5, "T3I-L": 7, "HPI-L": 3}, "ruled_neutral_share": 0.121} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（ジーティーパリス）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 6, "second_pre_rank": 1, "third_pre_rank": 2, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [3, 1, 9], "rescues": ["WINNER_ROLE_RESCUE", "ORDERED_PAIR_RESCUE", "PAIR |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 6, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `fa2cb827aa78e980`／Learning State `efc12fb27948`</sub>
