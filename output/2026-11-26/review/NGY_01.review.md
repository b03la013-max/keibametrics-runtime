# 2026-11-26 NGY_01 詳細反省（自動・実購入なし）

- 公式着順：3-2-11-7-4（上位3頭 [3, 2, 11]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 4／2着 1／3着 3；W False・P2 False・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 560／損益 -140／PFS 80.0%
- 参照：{"revision": "NGY_01.r2", "ticket_sha256": "50e4a5591ff73573aae8c3f764028e2e8cf57380bb7dfe3c7dbe89b70a63ec14", "frozen_at": "2026-11-26T13:55:15.662798+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 8／2着 2／3着 5；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "2574c98b287a054ceb9add9628b7fd96693249e0ae2da97d1a4a29fdbbd27bdd", "result_receipt_sha256": "5f44edd73038cebfea952b1cbcfcae9246f5a7aa2aac272119aa4b320fb1e277", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "c32e4a32ad0dd5ff8ca39622c2f3c4210eb0cf46ca3722dda9d3d2d418cc0679", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-26T05:32:21.478468+00:00", "source_receipt_sha256": "e9786ca5bef35c31f593a8b755bc2aeb67f34e7abec8b5ca7c2e62455c3a90d9", "signed_final_at": "2026-11-26T05:32:34.874870+00:00", "delivered_ticket_sha256": "99852fb83513ab9068410d7496aebd48b7f543f842b4bfeb1d67f6d471eacb02", "settled_ticket_sha256": "2574c98b287a054ceb9add9628b7fd96693249e0ae2da97d1a4a29fdbbd27bdd"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 5, "TPI-L": 5, "SRI-L": 7, "T3I-L": 11, "HPI-L": 4}, "ruled_neutral_share": 0.075} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（チャーチルデュース）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 8, "second_pre_rank": 2, "third_pre_rank": 5, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [3, 2, 11], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CON |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 8, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `9bf3de1471eb9edd`／Learning State `71b5dee75159`</sub>
