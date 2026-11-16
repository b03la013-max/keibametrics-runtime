# 2026-11-16 MIZ_01 詳細反省（自動・実購入なし）

- 公式着順：7-6-8-9-3（上位3頭 [7, 6, 8]）
- 距離帯：UNKNOWN／第一実質失敗：**P2_MISS**
- 正しく判断できた項目：winner_in_W, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 1／2着 7／3着 2；W True・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 3170／損益 2470／PFS 452.9%
- 参照：{"revision": "MIZ_01.r2", "ticket_sha256": "aff37149af391a350b69200c0d6cad04bf4ee5f7a7dd525fb8a095a902ff43b8", "frozen_at": "2026-11-16T11:00:15.434718+09:00"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | UNKNOWN | "no formal SOURCE for this race (PAPER only)" |
| INDEX | UNKNOWN | "NO_PRODUCTION_FULL29" |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（イヌボウノシオカゼ）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 1, "second_pre_rank": 7, "third_pre_rank": 2, "winner_in_W": true, "second_in_P2": false, "third_in_P3": false} |
| KRS | UNKNOWN | {"research_krs": []} |
| TICKET | OK | {"head_local_p2": null, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": null, "top3_set_ticket_coverage": null, "ordered_exact_ticket_cove |
| CAPITAL | OK | {"pfs": 452.9, "profit_loss": 2470, "hit_but_loss": null, "tickets": null} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 7} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `c2a5ef49864d3df4`／Learning State ``</sub>
