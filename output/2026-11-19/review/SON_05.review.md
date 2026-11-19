# 2026-11-19 SON_05 詳細反省（自動・実購入なし）

- 公式着順：11-7-12-4-9（上位3頭 [11, 7, 12]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 7／2着 9／3着 8；W False・P2 False・P3 False
- Top3捕捉 0／Top4捕捉 0；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "SON_05.r2", "ticket_sha256": "fc50b0065bbf164092218a3a6d882008b24c2dc698da77627312870c7182e20a", "frozen_at": "2026-11-19T11:55:11.834475+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 10／2着 4／3着 7；W False・P2 True・P3 True
- Top3捕捉 0／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "32bfdd91bb0e7f80f9bfebfbae24b5b7e74450207a3b93cd03612193cc31ecef", "result_receipt_sha256": "3d0088c1db6f11b23b2dfe3dbb64a0414ea839b3fb61b72cd80921cd19b3f196", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "2b5fc12be55a3264745665610d4bc54ef177bceb00586d5edccb9ed27f776248", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_1", "source_at": null, "signed_final_at": "2026-11-19T02:56:43.003506+00:00", "delivered_ticket_sha256": "1c51363ded6a66507c76ecc552712400ea8af3d9faf628a2056b3a3f61f7c5ed", "settled_ticket_sha256": "32bfdd91bb0e7f80f9bfebfbae24b5b7e74450207a3b93cd03612193cc31ecef"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 10, "TPI-L": 10, "SRI-L": 10, "T3I-L": 11, "HPI-L": 10}, "ruled_neutral_share": 0.118} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 10, "second_pre_rank": 4, "third_pre_rank": 7, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [11, 7, 12], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CONFIRMED"], " |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 10, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `86e810a38996bfce`／Learning State `7c21faac849f`</sub>
