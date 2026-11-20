# 2026-11-20 KSM_12 詳細反省（自動・実購入なし）

- 公式着順：2-8-9-4-3（上位3頭 [2, 8, 9]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_P2**
- 正しく判断できた項目：winner_in_W, third_in_P3, winner_is_ticket_head

## PAPER

- 1着の事前順位 1／2着 9／3着 4；W True・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "KSM_12.r2", "ticket_sha256": "172fc09ef178a72f0c43e9014daae5914254700907d1d450c713fc916bc47a89", "frozen_at": "2026-11-20T15:31:24.531887+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 9／3着 2；W True・P2 False・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 False；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "bf2ead336b62cd0607755ce73aeb4bf72895b6ec8fe93967fb7bfeee9517d647", "result_receipt_sha256": "ed0b9b709944325ebd8952e0131d61e0e258d8642d9b8f60c911e1daaa9b01be", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "782903db27811a69b93350488c5d461f164979eb52d68efb05b3b5785f418d29", "signed_final_ticket_count": 120, "signed_final_total_investment": 12000, "signed_final_settlement": {"invest": 12000, "refund": 0, "effective_invest": 12000, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_1", "source_at": "2026-11-20T06:34:46.997255+00:00", "source_receipt_sha256": "f46d606de82b0fb88d9b53ba6a3d66d9ad2d50f88406861b26a13e904add870c", "signed_final_at": "2026-11-20T06:34:54.980867+00:00", "delivered_ticket_sha256": "c8a2c2c96afa986d79a368803c4b24493f3d7595b5e37a7b2399a5bcc05c3673", "settled_ticket_sha256": "bf2ead336b62cd0607755ce73aeb4bf72895b6ec8fe93967fb7bfeee9517d647"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 1, "HPI-L": 3}, "ruled_neutral_share": 0.119} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 1, "second_pre_rank": 9, "third_pre_rank": 2, "winner_in_W": true, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [2, 8, 9], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P3_ROLE_CONFIRMED"], |
| TICKET | ISSUE | {"head_local_p2": false, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 9} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `976da7a91860dfa6`／Learning State `141b9d48f60e`</sub>
