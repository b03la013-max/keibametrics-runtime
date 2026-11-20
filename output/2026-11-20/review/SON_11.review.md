# 2026-11-20 SON_11 詳細反省（自動・実購入なし）

- 公式着順：8-1-5-7-4（上位3頭 [8, 1, 5]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 2／2着 3／3着 5；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "SON_11.r2", "ticket_sha256": "d1c50d41342a511153cb75fcaa3779aaf3e5d5d4a34af5de1ca6ff37a4263d98", "frozen_at": "2026-11-20T15:11:32.074567+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 7／2着 2／3着 5；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "9cfc446c26d7e6580adac6f0a8614a0555f1638fed89b3b87edb58a17cc4489b", "result_receipt_sha256": "f3e2c510fba2d18adc5eee3fe0a23ebe623c3a16202d633789d45c33f2e49200", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "6799be3043155a522cc62959a5b70da4c9913f4aaf74ba5f59c4ad650c8933c8", "signed_final_ticket_count": 144, "signed_final_total_investment": 14400, "signed_final_settlement": {"invest": 14400, "refund": 0, "effective_invest": 14400, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_1", "source_at": "2026-11-20T06:14:34.113588+00:00", "source_receipt_sha256": "784f8b460b19e51f2db54fcb8f562acb79034691edc6d085ce812f1e477043e2", "signed_final_at": "2026-11-20T06:14:43.278358+00:00", "delivered_ticket_sha256": "03737a944f6fe9d23132b7039aac367ca3b0711ef7448a2786e2863fbc269ee6", "settled_ticket_sha256": "9cfc446c26d7e6580adac6f0a8614a0555f1638fed89b3b87edb58a17cc4489b"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 4, "TPI-L": 3, "SRI-L": 6, "T3I-L": 8, "HPI-L": 6}, "ruled_neutral_share": 0.119} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 7, "second_pre_rank": 2, "third_pre_rank": 5, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [8, 1, 5], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CONF |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 7, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `fd930f1012a62553`／Learning State `0f41ab99b7b9`</sub>
