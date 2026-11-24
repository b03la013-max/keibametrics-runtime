# 2026-11-24 NGY_03 詳細反省（自動・実購入なし）

- 公式着順：3-5-4-6-8（上位3頭 [3, 5, 4]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 5／2着 1／3着 2；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 1790／損益 1090／PFS 255.7%
- 参照：{"revision": "NGY_03.r2", "ticket_sha256": "fbf67ae5135c36e570a731c23ff50e300333e926572104f5c32cd47d00a24359", "frozen_at": "2026-11-24T14:51:21.865751+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 6／2着 1／3着 2；W False・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 1290／損益 -4710／PFS 21.5%
- 参照：{"final_receipt_sha256": "f5cf7bf81f50aaa5c3223ca29ac5fb735e0de8d77606b7edbc1450ace871ca57", "result_receipt_sha256": "1a567c5fed0d2ffddc0336426b1ef7b19755d4353d9a3581eaea1e96e61013e2", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "13a85eb02ca5f06595df0aa9e1da765022853329a345a9a2fb98ff77a4b1ef68", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-24T06:27:12.883355+00:00", "source_receipt_sha256": "a38ed4a501b499fa003c94b024441ce3ca6c7103323dabd26c651e3cce68d414", "signed_final_at": "2026-11-24T06:27:28.261635+00:00", "delivered_ticket_sha256": "ee9fb672d7ddbea554d19ac87376618abb27fe40202903cb77947d62ecbe80a1", "settled_ticket_sha256": "f5cf7bf81f50aaa5c3223ca29ac5fb735e0de8d77606b7edbc1450ace871ca57"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 3, "SRI-L": 5, "T3I-L": 6, "HPI-L": 2}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 6, "second_pre_rank": 1, "third_pre_rank": 2, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [3, 5, 4], "rescues": ["WINNER_ROLE_RESCUE", "ORDERED_PAIR_RESCUE", "PAIR |
| TICKET | OK | {"head_local_p2": null, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cov |
| CAPITAL | ISSUE | {"pfs": 21.5, "profit_loss": -4710, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 6, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P1:HIT_BUT_LOSS | P1 | {"pfs": 21.5, "tickets": 60, "payout": 1290} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `e8b363a1e08335f5`／Learning State `48fc5b0c508c`</sub>
