# 2026-11-19 SON_09 詳細反省（自動・実購入なし）

- 公式着順：9-8-6-7-1（上位3頭 [9, 8, 6]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 1／2着 4／3着 8；W True・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 1600／返還 0／払戻 430／損益 -1170／PFS 26.9%
- 参照：{"revision": "SON_09.r2", "ticket_sha256": "67b6724d1c075b4dab8625be7f046b0727fc2c9fb031d015467ce72a4f58b339", "frozen_at": "2026-11-19T14:00:13.944102+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 2／3着 6；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 5340／損益 -660／PFS 89.0%
- 参照：{"final_receipt_sha256": "b18056f331fcad100f3ef26e36ca52ad24861269db86491bc18614b7ca0675f5", "result_receipt_sha256": "84662e7333af8e3eda119ca51a86c2583cddf18564b0e1bc15f8e5bc63793211", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "80d8b0b8104961dac13eed223deb386159451f98ba10044476bc28c6eb13bdd3", "signed_final_ticket_count": 120, "signed_final_total_investment": 12000, "signed_final_settlement": {"invest": 12000, "refund": 0, "effective_invest": 12000, "payout": 5340, "pfs": 44.5}, "effective_revision": "REVISION_1", "source_at": null, "signed_final_at": "2026-11-19T05:05:31.165438+00:00", "delivered_ticket_sha256": "ea3b81269b79c100ca2e6401dfc26989ec83a6f7366858d349f3b508868939a1", "settled_ticket_sha256": "b18056f331fcad100f3ef26e36ca52ad24861269db86491bc18614b7ca0675f5"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 2, "HPI-L": 2}, "ruled_neutral_share": 0.111} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 2, "third_pre_rank": 6, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [9, 8, 6], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_CONFIRMED",  |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 89.0, "profit_loss": -660, "hit_but_loss": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 89.0, "tickets": 60, "payout": 5340} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `8e7ade24b482d1d0`／Learning State `7809b830ba09`</sub>
