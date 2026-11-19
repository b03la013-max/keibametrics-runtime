# 2026-11-19 OHI_12 詳細反省（自動・実購入なし）

- 公式着順：10-9-2-12-3（上位3頭 [10, 9, 2]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：third_in_P3

## PAPER

- 1着の事前順位 5／2着 6／3着 7；W False・P2 False・P3 False
- Top3捕捉 0／Top4捕捉 0；Head-local P2 None；Pair条件付き3着 None
- 投資 900／返還 0／払戻 0／損益 -900／PFS 0.0%
- 参照：{"revision": "OHI_12.r2", "ticket_sha256": "a08c2524503ff3354e31431ab29868353a73c839c362af48b3a2ea8bc94af4e1", "frozen_at": "2026-11-19T20:05:10.661585+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 4／2着 7／3着 1；W False・P2 False・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "c99cb7f4d46c69c1c1e1aee27863d845cd39691dba8a60dde4f183874abbde79", "result_receipt_sha256": "a2566964c26470c872819c576133d3025e6b576a570f01be4bf94f2cdf677074", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "1fbc1ae2213741ef9f716f9db32b9edb69c1873d926f4f39454814e286fe4701", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": null, "signed_final_at": "2026-11-19T11:41:14.998995+00:00", "delivered_ticket_sha256": "a602145fb87b466101743f8161178428cd35a31b378f6de58b170276b975fef5", "settled_ticket_sha256": "c99cb7f4d46c69c1c1e1aee27863d845cd39691dba8a60dde4f183874abbde79"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 4, "SRI-L": 2, "T3I-L": 1, "HPI-L": 3}, "ruled_neutral_share": 0.106} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 4, "second_pre_rank": 7, "third_pre_rank": 1, "winner_in_W": false, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [10, 9, 2], "rescues": ["P2_ROLE_RESCUE"], "supports": ["P3_ROLE_CONFIRME |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": true, "ordered_exact_ticket_co |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 4, "alternative_signals_that_had_winner_top": ["T3I-L ranked the winner #1"]} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `69bbaece446a9156`／Learning State `16e66871aa2d`</sub>
