# 2026-11-21 SAG_11 詳細反省（自動・実購入なし）

- 公式着順：11-4-12-9-7（上位3頭 [11, 4, 12]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：third_in_P3

## PAPER

- 1着の事前順位 1／2着 7／3着 9；W True・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 2780／損益 2080／PFS 397.1%
- 参照：{"revision": "SAG_11.r2", "ticket_sha256": "01a7f6549a3b862499d42044d16be0a1066f6fced1eb6baeccbbcfb61b156ee5", "frozen_at": "2026-11-21T19:55:13.870497+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 6／2着 13／3着 7；W False・P2 False・P3 True
- Top3捕捉 0／Top4捕捉 0；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "5d6b4aa66a53c002a12043f2c149e43dfd04e8b4d4f623cc2721181477b3db04", "result_receipt_sha256": "46e635c44ae8554834a94841b241a0ddd63379dc030e4cc648884cd112ec44d7", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "c1243acee23358ef99bd49af407a04acdbb4bf0313e4754ea7358a12a2d98650", "signed_final_ticket_count": 180, "signed_final_total_investment": 18000, "signed_final_settlement": {"invest": 18000, "refund": 0, "effective_invest": 18000, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_1", "source_at": "2026-11-21T10:56:35.860405+00:00", "source_receipt_sha256": "6eadaba946e5a4d447952ff394eff0a6d224b90e06fa81335447ef36d880680a", "signed_final_at": "2026-11-21T10:56:47.072976+00:00", "delivered_ticket_sha256": "9dc9099428e311f2661278bb29c445f72d09c0979bea679e184ac10a78f9509f", "settled_ticket_sha256": "5d6b4aa66a53c002a12043f2c149e43dfd04e8b4d4f623cc2721181477b3db04"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 3, "T3I-L": 4, "HPI-L": 2}, "ruled_neutral_share": 0.116} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 6, "second_pre_rank": 13, "third_pre_rank": 7, "winner_in_W": false, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [11, 4, 12], "rescues": ["WINNER_ROLE_RESCUE"], "supports": ["P3_ROLE_CON |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 6, "alternative_signals_that_had_winner_top": ["PAPER ◎ was the winner"]} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `2f3368ec38e4b15a`／Learning State `19ae87eaad80`</sub>
