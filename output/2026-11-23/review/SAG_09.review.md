# 2026-11-23 SAG_09 詳細反省（自動・実購入なし）

- 公式着順：8-10-7-6-2（上位3頭 [8, 10, 7]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 1／2着 2／3着 5；W True・P2 True・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 1590／損益 890／PFS 227.1%
- 参照：{"revision": "SAG_09.r2", "ticket_sha256": "0c8003829377a8ff60af0d12b616992d3684c78b169ad2bd8753d25b305079c5", "frozen_at": "2026-11-23T19:00:03.411976+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 3／2着 2／3着 5；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 1790／損益 -4210／PFS 29.8%
- 参照：{"final_receipt_sha256": "b882470af77112a8183988c72fa435296a457bc8c0b7fdf225c7da4be153097d", "result_receipt_sha256": "20cc502a202db2f97d33cb54d6f40697eda995174af5c3b1614673aa3f514876", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "f8f0c9b27363dfb47c79a8a41ad0de3f8a86ef08bafb931f92c5dc77c5520918", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 3640, "pfs": 27.6}, "effective_revision": "REVISION_2", "source_at": "2026-11-23T10:37:20.242491+00:00", "source_receipt_sha256": "da77e7ba8820ba8d0da2f9fd6c85d2b30fdd5c9ef0c1a2f2bbf8e98ebdd3ddaa", "signed_final_at": "2026-11-23T10:37:35.130498+00:00", "delivered_ticket_sha256": "31118a655dc051618591113acc3efef1c2aaab222f84fb5c843612f92c3cd80b", "settled_ticket_sha256": "b882470af77112a8183988c72fa435296a457bc8c0b7fdf225c7da4be153097d"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 4, "TPI-L": 4, "SRI-L": 4, "T3I-L": 6, "HPI-L": 3}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補4頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 3, "second_pre_rank": 2, "third_pre_rank": 5, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [8, 10, 7], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CON |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 29.8, "profit_loss": -4210, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 29.8, "tickets": 60, "payout": 1790} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `b47a367a5811afe9`／Learning State `7dd1717beadd`</sub>
