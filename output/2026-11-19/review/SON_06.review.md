# 2026-11-19 SON_06 詳細反省（自動・実購入なし）

- 公式着順：5-9-3-8-4（上位3頭 [5, 9, 3]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 1／2着 4／3着 5；W True・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 False；Pair条件付き3着 None
- 投資 800／返還 0／払戻 160／損益 -640／PFS 20.0%
- 参照：{"revision": "SON_06.r2", "ticket_sha256": "241074e61bc2e0e5f8aac49c88e6d46eb36d3ed489b548655beeba1eca7545e6", "frozen_at": "2026-11-19T12:25:05.572266+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 4／3着 6；W True・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 320／損益 -5680／PFS 5.3%
- 参照：{"final_receipt_sha256": "790bca3f79b87989da75338b283c17a4a95f459459640e18ffbc5de71017966c", "result_receipt_sha256": "af201af663ba51d4dcab83add9b8b8080c7e4f14014c062c404e131361988f80", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "0548b97757684008bbe3200c8fdae0d94c31924c4e8e179f9b9db66e5dd6d89d", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 1290, "pfs": 8.3}, "effective_revision": "REVISION_1", "source_at": null, "signed_final_at": "2026-11-19T03:26:36.063817+00:00", "delivered_ticket_sha256": "b3df3615223b403303b915d04dc1f39696f7246783b6f173b07b6cfe365f91c9", "settled_ticket_sha256": "790bca3f79b87989da75338b283c17a4a95f459459640e18ffbc5de71017966c"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 1, "HPI-L": 1}, "ruled_neutral_share": 0.118} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 4, "third_pre_rank": 6, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [5, 9, 3], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_co |
| CAPITAL | ISSUE | {"pfs": 5.3, "profit_loss": -5680, "hit_but_loss": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 5.3, "tickets": 60, "payout": 320} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `4f8457af2fe7aaf4`／Learning State `14873842933d`</sub>
