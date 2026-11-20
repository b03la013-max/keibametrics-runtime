# 2026-11-20 OHI_06 詳細反省（自動・実購入なし）

- 公式着順：9-5-1-10-3（上位3頭 [9, 5, 1]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 2／2着 3／3着 11；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "OHI_06.r2", "ticket_sha256": "c26aa9d3c1b196dcc5436cc0a96760a558e7c944d14c36d38be107ac898b09ab", "frozen_at": "2026-11-20T16:28:07.736116+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 4／2着 3／3着 8；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "b44f19537a98840b15050eb550f3454255999f85e7fea0335a0d50bebb59e8c0", "result_receipt_sha256": "0ddd413279a44bef625139d3b5404360c321c36351743a752754a84ce5f96442", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "7f68ce661994988756007342ffe02f17188fbf961f103ea85d55e06647cc8a4a", "signed_final_ticket_count": 180, "signed_final_total_investment": 18000, "signed_final_settlement": {"invest": 18000, "refund": 0, "effective_invest": 18000, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_1", "source_at": "2026-11-20T07:33:12.023850+00:00", "source_receipt_sha256": "126a4b685b5ff8fc8dbdbe1122766d2f37324a57a14b7898be6ae9b67e869cae", "signed_final_at": "2026-11-20T07:33:24.666645+00:00", "delivered_ticket_sha256": "dff028ec9dc1f683dd85d7394bfdf5b6a7ff9da72a22659702de241bc4127dd1", "settled_ticket_sha256": "b44f19537a98840b15050eb550f3454255999f85e7fea0335a0d50bebb59e8c0"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 5, "SRI-L": 4, "T3I-L": 6, "HPI-L": 4}, "ruled_neutral_share": 0.111} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 4, "second_pre_rank": 3, "third_pre_rank": 8, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [9, 5, 1], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CONF |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 4, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `8b0e2e0efff10a49`／Learning State `82ec2c1af9f6`</sub>
