# 2026-11-16 OHI_07 詳細反省（自動・実購入なし）

- 公式着順：11-8-2-4-1（上位3頭 [11, 8, 2]）
- 距離帯：UNKNOWN／第一実質失敗：**WINNER_NOT_DISCOVERED**
- 正しく判断できた項目：なし

## PAPER

- 1着の事前順位 7／2着 6／3着 1；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 800／返還 0／払戻 0／損益 -800／PFS 0.0%
- 参照：{"revision": "OHI_07.r2", "ticket_sha256": "084bbc9f60b6458c78982461bf54393706a263c74d276cb0617b93c8a9a4c4a5", "frozen_at": "2026-11-16T17:00:03.362937+09:00"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | UNKNOWN | "no formal SOURCE for this race (PAPER only)" |
| INDEX | UNKNOWN | "NO_PRODUCTION_FULL29" |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 7, "second_pre_rank": 6, "third_pre_rank": 1, "winner_in_W": false, "second_in_P2": false, "third_in_P3": false} |
| KRS | UNKNOWN | {"research_krs": ["OHI_07.r2"]} |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": null, "top3_set_ticket_coverage": null, "ordered_exact_ticket_cov |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -800, "hit_but_loss": null, "tickets": null} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | "SOURCE_FREEZE: HTTP_200:['REQUIRED_SOURCE_FETCH_FAILED:RAKUTEN_RACE_CARD:SOURCE_HOST_NOT_ALLOWED:keiba.rakuten.co.jp',  | next 20 eligible races reach Signed FINAL | formal completion rate per venue | formal Signed FINAL rate |
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 7, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `88384a8fd3399943`／Learning State ``</sub>
