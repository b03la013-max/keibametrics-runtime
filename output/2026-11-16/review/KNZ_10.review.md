# 2026-11-16 KNZ_10 詳細反省（自動・実購入なし）

- 公式着順：2-8-1-3-9（上位3頭 [2, 8, 1]）
- 距離帯：UNKNOWN／第一実質失敗：**W_WIDTH_OR_ROLE**
- 正しく判断できた項目：third_in_P3, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 2／2着 4／3着 3；W False・P2 False・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 900／返還 0／払戻 1650／損益 750／PFS 183.3%
- 参照：{"revision": "KNZ_10.r2", "ticket_sha256": "90f5097ff906b26f9e6868f4da52edb4cda42c5065fc78aadf5c53142edc90c7", "frozen_at": "2026-11-16T16:45:08.080939+09:00"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | UNKNOWN | "no formal SOURCE for this race (PAPER only)" |
| INDEX | UNKNOWN | "NO_PRODUCTION_FULL29" |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補4頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 2, "second_pre_rank": 4, "third_pre_rank": 3, "winner_in_W": false, "second_in_P2": false, "third_in_P3": true} |
| KRS | UNKNOWN | {"research_krs": ["KNZ_10.r2"]} |
| TICKET | OK | {"head_local_p2": null, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": null, "top3_set_ticket_coverage": null, "ordered_exact_ticket_cove |
| CAPITAL | OK | {"pfs": 183.3, "profit_loss": 750, "hit_but_loss": null, "tickets": null} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 2, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `cfb385064e92d7ae`／Learning State ``</sub>
