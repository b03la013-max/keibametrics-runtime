# 2026-11-27 SON_10 詳細反省（自動・実購入なし）

- 公式着順：10-2-8-11-6（上位3頭 [10, 2, 8]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 8／2着 1／3着 7；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 2880／損益 2180／PFS 411.4%
- 参照：{"revision": "SON_10.r2", "ticket_sha256": "b6fbd91f7c09bf658f69fab6801b1e3bea8525334f49c0e7c06096ade4042934", "frozen_at": "2026-11-27T14:50:15.865322+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 6／2着 2／3着 8；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "1d3fbff1565edd39ad9ce67b062bed5081f72f938c381d1274829602a0423f46", "result_receipt_sha256": "d41cfe7caeb2f20f7e50bfbcead608962367fb2e41a27a1f0d0061682c8315a6", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "3a3dd054a8c1f924646fbdc9fd6ac239677c06a0a4e851539e0b35539bd2c9c8", "signed_final_ticket_count": 144, "signed_final_total_investment": 14400, "signed_final_settlement": {"invest": 14400, "refund": 0, "effective_invest": 14400, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-27T06:27:17.830916+00:00", "source_receipt_sha256": "1c4934bf1d4aee5704c4f8d10fb5272b51898c70f89194e681f5aa48b8dcc246", "signed_final_at": "2026-11-27T06:27:29.776084+00:00", "delivered_ticket_sha256": "cc2d241e0cef4edfd29a6174289ce81b78f89223aa21e19bb65871b1a8da0d5a", "settled_ticket_sha256": "1d3fbff1565edd39ad9ce67b062bed5081f72f938c381d1274829602a0423f46"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 5, "TPI-L": 5, "SRI-L": 6, "T3I-L": 6, "HPI-L": 3}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 6, "second_pre_rank": 2, "third_pre_rank": 8, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [10, 2, 8], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CON |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 6, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `f7a38e5497b80549`／Learning State `848c3aac23f0`</sub>
