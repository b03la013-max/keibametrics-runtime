# 2026-11-16 KNZ_12 詳細反省（自動・実購入なし）

- 公式着順：2-3-1-4-5（上位3頭 [2, 3, 1]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 2／2着 1／3着 3；W False・P2 False・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 600／返還 0／払戻 360／損益 -240／PFS 60.0%
- 参照：{"revision": "KNZ_12.r2", "ticket_sha256": "18410713f8c6fa10b14540acad3bb172803be3c199f6669e1f55a2f8a68b7b70", "frozen_at": "2026-11-16T18:00:06.758696+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 1／3着 4；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 4800／返還 0／払戻 780／損益 -4020／PFS 16.2%
- 参照：{"final_receipt_sha256": "bacbed68d4f75ef5ad3fa7dd9e7d6b65c00f7e66679d6eea1c4bb37013e07bcf", "result_receipt_sha256": "8b7531709f2d442e6af6ffcc6516d7c9f59d06ec81145507ac53ecf7e1a6f867", "result_receipt_verified": true, "krs_input_mode": null, "authority": null}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 1, "HPI-L": 1}, "ruled_neutral_share": null} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（シンリミテス）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 1, "third_pre_rank": 4, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | UNKNOWN | {"pre_result_utility_class": null, "post_result_evaluation": {"classification": "NOT_AVAILABLE", "rescues": [], "supports": [], "misses": []}} |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 16.2, "profit_loss": -4020, "hit_but_loss": true, "tickets": 48} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | "automatic review krs.post_result_evaluation = NOT_AVAILABLE (utility not frozen in FINAL)" | next formal races carry krs_prediction_utility in the FINAL package | check FINAL package krs_prediction_utility_shadow presence | KRS evaluation availability rate |
| P1:HIT_BUT_LOSS | P1 | {"pfs": 16.2, "tickets": 48, "payout": 780} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `71a0c2e094d3d186`／Learning State `028a7b9e8cf7`</sub>
