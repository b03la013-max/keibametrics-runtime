# 2026-11-25 SON_07 詳細反省（自動・実購入なし）

- 公式着順：6-4-5-2-7（上位3頭 [6, 4, 5]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 1／2着 6／3着 2；W True・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 False；Pair条件付き3着 True
- 投資 1600／返還 0／払戻 2290／損益 690／PFS 143.1%
- 参照：{"revision": "SON_07.r2", "ticket_sha256": "3b94c3cb235828b1972d6b74013a29a2b5d5e3f196d0303850fc9cc249a0f2d4", "frozen_at": "2026-11-25T13:15:13.643593+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 4／2着 6／3着 1；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 2290／損益 -3710／PFS 38.2%
- 参照：{"final_receipt_sha256": "eae1505f76bba334a5924f0887fa8dfea6b94b7eabdae32d4069f43f26f3d0f2", "result_receipt_sha256": "5db293b8355ba2ebc9f21b0800986b8e78196fb2383b23f4871ba1a53dd68c54", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "644a527226dd576a5eb072079ee262e3dc72f94a28dc8b86fb92751eef419b85", "signed_final_ticket_count": 90, "signed_final_total_investment": 9000, "signed_final_settlement": {"invest": 9000, "refund": 0, "effective_invest": 9000, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-25T04:50:12.194973+00:00", "source_receipt_sha256": "5d73c4908336f640eadb9c3719c0ea38bef2939584df25ccc0e353f36f2d9e5a", "signed_final_at": "2026-11-25T04:50:21.619925+00:00", "delivered_ticket_sha256": "88661a32bfa340bc67b339a65c935742b937ff57579273e022bece3cd42d0178", "settled_ticket_sha256": "eae1505f76bba334a5924f0887fa8dfea6b94b7eabdae32d4069f43f26f3d0f2"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 1, "SRI-L": 5, "T3I-L": 7, "HPI-L": 1}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（バフランティ）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 4, "second_pre_rank": 6, "third_pre_rank": 1, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [6, 4, 5], "rescues": ["WINNER_ROLE_RESCUE", "ORDERED_PAIR_RESCUE", "PAIR |
| TICKET | OK | {"head_local_p2": null, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cov |
| CAPITAL | ISSUE | {"pfs": 38.2, "profit_loss": -3710, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 4, "alternative_signals_that_had_winner_top": ["PAPER ◎ was the winner", "TPI-L ranked the winner #1 | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P1:HIT_BUT_LOSS | P1 | {"pfs": 38.2, "tickets": 60, "payout": 2290} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `b9d639446beba6b9`／Learning State `71fba0ab6d00`</sub>
