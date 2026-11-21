# 2026-11-21 KOC_04 詳細反省（自動・実購入なし）

- 公式着順：4-5-9-6-2（上位3頭 [4, 5, 9]）
- 距離帯：UNKNOWN／第一実質失敗：**WINNER_DISCOVERED_LOW**
- 正しく判断できた項目：payout_positive

## PAPER

- 1着の事前順位 5／2着 1／3着 2；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 160／損益 -540／PFS 22.9%
- 参照：{"revision": "KOC_04.r2", "ticket_sha256": "0aca8f2026a2b2583562bbd5ab434a68a2c1aa7013b0b371661540319a7cda35", "frozen_at": "2026-11-21T16:20:59.257959+09:00"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | UNKNOWN | "no formal SOURCE for this race (PAPER only)" |
| INDEX | UNKNOWN | "NO_PRODUCTION_FULL29" |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（バリキング）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 5, "second_pre_rank": 1, "third_pre_rank": 2, "winner_in_W": false, "second_in_P2": false, "third_in_P3": false} |
| KRS | UNKNOWN | {"research_krs": ["KOC_04.r2"]} |
| TICKET | OK | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 22.9, "profit_loss": -540, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": null, "tickets": null} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | "SOURCE_FREEZE: HTTP_422:RAKUTEN_VENUE_NOT_IN_SCOPE" | next 20 eligible races reach Signed FINAL | formal completion rate per venue | formal Signed FINAL rate |
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 5, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P1:HIT_BUT_LOSS | P1 | {"pfs": 22.9, "tickets": null, "payout": 160} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `3080b8a126ad1a7e`／Learning State ``</sub>
