# 2026-11-16 KNZ_07 詳細反省（自動・実購入なし）

- 公式着順：3-8-4-6-1（上位3頭 [3, 8, 4]）
- 距離帯：UNKNOWN／第一実質失敗：**WINNER_DISCOVERED_LOW**
- 正しく判断できた項目：third_in_P3, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 4／2着 1／3着 3；W False・P2 False・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 800／返還 0／払戻 330／損益 -470／PFS 41.2%
- 参照：{"revision": "KNZ_07.r2", "ticket_sha256": "f25ce804ee263b442600988b9e71575fc88fc0f01906706aef536c132141a3e8", "frozen_at": "2026-11-16T15:00:06.772009+09:00"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | UNKNOWN | "no formal SOURCE for this race (PAPER only)" |
| INDEX | UNKNOWN | "NO_PRODUCTION_FULL29" |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 4, "second_pre_rank": 1, "third_pre_rank": 3, "winner_in_W": false, "second_in_P2": false, "third_in_P3": true} |
| KRS | UNKNOWN | {"research_krs": []} |
| TICKET | OK | {"head_local_p2": null, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": null, "top3_set_ticket_coverage": null, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 41.2, "profit_loss": -470, "hit_but_loss": null, "tickets": null} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 4, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P1:HIT_BUT_LOSS | P1 | {"pfs": 41.2, "tickets": null, "payout": 330} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `f901a430a726129f`／Learning State ``</sub>
