# 2026-11-16 KNZ_03 詳細反省（自動・実購入なし）

- 公式着順：3-2-7-5-6（上位3頭 [3, 2, 7]）
- 距離帯：UNKNOWN／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 1／2着 2／3着 5；W True・P2 True・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 800／返還 0／払戻 500／損益 -300／PFS 62.5%
- 参照：{"revision": "KNZ_03.r2", "ticket_sha256": "fd1dfddccceb0426bba4efd51ebb0f3ed97472ed8aa19fde96bdcc8b013f52be", "frozen_at": "2026-11-16T12:40:14.117043+09:00"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | UNKNOWN | "no formal SOURCE for this race (PAPER only)" |
| INDEX | UNKNOWN | "NO_PRODUCTION_FULL29" |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（ドリーマーズ）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 1, "second_pre_rank": 2, "third_pre_rank": 5, "winner_in_W": true, "second_in_P2": true, "third_in_P3": false} |
| KRS | UNKNOWN | {"research_krs": []} |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": null, "top3_set_ticket_coverage": null, "ordered_exact_ticket_co |
| CAPITAL | ISSUE | {"pfs": 62.5, "profit_loss": -300, "hit_but_loss": null, "tickets": null} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P3_MISS | P1 | {"third_pre_rank": 5} | >=30 forward races: P3 tail extension does not raise PFS | counterfactual P3 tail on frozen races | P3 capture, PFS |
| P1:HIT_BUT_LOSS | P1 | {"pfs": 62.5, "tickets": null, "payout": 500} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `ad364956021f9bee`／Learning State ``</sub>
