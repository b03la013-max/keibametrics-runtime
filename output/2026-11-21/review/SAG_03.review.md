# 2026-11-21 SAG_03 詳細反省（自動・実購入なし）

- 公式着順：2-3-8-1-4（上位3頭 [2, 3, 8]）
- 距離帯：UNKNOWN／第一実質失敗：**W_WIDTH_OR_ROLE**
- 正しく判断できた項目：payout_positive

## PAPER

- 1着の事前順位 2／2着 1／3着 6；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 110／損益 -590／PFS 15.7%
- 参照：{"revision": "SAG_03.r2", "ticket_sha256": "d2b4844f5cb70e114dd8c90c5ba23ae5a2d866490b6c488718de860618d38427", "frozen_at": "2026-11-21T16:20:09.333055+09:00"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | UNKNOWN | "no formal SOURCE for this race (PAPER only)" |
| INDEX | UNKNOWN | "NO_PRODUCTION_FULL29" |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（マッドヘッドラブ）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 2, "second_pre_rank": 1, "third_pre_rank": 6, "winner_in_W": false, "second_in_P2": false, "third_in_P3": false} |
| KRS | UNKNOWN | {"research_krs": []} |
| TICKET | OK | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 15.7, "profit_loss": -590, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": null, "tickets": null} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 2, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P1:HIT_BUT_LOSS | P1 | {"pfs": 15.7, "tickets": null, "payout": 110} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `41141068b1b430ba`／Learning State ``</sub>
