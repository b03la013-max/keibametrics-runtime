# 2026-11-16 OHI_09 詳細反省（自動・実購入なし）

- 公式着順：6-11-2-7-8（上位3頭 [6, 11, 2]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**PREDICTION_ROLE_P2**
- 正しく判断できた項目：winner_in_W, third_in_P3, winner_is_ticket_head, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 1／2着 4／3着 2；W True・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 3；Head-local P2 False；Pair条件付き3着 True
- 投資 800／返還 0／払戻 3200／損益 2400／PFS 400.0%
- 参照：{"revision": "OHI_09.r2", "ticket_sha256": "f175dca4a55699cb2b7f2443943089a660c91ca905360237b915cc0d31f4cd7c", "frozen_at": "2026-11-16T18:11:59.085788+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 10／3着 2；W True・P2 False・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 False；Pair条件付き3着 True
- 投資 16800／返還 0／払戻 3040／損益 -13760／PFS 18.1%
- 参照：{"final_receipt_sha256": "5d17b4e931826c8a8d2413d0d5a520a17d7a2a6ace8c56f8fd5ade372124fda5", "result_receipt_sha256": "594f873ffb736ed77ea1c2f0e23adc35b7cbaa2859bffd572afca6f338d18456", "result_receipt_verified": true, "krs_input_mode": null, "authority": null}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 1, "SRI-L": 1, "T3I-L": 1, "HPI-L": 1}, "ruled_neutral_share": null} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 1, "second_pre_rank": 10, "third_pre_rank": 2, "winner_in_W": true, "second_in_P2": false, "third_in_P3": true} |
| KRS | UNKNOWN | {"pre_result_utility_class": null, "post_result_evaluation": {"classification": "NOT_AVAILABLE", "rescues": [], "supports": [], "misses": []}} |
| TICKET | OK | {"head_local_p2": false, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": true, "ordered_exact_ticket_co |
| CAPITAL | ISSUE | {"pfs": 18.1, "profit_loss": -13760, "hit_but_loss": true, "tickets": 168} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | "automatic review krs.post_result_evaluation = NOT_AVAILABLE (utility not frozen in FINAL)" | next formal races carry krs_prediction_utility in the FINAL package | check FINAL package krs_prediction_utility_shadow presence | KRS evaluation availability rate |
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 10} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P1:HIT_BUT_LOSS | P1 | {"pfs": 18.1, "tickets": 168, "payout": 3040} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `6c850bb25d72e691`／Learning State `f4fa81fd4052`</sub>
