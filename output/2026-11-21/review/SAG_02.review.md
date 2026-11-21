# 2026-11-21 SAG_02 詳細反省（自動・実購入なし）

- 公式着順：12-9-6-7-10（上位3頭 [12, 9, 6]）
- 距離帯：UNKNOWN／第一実質失敗：**WINNER_DISCOVERED_LOW**
- 正しく判断できた項目：なし

## PAPER

- 1着の事前順位 6／2着 5／3着 1；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 1600／返還 0／払戻 0／損益 -1600／PFS 0.0%
- 参照：{"revision": "SAG_02.r1", "ticket_sha256": "4e87c1713fa38d8958bcb4491ca9470e5de28ffe9bc87307b49d5dfe74d140da", "frozen_at": "2026-11-20T21:05:35.512130+09:00"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | UNKNOWN | "no formal SOURCE for this race (PAPER only)" |
| INDEX | UNKNOWN | "NO_PRODUCTION_FULL29" |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 6, "second_pre_rank": 5, "third_pre_rank": 1, "winner_in_W": false, "second_in_P2": false, "third_in_P3": false} |
| KRS | UNKNOWN | {"research_krs": []} |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -1600, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": null, "tickets": null} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 6, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `2b54dc4d1b31b581`／Learning State ``</sub>
