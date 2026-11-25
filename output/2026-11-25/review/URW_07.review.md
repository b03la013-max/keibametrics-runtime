# 2026-11-25 URW_07 詳細反省（自動・実購入なし）

- 公式着順：7-5-4-10-3（上位3頭 [7, 5, 4]）
- 距離帯：MIDDLE(1701-2100)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 2／2着 1／3着 5；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 3710／損益 3010／PFS 530.0%
- 参照：{"revision": "URW_07.r2", "ticket_sha256": "de00091e11ea28947417a2d7871a29d00f6a09a78b97260fa1c2043cc53212bc", "frozen_at": "2026-11-25T14:40:07.891943+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 4／2着 1／3着 9；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "a63acd07011ffd6e4aa297a0d520d6634832f094e8de02bde288844cd3407ff5", "result_receipt_sha256": "fdb0cc3145b247797bfb656aa2e0576deccb109ffb0594470131042f38ee0cd9", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "e8f83c73541861c78b8b049b40532f0f6bdb9baaaaa798e25b383992c74b3c3c", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-25T06:17:19.710088+00:00", "source_receipt_sha256": "4c4428639014444310db92b3a415243641a5f59e30517b4ba5dc582780ca0f0e", "signed_final_at": "2026-11-25T06:17:32.129376+00:00", "delivered_ticket_sha256": "f92e64ddba78db9abaaf4b930cdd638f3c89d2316cf5865b3cd9606f2f4d45e2", "settled_ticket_sha256": "a63acd07011ffd6e4aa297a0d520d6634832f094e8de02bde288844cd3407ff5"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 5, "TPI-L": 6, "SRI-L": 5, "T3I-L": 10, "HPI-L": 2}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 4, "second_pre_rank": 1, "third_pre_rank": 9, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [7, 5, 4], "rescues": ["WINNER_ROLE_RESCUE", "ORDERED_PAIR_RESCUE"], "sup |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 4, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `516ec5cf18f2b016`／Learning State `7f040b00f5a2`</sub>
