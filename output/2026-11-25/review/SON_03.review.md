# 2026-11-25 SON_03 詳細反省（自動・実購入なし）

- 公式着順：9-6-2-5-8（上位3頭 [9, 6, 2]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 6／2着 1／3着 2；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 190／損益 -510／PFS 27.1%
- 参照：{"revision": "SON_03.r2", "ticket_sha256": "1f9195728ec5541358f34ad99fcdb8bc8213b0a4bbaa6cd6a0c710c1b0ae0ab8", "frozen_at": "2026-11-25T10:55:10.142307+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 5／2着 1／3着 2；W False・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 740／損益 -5260／PFS 12.3%
- 参照：{"final_receipt_sha256": "03f7ec81960f9b578b0dc7f4b6d7b8fc3f0f9f38aac00daa92fd16d819556316", "result_receipt_sha256": "7afeaa560b9924464a7c649051ee1cb2afcd395a5120752018a58b13b0a89fe0", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "d739be7954b4b46722254a406b41fd4bdfb1c9e80b1aef9340bdd699c1e94aec", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-25T02:30:03.356991+00:00", "source_receipt_sha256": "6355b7da09fd446c5b45347d12e30d91c48ed1797e3137aa9623006d8308dbaf", "signed_final_at": "2026-11-25T02:30:15.628863+00:00", "delivered_ticket_sha256": "ea212fffb143445ab469cdf333a59f250ccb57b6aa6e8c35210442770f29951e", "settled_ticket_sha256": "03f7ec81960f9b578b0dc7f4b6d7b8fc3f0f9f38aac00daa92fd16d819556316"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 5, "TPI-L": 5, "SRI-L": 7, "T3I-L": 8, "HPI-L": 3}, "ruled_neutral_share": 0.003} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補5頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 5, "second_pre_rank": 1, "third_pre_rank": 2, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [9, 6, 2], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CONF |
| TICKET | OK | {"head_local_p2": null, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cov |
| CAPITAL | ISSUE | {"pfs": 12.3, "profit_loss": -5260, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 5, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P1:HIT_BUT_LOSS | P1 | {"pfs": 12.3, "tickets": 60, "payout": 740} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `8027b017992e1130`／Learning State `02137aa0f037`</sub>
