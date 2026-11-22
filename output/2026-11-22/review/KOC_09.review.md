# 2026-11-22 KOC_09 詳細反省（自動・実購入なし）

- 公式着順：8-2-4-1-3（上位3頭 [8, 2, 4]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 3／2着 5／3着 2；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "KOC_09.r2", "ticket_sha256": "79d408670af2404c466fd29b96e75aabedb50f78664fcc59a8c71de9bb7a65cc", "frozen_at": "2026-11-22T19:00:09.171813+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 5／2着 4／3着 1；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 800／損益 -5200／PFS 13.3%
- 参照：{"final_receipt_sha256": "6b2e355d38e0a111b189bb79740c1d751d8118a7a70ed98111e160a9d119ec6a", "result_receipt_sha256": "3751a57369ccbefd60d0fa1d2565ee78827bda735b7269442a3497d3436fb033", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "2d4d75a833e48db9de42045c3f0f2d9bb841a5a0dd1582aa7a724b6de692ddc5", "signed_final_ticket_count": 105, "signed_final_total_investment": 10500, "signed_final_settlement": {"invest": 10500, "refund": 0, "effective_invest": 10500, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_1", "source_at": "2026-11-22T10:02:11.710854+00:00", "source_receipt_sha256": "cb809252f1adccce09e52e7443743d997fbe9b8ba5bb53ae916a90fd4010df03", "signed_final_at": "2026-11-22T10:02:21.922712+00:00", "delivered_ticket_sha256": "00cca85c188145c9ce5adc67024da00907576afa905f91c2f46fd3428dd2796a", "settled_ticket_sha256": "6b2e355d38e0a111b189bb79740c1d751d8118a7a70ed98111e160a9d119ec6a"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 4, "TPI-L": 4, "SRI-L": 4, "T3I-L": 6, "HPI-L": 2}, "ruled_neutral_share": 0.073} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 5, "second_pre_rank": 4, "third_pre_rank": 1, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [8, 2, 4], "rescues": [], "supports": ["P3_ROLE_CONFIRMED", "ORDERED_PAIR_CONFIRMED"] |
| TICKET | OK | {"head_local_p2": null, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cov |
| CAPITAL | ISSUE | {"pfs": 13.3, "profit_loss": -5200, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 5, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P1:HIT_BUT_LOSS | P1 | {"pfs": 13.3, "tickets": 60, "payout": 800} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `be74fce97df4529f`／Learning State `c3e6c67ccb4a`</sub>
