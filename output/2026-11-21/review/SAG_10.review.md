# 2026-11-21 SAG_10 詳細反省（自動・実購入なし）

- 公式着順：10-7-6-5-1（上位3頭 [10, 7, 6]）
- 距離帯：MIDDLE(1701-2100)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 3／2着 1／3着 10；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "SAG_10.r2", "ticket_sha256": "1d7ab6c485a7447e5811484ca79ffa16a15062d5870ec585513224e944127054", "frozen_at": "2026-11-21T19:25:18.779437+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 3／2着 2／3着 7；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 2150／損益 -3850／PFS 35.8%
- 参照：{"final_receipt_sha256": "9375369661500b7b9b1c5f7668b9ae2f119616a03964a8b42d14d82309755765", "result_receipt_sha256": "f3f04c9a69a1d5c427b1c1728a1ba022a28f994a1439c0563403e95ed45d64e7", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "7585481b27756f90f6ffa01ffb6815501399c3c639509a52c234a8cfb5aff111", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 20880, "pfs": 158.2}, "effective_revision": "REVISION_2", "source_at": "2026-11-21T11:00:20.602471+00:00", "source_receipt_sha256": "50c0cd51607048227b4f98f4861c8f4695ef270e7ee9aadfa068956e3a01fb04", "signed_final_at": "2026-11-21T11:00:29.432120+00:00", "delivered_ticket_sha256": "a1c939c33e528fcd54b0d56b83648b575648985f15d603c2d5d54e0be06253ca", "settled_ticket_sha256": "9375369661500b7b9b1c5f7668b9ae2f119616a03964a8b42d14d82309755765"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 1, "HPI-L": 1}, "ruled_neutral_share": 0.117} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（ウインポラリス）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 3, "second_pre_rank": 2, "third_pre_rank": 7, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [10, 7, 6], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 35.8, "profit_loss": -3850, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 35.8, "tickets": 60, "payout": 2150} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `6ca18fa9ddfd149a`／Learning State `884f9c04078b`</sub>
