# 2026-11-28 SAG_07 詳細反省（自動・実購入なし）

- 公式着順：5-7-8-10-6（上位3頭 [5, 7, 8]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 4／2着 3／3着 9；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "SAG_07.r2", "ticket_sha256": "83b4f3b97c311d86afc8365495a3502a21d27b058f7a863c18f440e0212798cd", "frozen_at": "2026-11-28T17:20:17.684356+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 4／2着 2／3着 8；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "087f7f537fd17a3cb9bbfbc6036c83295ebd701579f22c18175551888b281c83", "result_receipt_sha256": "58e10c91b04b26fa5d45bd432843ba28c9ad92ca53f1584f98031f5678ee03f9", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "a0595ee2462874c0ec1fec066606f5c5f861c143732f56902df285d42c515e7b", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-28T08:55:07.619807+00:00", "source_receipt_sha256": "c969951cfb8c6093cb0142379abdacc325f4cff13f7715a8d1e4f14b0ad89d20", "signed_final_at": "2026-11-28T08:55:19.328004+00:00", "delivered_ticket_sha256": "2aaea09beb78e6dd62520876031b82e6a67a4eb6415f8b18edf2b649dc6d23d7", "settled_ticket_sha256": "087f7f537fd17a3cb9bbfbc6036c83295ebd701579f22c18175551888b281c83"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 4, "TPI-L": 4, "SRI-L": 4, "T3I-L": 4, "HPI-L": 4}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 4, "second_pre_rank": 2, "third_pre_rank": 8, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [5, 7, 8], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "ORDERED_PAIR_CONFIRMED"] |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 4, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `eefa2c52d878c3f4`／Learning State `d606264d9dc9`</sub>
