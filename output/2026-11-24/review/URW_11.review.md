# 2026-11-24 URW_11 詳細反省（自動・実購入なし）

- 公式着順：5-7-1-2-3（上位3頭 [5, 7, 1]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：third_in_P3

## PAPER

- 1着の事前順位 6／2着 10／3着 2；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "URW_11.r2", "ticket_sha256": "ba1a5b3298f79d53aa43da8ee7982c8287e5243e95c7c8fe77b498a7fb8a041d", "frozen_at": "2026-11-24T17:00:28.937627+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 4／2着 9／3着 3；W False・P2 False・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "4a824c75bc3add97600ce332e0042e509885161c5ffad44f10d4d0ee229c461a", "result_receipt_sha256": "3de5468934d36aab5fe80f515053e899942100b9ea20b4aa7688465181457000", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "2717815603ed4ef815cb0a6a856776aa45aa2fd28bc3a2cc8d08fc3cd587358a", "signed_final_ticket_count": 180, "signed_final_total_investment": 18000, "signed_final_settlement": {"invest": 18000, "refund": 0, "effective_invest": 18000, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-24T08:37:20.975123+00:00", "source_receipt_sha256": "27b87c62285f2283a289e8e4bb437e2fc1ccde553506f7c0b71c156dad719f78", "signed_final_at": "2026-11-24T08:37:38.010445+00:00", "delivered_ticket_sha256": "14b2cdf06ed929fb08b371656a51d3a77532171fdce93bdb571093434e45b506", "settled_ticket_sha256": "4a824c75bc3add97600ce332e0042e509885161c5ffad44f10d4d0ee229c461a"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 2, "SRI-L": 2, "T3I-L": 2, "HPI-L": 1}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補4頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 4, "second_pre_rank": 9, "third_pre_rank": 3, "winner_in_W": false, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [5, 7, 1], "rescues": ["WINNER_ROLE_RESCUE"], "supports": ["P3_ROLE_CONFI |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 4, "alternative_signals_that_had_winner_top": ["F3S-L ranked the winner #1", "HPI-L ranked the winne | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `641f76c8b2096150`／Learning State `2769022839d2`</sub>
