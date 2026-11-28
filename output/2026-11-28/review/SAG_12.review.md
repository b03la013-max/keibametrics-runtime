# 2026-11-28 SAG_12 詳細反省（自動・実購入なし）

- 公式着順：1-6-10-11-2（上位3頭 [1, 6, 10]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 5／2着 11／3着 9；W False・P2 False・P3 False
- Top3捕捉 0／Top4捕捉 0；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "SAG_12.r2", "ticket_sha256": "c84726de5b8edb89313c86cb879d5fb0921489ec659d4a44cf0371ceaeb7dbf1", "frozen_at": "2026-11-28T19:55:10.996095+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 11／2着 2／3着 6；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 560／損益 -5440／PFS 9.3%
- 参照：{"final_receipt_sha256": "f9ac9b5a064e66b2767e52476d6db021e7771d8891db8d54347db36277f64026", "result_receipt_sha256": "c96afab23e47493f40700c12928b1a4c406dfeee01196fff7711dfcc6bf59a7d", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "d78cf8a434309f8d14a7fa2b106ac2f0ab1fc8deedf79e4e5fc039af7ef00112", "signed_final_ticket_count": 168, "signed_final_total_investment": 16800, "signed_final_settlement": {"invest": 16800, "refund": 0, "effective_invest": 16800, "payout": 2090, "pfs": 12.4}, "effective_revision": "REVISION_2", "source_at": "2026-11-28T11:31:22.102103+00:00", "source_receipt_sha256": "a38cdec2f21fcff614fe28d109d9dff375012585fda8f19f6c3abd3ec62ffffb", "signed_final_at": "2026-11-28T11:31:36.813710+00:00", "delivered_ticket_sha256": "258aaf057e0a7028c90de6cab66333c4146af8d609cd034b3fe8ca73630bcb42", "settled_ticket_sha256": "f9ac9b5a064e66b2767e52476d6db021e7771d8891db8d54347db36277f64026"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 9, "TPI-L": 8, "SRI-L": 10, "T3I-L": 11, "HPI-L": 6}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 11, "second_pre_rank": 2, "third_pre_rank": 6, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [1, 6, 10], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CON |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 9.3, "profit_loss": -5440, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 11, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P1:HIT_BUT_LOSS | P1 | {"pfs": 9.3, "tickets": 60, "payout": 560} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `2f50a1c250eadf52`／Learning State `9dab5af100c6`</sub>
