# 2026-11-26 NGY_12 詳細反省（自動・実購入なし）

- 公式着順：10-5-1-4-6（上位3頭 [10, 5, 1]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 4／2着 2／3着 8；W False・P2 True・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "NGY_12.r2", "ticket_sha256": "a623847200cf53ec90f04e5a0d7fe2b5b9d3acf72021a88ff312b35de9978c4e", "frozen_at": "2026-11-26T20:05:10.010601+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 8／2着 6／3着 12；W False・P2 True・P3 True
- Top3捕捉 0／Top4捕捉 0；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "dcfa01072878f9813ff43df94a3cad4f4d32464a0e449b3bd5fcb1f5986de484", "result_receipt_sha256": "546932c7c3eb864fc4f97a4de7cb7f3b905393d5f3f4d6bda9945d4540489cd8", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "e3ad25a32e8091e004aeedadee74e4c099af4183002f333eb5fd352df8f7cfdb", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-26T11:41:11.473851+00:00", "source_receipt_sha256": "15a9b8514fbc2180b5b16780f08b5bed3bc398e0de5a0edfe3ce57c5305ba693", "signed_final_at": "2026-11-26T11:41:25.305806+00:00", "delivered_ticket_sha256": "65eeca766793565ec5a46e574d3e76535b03faba9930fe051b414e8b02b755a6", "settled_ticket_sha256": "dcfa01072878f9813ff43df94a3cad4f4d32464a0e449b3bd5fcb1f5986de484"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 10, "TPI-L": 10, "SRI-L": 10, "T3I-L": 11, "HPI-L": 3}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 8, "second_pre_rank": 6, "third_pre_rank": 12, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [10, 5, 1], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "ORDERED_PAI |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 8, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `d6b93c502ff488dd`／Learning State `27e7ec97f4d0`</sub>
