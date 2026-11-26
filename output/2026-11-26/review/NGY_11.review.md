# 2026-11-26 NGY_11 詳細反省（自動・実購入なし）

- 公式着順：8-11-9-5-7（上位3頭 [8, 11, 9]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 5／2着 3／3着 6；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "NGY_11.r2", "ticket_sha256": "26e9eec77915cdd48cbb38c5c8187cb224336d50f75c26e96acf1119da9f7fa8", "frozen_at": "2026-11-26T19:30:16.277865+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 7／2着 3／3着 4；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "435f52e1be0349bf5826bc22b193b56bfa0d5096e99ddc2020b8e14f5ee0cb28", "result_receipt_sha256": "d22748fa75f8392674ebb5540d437c7ede5dd5c68c4202f2de3bde07b04905bd", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "5ba31c659b615022a565a0c0d7a693a7a40c72ef0d99636fcb402c4bf700b2c2", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-26T11:07:11.774600+00:00", "source_receipt_sha256": "106887b81431296e8b363d6335b750fbb4d2d0a99230908ec4f246b912e8a366", "signed_final_at": "2026-11-26T11:07:26.419577+00:00", "delivered_ticket_sha256": "2b0df779b4ca3309a966d9c2b587ec19d93f40fac0cd7a1456ef3b6f0949a7a9", "settled_ticket_sha256": "435f52e1be0349bf5826bc22b193b56bfa0d5096e99ddc2020b8e14f5ee0cb28"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 9, "TPI-L": 9, "SRI-L": 9, "T3I-L": 9, "HPI-L": 9}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 7, "second_pre_rank": 3, "third_pre_rank": 4, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [8, 11, 9], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CON |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 7, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `1a6ac9c89f000a29`／Learning State `f4cfdc577d21`</sub>
