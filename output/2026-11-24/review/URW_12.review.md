# 2026-11-24 URW_12 詳細反省（自動・実購入なし）

- 公式着順：5-12-2-4-7（上位3頭 [5, 12, 2]）
- 距離帯：MIDDLE(1701-2100)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 7／2着 1／3着 8；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 1150／損益 450／PFS 164.3%
- 参照：{"revision": "URW_12.r2", "ticket_sha256": "65776efcc15c0b6c2537bd4dcc56232b7f87154972a9e1b4a826f62ef96c3b8b", "frozen_at": "2026-11-24T17:35:15.750243+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 8／2着 1／3着 3；W False・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "e5cbbea2b160753f6bb413490f3334309a53ce4900e21ebc88614732f84bca7a", "result_receipt_sha256": "9771c21c03bb9da027e605d575bf3254ea14d88822d5ff9b45ae2f9e2c795d14", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "29b5d6617f05b4935ac4884c0c73ae5a9bbe05b142ccdcc9dec230c08e7fbf6d", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-24T09:11:07.595885+00:00", "source_receipt_sha256": "05d14e9250e25c753f4ce472c289c66e0768b957d1bb96c515ebd797039add37", "signed_final_at": "2026-11-24T09:11:22.271551+00:00", "delivered_ticket_sha256": "9e6792166bb2fc150237e1d8eaed02efd229050a2a2ea92c1e7a47f903ec8049", "settled_ticket_sha256": "e5cbbea2b160753f6bb413490f3334309a53ce4900e21ebc88614732f84bca7a"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 10, "TPI-L": 10, "SRI-L": 10, "T3I-L": 9, "HPI-L": 10}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 8, "second_pre_rank": 1, "third_pre_rank": 3, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [5, 12, 2], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CON |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 8, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `0401a182fea215fc`／Learning State `8176177f7944`</sub>
