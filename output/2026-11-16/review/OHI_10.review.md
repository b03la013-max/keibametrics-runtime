# 2026-11-16 OHI_10 詳細反省（自動・実購入なし）

- 公式着順：10-2-13-7-14（上位3頭 [10, 2, 13]）
- 距離帯：LONG(>2100)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 1／2着 2／3着 7；W True・P2 True・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 800／返還 0／払戻 1100／損益 300／PFS 137.5%
- 参照：{"revision": "OHI_10.r2", "ticket_sha256": "46719ca5b1ad18172cb2770a10fe06d13cb4ed5cb6119790e27e0e9860b129ee", "frozen_at": "2026-11-16T18:45:12.873143+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 6／2着 3／3着 7；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 18000／返還 0／払戻 0／損益 -18000／PFS 0.0%
- 参照：{"final_receipt_sha256": "c5241d7249545b06325be3efad1c7993e37653886f746d6931a8ecf62c3a8174", "result_receipt_sha256": "d8d6825df0a627e3eea947feab44a7986e03c66e67e4f2517c1999ebad254540", "result_receipt_verified": true, "krs_input_mode": null, "authority": null}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 1, "SRI-L": 2, "T3I-L": 2, "HPI-L": 1}, "ruled_neutral_share": 0.113} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補4頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 6, "second_pre_rank": 3, "third_pre_rank": 7, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | UNKNOWN | {"pre_result_utility_class": null, "post_result_evaluation": {"classification": "NOT_AVAILABLE", "rescues": [], "supports": [], "misses": []}} |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": true, "ordered_exact_ticket_co |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -18000, "hit_but_loss": false, "tickets": 180} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | "automatic review krs.post_result_evaluation = NOT_AVAILABLE (utility not frozen in FINAL)" | next formal races carry krs_prediction_utility in the FINAL package | check FINAL package krs_prediction_utility_shadow presence | KRS evaluation availability rate |
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 6, "alternative_signals_that_had_winner_top": ["PAPER ◎ was the winner", "TPI-L ranked the winner #1 | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `192d8650d4080969`／Learning State `70cc5c61503d`</sub>
