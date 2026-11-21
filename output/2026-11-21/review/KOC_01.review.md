# 2026-11-21 KOC_01 詳細反省（自動・実購入なし）

- 公式着順：6-7-3-4-2（上位3頭 [6, 7, 3]）
- 距離帯：UNKNOWN／第一実質失敗：**WINNER_DISCOVERED_LOW**
- 正しく判断できた項目：second_in_P2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 6／2着 2／3着 1；W False・P2 True・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 830／損益 130／PFS 118.6%
- 参照：{"revision": "KOC_01.r1", "ticket_sha256": "8e7042a8ebbb0cc9406f51f6b11de87aa6bb120ed1473fd2b6db1e75d2229082", "frozen_at": "2026-11-20T21:03:33.703884+09:00"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | UNKNOWN | "no formal SOURCE for this race (PAPER only)" |
| INDEX | UNKNOWN | "NO_PRODUCTION_FULL29" |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 6, "second_pre_rank": 2, "third_pre_rank": 1, "winner_in_W": false, "second_in_P2": true, "third_in_P3": false} |
| KRS | UNKNOWN | {"research_krs": []} |
| TICKET | OK | {"head_local_p2": null, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cov |
| CAPITAL | OK | {"pfs": 118.6, "profit_loss": 130, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": null, "tickets": null} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 6, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `81809254416d2106`／Learning State ``</sub>
