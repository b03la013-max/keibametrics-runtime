# 2026-11-20 SON_12 詳細反省（自動・実購入なし）

- 公式着順：6-12-8-2-11（上位3頭 [6, 12, 8]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 5／2着 1／3着 6；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "SON_12.r2", "ticket_sha256": "dbe550b17d8e79f7d509fbae1704fc7cbb0a00ffe95e56ff332e6857926ce8d8", "frozen_at": "2026-11-20T15:46:28.659076+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 8／2着 5／3着 6；W False・P2 True・P3 True
- Top3捕捉 0／Top4捕捉 0；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "149fa3221242905c4658a3298853b7f175b7151d422a619c1ba0be44dfc12583", "result_receipt_sha256": "d40b4caeb713bbaee47e9d396f457b9702da218b1646082c802a8da14c85b10f", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "396c7f104f118f20279075b39c794615a33ffd14af2a9d70fedfcf6988819ca2", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-20T07:21:47.812251+00:00", "source_receipt_sha256": "8ee83d878163cee72baf69c9c8df8b22b6afa475f04c5e43c0b41e959036cc5d", "signed_final_at": "2026-11-20T07:21:58.067178+00:00", "delivered_ticket_sha256": "2b0ca7c4d3ca387f0700c05189d15a1c08878b2a13149025d8c1af5d7e7362a8", "settled_ticket_sha256": "149fa3221242905c4658a3298853b7f175b7151d422a619c1ba0be44dfc12583"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 8, "TPI-L": 7, "SRI-L": 8, "T3I-L": 10, "HPI-L": 7}, "ruled_neutral_share": 0.118} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 8, "second_pre_rank": 5, "third_pre_rank": 6, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [6, 12, 8], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CON |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 8, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `c8e44c1f6afbadb8`／Learning State `6e06a43969ca`</sub>
