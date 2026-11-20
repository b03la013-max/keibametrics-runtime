# 2026-11-20 SON_05 詳細反省（自動・実購入なし）

- 公式着順：4-10-3-12-7（上位3頭 [4, 10, 3]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 2／2着 6／3着 1；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 True
- 投資 900／返還 0／払戻 990／損益 90／PFS 110.0%
- 参照：{"revision": "SON_05.r2", "ticket_sha256": "0a622abf6be8d78e0f3e0644cb82ff83ec5b23311c3c475e6b23dd808bd92ff5", "frozen_at": "2026-11-20T11:56:22.964596+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 7／2着 1／3着 2；W False・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "7f9b26b5d4f57220990f2f716369fb498a9526e88b4cee06fd0f2c119a63a141", "result_receipt_sha256": "1b8420339e19ea052d074c0f732743fd55e8c413076c8ba871d57501d37cf404", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "807b370697be42f3ec15f9cae1e0aff14fd0449e0c1ef2bdcada4d3d864c9d77", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-20T03:31:31.014841+00:00", "source_receipt_sha256": "8e091fe388e684e76d84b47c31a86c14b42737b13f7d5421731693a908929c2b", "signed_final_at": "2026-11-20T03:31:40.330404+00:00", "delivered_ticket_sha256": "fc42ca8a0c8cc4fa4271a42b75cbb14650095564e7a40be9e4398cfa4d00493b", "settled_ticket_sha256": "7f9b26b5d4f57220990f2f716369fb498a9526e88b4cee06fd0f2c119a63a141"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 3, "SRI-L": 5, "T3I-L": 8, "HPI-L": 5}, "ruled_neutral_share": 0.121} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補4頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 7, "second_pre_rank": 1, "third_pre_rank": 2, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [4, 10, 3], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CON |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 7, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `dccad064e98a90d1`／Learning State `913927a637d4`</sub>
