# 2026-11-20 OHI_11 詳細反省（自動・実購入なし）

- 公式着順：1-2-6-9-13（上位3頭 [1, 2, 6]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：third_in_P3

## PAPER

- 1着の事前順位 3／2着 7／3着 4；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 1600／返還 0／払戻 0／損益 -1600／PFS 0.0%
- 参照：{"revision": "OHI_11.r2", "ticket_sha256": "9ba40e0891ab1c3aec8b07bf8560ff92c015006b8585db63da4f5d42cc9f84b5", "frozen_at": "2026-11-20T19:26:17.653269+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 8／2着 7／3着 5；W False・P2 False・P3 True
- Top3捕捉 0／Top4捕捉 0；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "f4123834ff6b914a6bcd0cf0774405a67131d031c48ef77d1dd6593ffd93be65", "result_receipt_sha256": "f76678617157e3ff874fab2c487111e28d0908fc36ffbff9977c1751970941c7", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "4d3f4f8ecc55aa02970619ff8950dc30ccf0ac1846303bae5c24786126a58cd6", "signed_final_ticket_count": 192, "signed_final_total_investment": 19200, "signed_final_settlement": {"invest": 19200, "refund": 0, "effective_invest": 19200, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_1", "source_at": "2026-11-20T10:30:24.672009+00:00", "source_receipt_sha256": "e9140994057b799a8e7077b6c55aa2f5b18288bcb1474b12ef55ffa3c15781de", "signed_final_at": "2026-11-20T10:30:36.077532+00:00", "delivered_ticket_sha256": "1823c305fd1db9f6fe0786ac6d5c9abdc4b5ebea47812941e8d4890544e10f37", "settled_ticket_sha256": "f4123834ff6b914a6bcd0cf0774405a67131d031c48ef77d1dd6593ffd93be65"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 6, "TPI-L": 6, "SRI-L": 6, "T3I-L": 14, "HPI-L": 7}, "ruled_neutral_share": 0.115} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 8, "second_pre_rank": 7, "third_pre_rank": 5, "winner_in_W": false, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [1, 2, 6], "rescues": [], "supports": ["P3_ROLE_CONFIRMED"], "misses": [" |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 8, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `0f63ef0b860a29e7`／Learning State `f27f07b56c45`</sub>
