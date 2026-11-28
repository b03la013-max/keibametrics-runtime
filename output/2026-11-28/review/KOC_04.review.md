# 2026-11-28 KOC_04 詳細反省（自動・実購入なし）

- 公式着順：6-4-5-3-7（上位3頭 [6, 4, 5]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 3／2着 5／3着 1；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 800／返還 0／払戻 0／損益 -800／PFS 0.0%
- 参照：{"revision": "KOC_04.r2", "ticket_sha256": "9d68188f4adf93146648a379d44ab1eec3373be5fc096d8835859f6f1d286a5b", "frozen_at": "2026-11-28T15:50:17.526484+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 4／2着 3／3着 1；W False・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "38a67c70eb1412013c6e9ada224230fa259b7a708384d48aac505c4738fb0345", "result_receipt_sha256": "8a594936c3fbd69ab9d6d4c74a1ce24b92ee0a453ffd91809971da9a644b3ce5", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "37d042b0fe5ed147cf6b61908bc4d4ecc6d4ec70e0aed9ca9478393b740b5ddd", "signed_final_ticket_count": 105, "signed_final_total_investment": 10500, "signed_final_settlement": {"invest": 10500, "refund": 0, "effective_invest": 10500, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-28T07:27:16.695313+00:00", "source_receipt_sha256": "5732e302bc4755ab66d58fc46b043fb2539e5b30d6272169e96b845d8baed5fc", "signed_final_at": "2026-11-28T07:27:26.696021+00:00", "delivered_ticket_sha256": "6bc5c25e972340c4a487832254d89720df60eca57f90e53219b7941fb593e16d", "settled_ticket_sha256": "38a67c70eb1412013c6e9ada224230fa259b7a708384d48aac505c4738fb0345"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 4, "TPI-L": 4, "SRI-L": 4, "T3I-L": 4, "HPI-L": 5}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 4, "second_pre_rank": 3, "third_pre_rank": 1, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [6, 4, 5], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CONFIRMED"], "mi |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 4, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `87490c63ea9a2b1a`／Learning State `91a4df6e3e5f`</sub>
