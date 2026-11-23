# 2026-11-23 KNZ_05 詳細反省（自動・実購入なし）

- 公式着順：4-8-3-5-1（上位3頭 [4, 8, 3]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 7／2着 1／3着 3；W False・P2 False・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "KNZ_05.r2", "ticket_sha256": "67bd4e40e0bd5558a5048d9c53e73921bb1eac84ded22b7bc468bf53d9044d7a", "frozen_at": "2026-11-23T15:10:06.752253+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 7／2着 1／3着 6；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "ef8976a2ff5a57a6d531a06cc3fa625e3360ebe839ba87237d3b0f273e38e6da", "result_receipt_sha256": "edb4f1f32d3c1209a4fa56410e94639d40aaff3b9c31e951c0e41513d1f9117a", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "9113d946097acb0eb58064128e2e1945958927472066e0efcd423ace27309e60", "signed_final_ticket_count": 105, "signed_final_total_investment": 10500, "signed_final_settlement": {"invest": 10500, "refund": 0, "effective_invest": 10500, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-23T06:47:14.047370+00:00", "source_receipt_sha256": "fc7dad566487d7cc1d6f94f96d1931418d0b586f716ff19ec7efc061db566445", "signed_final_at": "2026-11-23T06:47:24.640134+00:00", "delivered_ticket_sha256": "d22c6725f576fe8c6c71e998c7d3da1514a93eb50c7d4f3bad24edb630a22b3a", "settled_ticket_sha256": "ef8976a2ff5a57a6d531a06cc3fa625e3360ebe839ba87237d3b0f273e38e6da"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 7, "TPI-L": 7, "SRI-L": 7, "T3I-L": 8, "HPI-L": 7}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 7, "second_pre_rank": 1, "third_pre_rank": 6, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [4, 8, 3], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CONFIRMED"], "mi |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 7, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `e2864c1ae97c0764`／Learning State `8283b17bd3d4`</sub>
