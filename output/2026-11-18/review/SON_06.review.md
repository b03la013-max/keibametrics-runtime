# 2026-11-18 SON_06 詳細反省（自動・実購入なし）

- 公式着順：5-3-2-9-4（上位3頭 [5, 3, 2]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 3／2着 4／3着 1；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "SON_06.r2", "ticket_sha256": "c7675f33f933b193b240083b76bac8a36f04b67dad872f9128f5bb48d233f804", "frozen_at": "2026-11-18T12:25:05.419206+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 5／2着 6／3着 1；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "f7325dc0b7ea165a77c76e8ec26409c16b89b3482c88c85f8d15d6120145cc53", "result_receipt_sha256": "42aa418958794476cc9d8c5bc45470a5f26cfd53ffa465f7450d8bd02306168f", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "0af6cc4c1ab6f8ebd327d573b0a30e285b9509f81bdce04a57db88fca8102d04", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 0, "pfs": 0.0}}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 3, "SRI-L": 4, "T3I-L": 4, "HPI-L": 3}, "ruled_neutral_share": 0.124} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（サチノメグミ）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 5, "second_pre_rank": 6, "third_pre_rank": 1, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [5, 3, 2], "rescues": ["WINNER_ROLE_RESCUE"], "supports": ["P3_ROLE_CONFI |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": true, "ordered_exact_ticket_co |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 5, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `84fbfb95276f9715`／Learning State `d63bfdc42791`</sub>
