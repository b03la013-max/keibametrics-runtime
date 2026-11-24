# 2026-11-24 MIZ_02 詳細反省（自動・実購入なし）

- 公式着順：8-2-1-3-4（上位3頭 [8, 2, 1]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 3／2着 4／3着 6；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "MIZ_02.r2", "ticket_sha256": "8a69c71d72755535ec0f1ba3f59aac104112311a7d1529b1f26a286cebb50841", "frozen_at": "2026-11-24T11:26:26.488811+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 6／2着 3／3着 7；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "9f0d0d6a2befdf4794b9df66d22193a9944d0b01267f465bf5f2126a9564144c", "result_receipt_sha256": "925ca5fc885d432d5df53bdcb15cd41c6be5400cf3628c3ea3a650887998ab05", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "9330a85c6aaaf2c8327b8a3b0f4f146bb174f650dc63c35c854e1652491ae9c3", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-24T03:04:20.601852+00:00", "source_receipt_sha256": "444beeae88b805f63dc6cf3623e03cacfe627e216757bd8afb865890e2c307ec", "signed_final_at": "2026-11-24T03:04:34.574665+00:00", "delivered_ticket_sha256": "224e4c032dab257e02df5236fce8136ca822e8e8acc88c35c7447f762a3b4bab", "settled_ticket_sha256": "9f0d0d6a2befdf4794b9df66d22193a9944d0b01267f465bf5f2126a9564144c"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 6, "TPI-L": 6, "SRI-L": 6, "T3I-L": 5, "HPI-L": 4}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 6, "second_pre_rank": 3, "third_pre_rank": 7, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [8, 2, 1], "rescues": ["WINNER_ROLE_RESCUE", "ORDERED_PAIR_RESCUE"], "sup |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 6, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `2482dfe6fc253ad1`／Learning State `70eddeb71476`</sub>
