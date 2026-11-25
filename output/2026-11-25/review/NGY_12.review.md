# 2026-11-25 NGY_12 詳細反省（自動・実購入なし）

- 公式着順：8-10-12-6-4（上位3頭 [8, 10, 12]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 5／2着 6／3着 1；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "NGY_12.r2", "ticket_sha256": "291544ce23bb5360cafc44f6c28621ec520db0b8700095852c5b1cb740f27243", "frozen_at": "2026-11-25T20:05:04.659066+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 8／2着 5／3着 3；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "9c41c242058f8cf29d67ecf66dab51b4409493a6188fe4c74e835cc94cf6f32c", "result_receipt_sha256": "184c0eed441e20c84680fe9202089500f1551e18f473d2d20c1c53b453f0a8b1", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "280dc4f65b4470002f397479484d563ec0c6b2ae57888f7c585d10557ed022c7", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-25T11:41:06.639383+00:00", "source_receipt_sha256": "2f2cd3ea1fb3a5b0d39c669fe118924e4e620b1dad8212b55d16a05923567308", "signed_final_at": "2026-11-25T11:41:20.456093+00:00", "delivered_ticket_sha256": "6c4b8982a85675ceb1d9b65c3258de46390e84dc2b6502a0ab024e5235fdf382", "settled_ticket_sha256": "9c41c242058f8cf29d67ecf66dab51b4409493a6188fe4c74e835cc94cf6f32c"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 9, "TPI-L": 8, "SRI-L": 9, "T3I-L": 8, "HPI-L": 9}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 8, "second_pre_rank": 5, "third_pre_rank": 3, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [8, 10, 12], "rescues": [], "supports": ["P3_ROLE_CONFIRMED"], "misses":  |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 8, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `3cd70f7ccfd6e764`／Learning State `9bd824c04bd0`</sub>
