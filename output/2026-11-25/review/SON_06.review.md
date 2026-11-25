# 2026-11-25 SON_06 詳細反省（自動・実購入なし）

- 公式着順：10-4-6-5-9（上位3頭 [10, 4, 6]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 7／2着 3／3着 10；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "SON_06.r2", "ticket_sha256": "ed8f04e00fbf4ef0da6600e8c1676ce88b492c66dd2bac3dec88051dee4e831f", "frozen_at": "2026-11-25T12:35:06.488699+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 7／2着 5／3着 8；W False・P2 True・P3 True
- Top3捕捉 0／Top4捕捉 0；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "077e5d1237cca2d561f5e502b7f586476f0848b44c9b482805ca84514705ea84", "result_receipt_sha256": "06d5066eb319a5e7a2ef819df2397b913f8db8137dfb276058d7686efbbe8bc9", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "a5ab509fc153114d322890004e8049e92f0906f574a57fc2d0204180d5c7b082", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-25T04:10:02.730842+00:00", "source_receipt_sha256": "6cc8e2120b3ccc4c3c84ec82ebbd4d182b72e33cd6e52d3e792c34c3ffe8e625", "signed_final_at": "2026-11-25T04:10:14.070525+00:00", "delivered_ticket_sha256": "d97f1d6124c4c33fbbe14fe360432a560085ee9527f7120eb92877af706fde9f", "settled_ticket_sha256": "077e5d1237cca2d561f5e502b7f586476f0848b44c9b482805ca84514705ea84"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 10, "TPI-L": 10, "SRI-L": 10, "T3I-L": 10, "HPI-L": 10}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 7, "second_pre_rank": 5, "third_pre_rank": 8, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [10, 4, 6], "rescues": [], "supports": [], "misses": ["WINNER_ROLE_NOT_KR |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 7, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `57065c56e4c38bcb`／Learning State `43c4e5ced0c5`</sub>
