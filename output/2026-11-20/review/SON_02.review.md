# 2026-11-20 SON_02 詳細反省（自動・実購入なし）

- 公式着順：1-2-3-6-5（上位3頭 [1, 2, 3]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 1／2着 4／3着 2；W True・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 740／損益 40／PFS 105.7%
- 参照：{"revision": "SON_02.r2", "ticket_sha256": "0b791d5ffc63fd1c6f25ca0a91a3ac365200eb12c0608680b23e3a6e8aeb97d1", "frozen_at": "2026-11-20T10:25:52.113200+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 6／3着 5；W True・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 430／損益 -5570／PFS 7.2%
- 参照：{"final_receipt_sha256": "a8decd483e815bf9ff93d4fce3e2330e563713805d8cf37635fa9b16d58d7a9b", "result_receipt_sha256": "3037de24c2ca5a4cd37f7eb88a5329c43eb3766931a905fef85af5f936aeb33a", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "860ff0fa061e5b0c47e2bbe22354faca486a65780e1b19d204e4b4709cb4d5ed", "signed_final_ticket_count": 75, "signed_final_total_investment": 7500, "signed_final_settlement": {"invest": 7500, "refund": 0, "effective_invest": 7500, "payout": 2150, "pfs": 28.7}, "effective_revision": "REVISION_2", "source_at": "2026-11-20T02:00:55.263690+00:00", "source_receipt_sha256": "14f6fdd8b6997ee12a4c8d6ca34543322831a852e978d7a33d8845dd59a2ffcd", "signed_final_at": "2026-11-20T02:01:01.701887+00:00", "delivered_ticket_sha256": "cb0945f1b903e8ffbf49715d8abd2b0db12399ed63e2f821e1d41e23c81f3eff", "settled_ticket_sha256": "a8decd483e815bf9ff93d4fce3e2330e563713805d8cf37635fa9b16d58d7a9b"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 3, "SRI-L": 3, "T3I-L": 3, "HPI-L": 6}, "ruled_neutral_share": 0.414} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（マダムココ）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 6, "third_pre_rank": 5, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [1, 2, 3], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_CONFIRMED",  |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 7.2, "profit_loss": -5570, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 7.2, "tickets": 60, "payout": 430} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | {"ruled_neutral_share": 0.414} | ruled-neutral share falls below 15% without source changes | per-venue observation rate in forward_summary | CALCULATED share |

<sub>review sha256 `2d3013345e60ff5d`／Learning State `3d09011f1621`</sub>
