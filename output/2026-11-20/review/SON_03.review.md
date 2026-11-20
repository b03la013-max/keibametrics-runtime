# 2026-11-20 SON_03 詳細反省（自動・実購入なし）

- 公式着順：8-1-7-3-4（上位3頭 [8, 1, 7]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 4／2着 1／3着 3；W False・P2 False・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 1180／損益 480／PFS 168.6%
- 参照：{"revision": "SON_03.r2", "ticket_sha256": "0910bc85205c799b5ac3cffff26fd04e87796b49cfe007c8aa6671a3ad4f6252", "frozen_at": "2026-11-20T10:56:20.980744+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 6／3着 4；W True・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 3450／損益 -2550／PFS 57.5%
- 参照：{"final_receipt_sha256": "18f7867d3bf2891b8d89276cfa51f7a53a784744a4e40b7936a6ece441c028bc", "result_receipt_sha256": "cfdef2685c8509abc111bfde9ea8dd4f6c6e849b09fe29f79438cac167b8e4ee", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "5b8fe79b6d54962011c77c205c1730ab02d8bd47a26fd63a72022ca208e19cc8", "signed_final_ticket_count": 105, "signed_final_total_investment": 10500, "signed_final_settlement": {"invest": 10500, "refund": 0, "effective_invest": 10500, "payout": 13270, "pfs": 126.4}, "effective_revision": "REVISION_1", "source_at": "2026-11-20T01:58:41.870728+00:00", "source_receipt_sha256": "6d07300e8eba5ee057f3dfe76b54b846876dbc8017846499632adfd48e1f4939", "signed_final_at": "2026-11-20T01:58:49.235473+00:00", "delivered_ticket_sha256": "25f12a3f2fc00c9b91a52a90d198ed2f789a0999140c5725caf8f5d533e5f3ff", "settled_ticket_sha256": "18f7867d3bf2891b8d89276cfa51f7a53a784744a4e40b7936a6ece441c028bc"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 3, "SRI-L": 2, "T3I-L": 3, "HPI-L": 4}, "ruled_neutral_share": 0.112} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（ロミヒ）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 6, "third_pre_rank": 4, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [8, 1, 7], "rescues": [], "supports": ["P3_ROLE_CONFIRMED"], "misses": [" |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 57.5, "profit_loss": -2550, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 57.5, "tickets": 60, "payout": 3450} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `2afc657186746ceb`／Learning State `5f234a5789f4`</sub>
