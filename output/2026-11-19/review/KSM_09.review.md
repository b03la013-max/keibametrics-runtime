# 2026-11-19 KSM_09 詳細反省（自動・実購入なし）

- 公式着順：8-6-9-1-2（上位3頭 [8, 6, 9]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 2／2着 1／3着 4；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 280／損益 -420／PFS 40.0%
- 参照：{"revision": "KSM_09.r2", "ticket_sha256": "f37d18d54ec9574b83191ed19cf99128916440efcf8457dbf41ba93b226fd8b8", "frozen_at": "2026-11-19T13:50:11.613831+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 1／3着 4；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 640／損益 -5360／PFS 10.7%
- 参照：{"final_receipt_sha256": "d6a2d7fc78644a180ac450023f66be8d6bcf81968a48a4faa916acf497bcc726", "result_receipt_sha256": "361d4fe96d83983fc378c68b69cd1365d84b073f2092b052d10e9f2d1ba300c0", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "8a8506bba8b46c84ac401e7bfdcbc208669e99593d0deb30f0e7e2abdf121e95", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 640, "pfs": 4.8}, "effective_revision": "REVISION_1", "source_at": null, "signed_final_at": "2026-11-19T04:52:42.025296+00:00", "delivered_ticket_sha256": "156862732267c0a4cf4daf6c1c328cdf4ac2a2e62843b89ccb50cc9dcc524fa6", "settled_ticket_sha256": "d6a2d7fc78644a180ac450023f66be8d6bcf81968a48a4faa916acf497bcc726"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 2, "T3I-L": 2, "HPI-L": 1}, "ruled_neutral_share": 0.11} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（リモート）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 1, "third_pre_rank": 4, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [8, 6, 9], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_CONFIRMED",  |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 10.7, "profit_loss": -5360, "hit_but_loss": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 10.7, "tickets": 60, "payout": 640} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `e11d8e9997fdd553`／Learning State `fd286129d24a`</sub>
