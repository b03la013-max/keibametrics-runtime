# 2026-11-16 MIZ_12 詳細反省（自動・実購入なし）

- 公式着順：7-6-2-5-9（上位3頭 [7, 6, 2]）
- 距離帯：UNKNOWN／第一実質失敗：**P2_MISS**
- 正しく判断できた項目：winner_in_W

## PAPER

- 1着の事前順位 1／2着 6／3着 4；W True・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "MIZ_12.r2", "ticket_sha256": "a5c1e5f2ac069bd5ef8222b727870ae2e9bab414dd161651f584450035093fd8", "frozen_at": "2026-11-16T17:25:13.298939+09:00"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | UNKNOWN | "no formal SOURCE for this race (PAPER only)" |
| INDEX | UNKNOWN | "NO_PRODUCTION_FULL29" |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 1, "second_pre_rank": 6, "third_pre_rank": 4, "winner_in_W": true, "second_in_P2": false, "third_in_P3": false} |
| KRS | UNKNOWN | {"research_krs": ["MIZ_12.r2"]} |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": null, "top3_set_ticket_coverage": null, "ordered_exact_ticket_cov |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -700, "hit_but_loss": null, "tickets": null} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | "SOURCE_FREEZE: HTTP_200:['REQUIRED_SOURCE_FETCH_FAILED:RAKUTEN_RACE_CARD:SOURCE_HOST_NOT_ALLOWED:keiba.rakuten.co.jp',  | next 20 eligible races reach Signed FINAL | formal completion rate per venue | formal Signed FINAL rate |
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 6} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `1725eb9ab263d495`／Learning State ``</sub>
