# 2026-11-19 SON_10 詳細反省（自動・実購入なし）

- 公式着順：7-9-1-4-8（上位3頭 [7, 9, 1]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 1／2着 2／3着 3；W True・P2 True・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 400／損益 -300／PFS 57.1%
- 参照：{"revision": "SON_10.r2", "ticket_sha256": "040f97787d1ff3e9cdc0df98c38922fc963d76953c5e9114e43c8202b947178d", "frozen_at": "2026-11-19T14:35:01.583101+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 4／2着 3／3着 2；W False・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "b7954d010a6bd52c298a1b78d1121bbd918a98a7177116e58bb4f93b55444b59", "result_receipt_sha256": "8f7368055f1fb7773491701ad70991c34540531d87e9d34fde509ede16da7f48", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "84a94085ecc608220d895eff05397ecd8b3035ca332795b122da6992a3875c01", "signed_final_ticket_count": 120, "signed_final_total_investment": 12000, "signed_final_settlement": {"invest": 12000, "refund": 0, "effective_invest": 12000, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": null, "signed_final_at": "2026-11-19T06:12:18.760506+00:00", "delivered_ticket_sha256": "6478ab802fc078a81c3d82eacb9e3487330474adcc15a03edcadbba239da40fa", "settled_ticket_sha256": "b7954d010a6bd52c298a1b78d1121bbd918a98a7177116e58bb4f93b55444b59"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 4, "TPI-L": 3, "SRI-L": 3, "T3I-L": 4, "HPI-L": 6}, "ruled_neutral_share": 0.111} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 4, "second_pre_rank": 3, "third_pre_rank": 2, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [7, 9, 1], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CONFIRMED", "ORD |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": true, "ordered_exact_ticket_co |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 4, "alternative_signals_that_had_winner_top": ["PAPER ◎ was the winner"]} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `cccbbc00e4ded515`／Learning State `74aad8313e8f`</sub>
