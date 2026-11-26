# 2026-11-26 NGY_05 詳細反省（自動・実購入なし）

- 公式着順：11-12-6-2-4（上位3頭 [11, 12, 6]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 2／2着 1／3着 3；W False・P2 False・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 1290／損益 590／PFS 184.3%
- 参照：{"revision": "NGY_05.r2", "ticket_sha256": "3988211ac88e691d6dd8b3639bac987cf64d350bd43460f9cbc0a2cd04e241d5", "frozen_at": "2026-11-26T16:15:12.414635+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 5／3着 2；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 5670／損益 -330／PFS 94.5%
- 参照：{"final_receipt_sha256": "4a8e6c4ced0bfe5945a9bf59658749b40c76f7410815d59f5581eba96ec8625c", "result_receipt_sha256": "6f9ed24c1af225d8da23ccbac04b651d9ec3de66392c703662c74e9fb5450fc3", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "c1e812f902333c724d1d6e6d4bb69463bce90120edf156c893d211d8e15fb9b1", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 4620, "pfs": 29.6}, "effective_revision": "REVISION_2", "source_at": "2026-11-26T07:50:06.561977+00:00", "source_receipt_sha256": "99859dcbda27d77b422c1481c4d7fdfd51b911cc10d889dab6769705e78a7a89", "signed_final_at": "2026-11-26T07:50:20.012828+00:00", "delivered_ticket_sha256": "eca82c625b455faa74361bc82d7379e357cd666624433b4cd0ab27cc40fab08b", "settled_ticket_sha256": "4a8e6c4ced0bfe5945a9bf59658749b40c76f7410815d59f5581eba96ec8625c"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 1, "HPI-L": 2}, "ruled_neutral_share": 0.072} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 5, "third_pre_rank": 2, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [11, 12, 6], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P3_ROL |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 94.5, "profit_loss": -330, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 94.5, "tickets": 60, "payout": 5670} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `27cdbb0a8d6bba30`／Learning State `f51f9906c9e5`</sub>
