# 2026-11-22 KOC_08 詳細反省（自動・実購入なし）

- 公式着順：2-4-6-8-5（上位3頭 [2, 4, 6]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_P2**
- 正しく判断できた項目：winner_in_W, third_in_P3, winner_is_ticket_head

## PAPER

- 1着の事前順位 1／2着 7／3着 3；W True・P2 False・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 1320／損益 620／PFS 188.6%
- 参照：{"revision": "KOC_08.r2", "ticket_sha256": "91bce7cae48fe8ddb8d6ca454e83191d2ac7bde3ec8370c0fd574f8aeeaf933d", "frozen_at": "2026-11-22T18:30:22.685901+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 8／3着 4；W True・P2 False・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 False；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "af681130fb3ecb3e4c7165eee4f31a91665ea47e45cbd85a238387e81f1e2a10", "result_receipt_sha256": "3bf8a405c8d85194cf0c6de8bb2482ceed9a84c4beef54af0afc117e177fcbe5", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "2d5383aae56f74e07583355c0cc6d2e91a3a3367b87ef1e1f386892b47cf501a", "signed_final_ticket_count": 120, "signed_final_total_investment": 12000, "signed_final_settlement": {"invest": 12000, "refund": 0, "effective_invest": 12000, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-22T10:06:15.837908+00:00", "source_receipt_sha256": "4fc424c0858df3ab5c63f90b6b6e68bf7311f56cc900475e501ac1372252c113", "signed_final_at": "2026-11-22T10:06:26.287419+00:00", "delivered_ticket_sha256": "dc29294398439ce5fafc7dc2dfe99361ac0e4a164e1aea796d7053ea9c172fb3", "settled_ticket_sha256": "af681130fb3ecb3e4c7165eee4f31a91665ea47e45cbd85a238387e81f1e2a10"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 3, "SRI-L": 2, "T3I-L": 4, "HPI-L": 3}, "ruled_neutral_share": 0.077} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 2, "second_pre_rank": 8, "third_pre_rank": 4, "winner_in_W": true, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [2, 4, 6], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P3_ROLE_CONFIRMED"], |
| TICKET | ISSUE | {"head_local_p2": false, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 8} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `9ed2efb57cb6672f`／Learning State `ddb6462d3106`</sub>
