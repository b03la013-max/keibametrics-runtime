# 2026-11-27 SON_02 詳細反省（自動・実購入なし）

- 公式着順：7-4-9-3-6（上位3頭 [7, 4, 9]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 1／2着 3／3着 4；W True・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 470／損益 -230／PFS 67.1%
- 参照：{"revision": "SON_02.r2", "ticket_sha256": "9b6bf1a213d8d9b7d5badce2cd858bb99771f56c6146e50ff325c851e495e59b", "frozen_at": "2026-11-27T10:25:19.061830+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 3／3着 4；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 280／損益 -5720／PFS 4.7%
- 参照：{"final_receipt_sha256": "198a7d21162fcd79ad8427393b0835fcab633faf70c45910142f3a15d893f105", "result_receipt_sha256": "3aa996adeaae6dffd43a44848b089bfda5d034ae7991b413c1a79fafa163464d", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "b1ddb6ad0929f21420aa1de0304caf160971ddef475968b54b7c2b4726b60d4b", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 1230, "pfs": 9.3}, "effective_revision": "REVISION_2", "source_at": "2026-11-27T02:00:05.652094+00:00", "source_receipt_sha256": "6d7b3a800b6fd04025c16e9ffb4a0c600804ab30d158418816afa1374029d82b", "signed_final_at": "2026-11-27T02:00:16.802969+00:00", "delivered_ticket_sha256": "20cff283ff6dd260f7e416592c534011380d37c20529c1d696c1ae58b357faa3", "settled_ticket_sha256": "198a7d21162fcd79ad8427393b0835fcab633faf70c45910142f3a15d893f105"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 5, "TPI-L": 5, "SRI-L": 5, "T3I-L": 6, "HPI-L": 2}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 3, "third_pre_rank": 4, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [7, 4, 9], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 4.7, "profit_loss": -5720, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 4.7, "tickets": 60, "payout": 280} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `4bd03e1119b270be`／Learning State `5b2767883ded`</sub>
