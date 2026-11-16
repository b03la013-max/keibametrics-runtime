# 2026-11-16 KNZ_01 詳細反省（自動・実購入なし）

- 公式着順：2-1-6-4-7（上位3頭 [2, 1, 6]）
- 距離帯：UNKNOWN／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 1／2着 2／3着 4；W True・P2 True・P3 False
- Top3捕捉 2／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 800／返還 0／払戻 2990／損益 2190／PFS 373.8%
- 参照：{"revision": "KNZ_01.r2", "ticket_sha256": "32672376faa9ba9a2fa49e6aa7206cbbc7f5ded2fbac6ce678b8dee142e78fc4", "frozen_at": "2026-11-16T11:30:03.646859+09:00"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | UNKNOWN | "no formal SOURCE for this race (PAPER only)" |
| INDEX | UNKNOWN | "NO_PRODUCTION_FULL29" |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 1, "second_pre_rank": 2, "third_pre_rank": 4, "winner_in_W": true, "second_in_P2": true, "third_in_P3": false} |
| KRS | UNKNOWN | {"research_krs": []} |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": null, "top3_set_ticket_coverage": null, "ordered_exact_ticket_cove |
| CAPITAL | OK | {"pfs": 373.8, "profit_loss": 2190, "hit_but_loss": null, "tickets": null} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P3_MISS | P1 | {"third_pre_rank": 4} | >=30 forward races: P3 tail extension does not raise PFS | counterfactual P3 tail on frozen races | P3 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `22327a9c046b3c36`／Learning State ``</sub>
