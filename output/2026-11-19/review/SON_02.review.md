# 2026-11-19 SON_02 詳細反省（自動・実購入なし）

- 公式着順：10-5-6-1-3（上位3頭 [10, 5, 6]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 5／2着 2／3着 7；W False・P2 True・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "SON_02.r2", "ticket_sha256": "69adc29494970675f7b769fd705ead950797b8d864df41efa02be725a7b1188c", "frozen_at": "2026-11-19T10:25:15.458865+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 5／2着 4／3着 7；W False・P2 True・P3 True
- Top3捕捉 0／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "7a372d34b9c11af8c2a1aae72787ef02c85a6c73175d935966c00b1222dd2d14", "result_receipt_sha256": "63f578fdfe99f9e801e594ee7f6a9006e18f225f23671da26b402ddc41373749", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "fe20e7d265f86ecdfce0ae72d5f60d33d06d1f40a2a0fa247f36a51c6de1d502", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": null, "signed_final_at": "2026-11-19T02:00:16.547275+00:00", "delivered_ticket_sha256": "d45278508415c47c3e53aba792ddb6222a26e1f4fc62f2035c4d4e97f260d322", "settled_ticket_sha256": "7a372d34b9c11af8c2a1aae72787ef02c85a6c73175d935966c00b1222dd2d14"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 2, "SRI-L": 5, "T3I-L": 5, "HPI-L": 4}, "ruled_neutral_share": 0.124} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 5, "second_pre_rank": 4, "third_pre_rank": 7, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [10, 5, 6], "rescues": ["WINNER_ROLE_RESCUE", "ORDERED_PAIR_RESCUE"], "su |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 5, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `e5756af0df41aac7`／Learning State `aeb24c443e9c`</sub>
