# 2026-11-26 SON_12 詳細反省（自動・実購入なし）

- 公式着順：12-11-8-9-10（上位3頭 [12, 11, 8]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 6／2着 3／3着 1；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "SON_12.r2", "ticket_sha256": "edfb855b11866b2479c640cdb3a08286fa02f47071650b2e614ad04c5ede7694", "frozen_at": "2026-11-26T16:01:16.373051+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 6／2着 2／3着 3；W False・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 2350／損益 -3650／PFS 39.2%
- 参照：{"final_receipt_sha256": "1a027f83dbb9047293ad6288dda3d9ef6bc412396adc7c12b84b5e95536374a1", "result_receipt_sha256": "f9de25d5c3cfec3b4871d2ccc0b0fa6b0ae4e930d4e357357946f279698fe0a6", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "a3964e7248ae6696585e9abcd1edff404401746a138451172a4071ddc2e5dba6", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-26T07:36:15.602730+00:00", "source_receipt_sha256": "4f65d93d89225f89536e3667c4af96dfd1eab49f03136235551fd1152bfa9a5d", "signed_final_at": "2026-11-26T07:36:27.939776+00:00", "delivered_ticket_sha256": "28cbff4feaf1e3bba6af9259f70215ca33f260bd469380539e423f9388089def", "settled_ticket_sha256": "1a027f83dbb9047293ad6288dda3d9ef6bc412396adc7c12b84b5e95536374a1"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 6, "TPI-L": 6, "SRI-L": 6, "T3I-L": 7, "HPI-L": 6}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 6, "second_pre_rank": 2, "third_pre_rank": 3, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [12, 11, 8], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CO |
| TICKET | OK | {"head_local_p2": null, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cov |
| CAPITAL | ISSUE | {"pfs": 39.2, "profit_loss": -3650, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 6, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P1:HIT_BUT_LOSS | P1 | {"pfs": 39.2, "tickets": 60, "payout": 2350} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `c2ea9e338e97cb2a`／Learning State `1a2d2ea5f99b`</sub>
