# 2026-11-16 KNZ_05 詳細反省（自動・実購入なし）

- 公式着順：6-2-8-5-4（上位3頭 [6, 2, 8]）
- 距離帯：UNKNOWN／第一実質失敗：**THIRD_MISS**
- 正しく判断できた項目：winner_in_W, second_in_P2, payout_positive

## PAPER

- 1着の事前順位 1／2着 2／3着 8；W True・P2 True・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 120／損益 -580／PFS 17.1%
- 参照：{"revision": "KNZ_05.r2", "ticket_sha256": "7cdb6eed51200c803d716ab1db92e030e284bd844d5d1a66964afc4e3b129916", "frozen_at": "2026-11-16T13:50:05.436563+09:00"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | UNKNOWN | "no formal SOURCE for this race (PAPER only)" |
| INDEX | UNKNOWN | "NO_PRODUCTION_FULL29" |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 1, "second_pre_rank": 2, "third_pre_rank": 8, "winner_in_W": true, "second_in_P2": true, "third_in_P3": false} |
| KRS | UNKNOWN | {"research_krs": []} |
| TICKET | OK | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": null, "top3_set_ticket_coverage": null, "ordered_exact_ticket_cov |
| CAPITAL | ISSUE | {"pfs": 17.1, "profit_loss": -580, "hit_but_loss": null, "tickets": null} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P3_MISS | P1 | {"third_pre_rank": 8} | >=30 forward races: P3 tail extension does not raise PFS | counterfactual P3 tail on frozen races | P3 capture, PFS |
| P1:HIT_BUT_LOSS | P1 | {"pfs": 17.1, "tickets": null, "payout": 120} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `c6046e29979f06fd`／Learning State ``</sub>
