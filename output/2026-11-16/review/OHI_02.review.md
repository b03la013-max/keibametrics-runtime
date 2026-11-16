# 2026-11-16 OHI_02 詳細反省（自動・実購入なし）

- 公式着順：7-3-10-2-9（上位3頭 [7, 3, 10]）
- 距離帯：UNKNOWN／第一実質失敗：**WINNER_DISCOVERED_LOW**
- 正しく判断できた項目：なし

## PAPER

- 1着の事前順位 5／2着 3／3着 2；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 900／返還 0／払戻 0／損益 -900／PFS 0.0%
- 参照：{"revision": "OHI_02.r2", "ticket_sha256": "70f2ca0610e9879df10b0b7ebd98ccc3ee0b463ef01fe5171585aed4409759c0", "frozen_at": "2026-11-16T14:17:14.346328+09:00"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | UNKNOWN | "no formal SOURCE for this race (PAPER only)" |
| INDEX | UNKNOWN | "NO_PRODUCTION_FULL29" |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（アルダヴァイン）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 5, "second_pre_rank": 3, "third_pre_rank": 2, "winner_in_W": false, "second_in_P2": false, "third_in_P3": false} |
| KRS | UNKNOWN | {"research_krs": []} |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": null, "top3_set_ticket_coverage": null, "ordered_exact_ticket_cov |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -900, "hit_but_loss": null, "tickets": null} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 5, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `2071b5ac7ba0cc9e`／Learning State ``</sub>
