# 2026-11-19 OHI_07 詳細反省（自動・実購入なし）

- 公式着順：6-9-1-10-4（上位3頭 [6, 9, 1]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 1／2着 6／3着 2；W True・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 1560／損益 860／PFS 222.9%
- 参照：{"revision": "OHI_07.r2", "ticket_sha256": "85cade4ce0a4c993fbbef2b92288799c1a86db5b71c5c64740185e47f2af98df", "frozen_at": "2026-11-19T17:00:13.235079+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 4／3着 1；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 5290／損益 -710／PFS 88.2%
- 参照：{"final_receipt_sha256": "fe96af83de02c89ac63d8b153ef6efb7e69cc7ab7f8d562f5ca17e27621a9b8a", "result_receipt_sha256": "fe5288cbeac901fd41c4b03143d7549a6dfc3344799cd9fbe24c59aa73280dfe", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "4ae30d45ba1f9b1f4e1d6a8630eabf35c5b96b3d2b46e427540faeb738cf8f4e", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 5290, "pfs": 33.9}, "effective_revision": "REVISION_2", "source_at": null, "signed_final_at": "2026-11-19T08:37:27.656687+00:00", "delivered_ticket_sha256": "161dd523a0adf0ad62e2af976a7ef9d1e7acb8d453b0c91b2a922feed54f400d", "settled_ticket_sha256": "fe96af83de02c89ac63d8b153ef6efb7e69cc7ab7f8d562f5ca17e27621a9b8a"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 2, "T3I-L": 1, "HPI-L": 2}, "ruled_neutral_share": 0.115} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（オールケアドリーム）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 4, "third_pre_rank": 1, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [6, 9, 1], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 88.2, "profit_loss": -710, "hit_but_loss": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 88.2, "tickets": 60, "payout": 5290} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `6bce1ccb4d224c95`／Learning State `5e445f1e08b3`</sub>
