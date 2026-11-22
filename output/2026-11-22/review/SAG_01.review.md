# 2026-11-22 SAG_01 詳細反省（自動・実購入なし）

- 公式着順：1-3-2-6-5（上位3頭 [1, 3, 2]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 4／2着 3／3着 1；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 800／返還 0／払戻 600／損益 -200／PFS 75.0%
- 参照：{"revision": "SAG_01.r2", "ticket_sha256": "d447dd2ab02a7d5725ae4424b945131baacd2a0f18a2cebca380d9c960a7c486", "frozen_at": "2026-11-22T14:30:06.131039+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 4／2着 3／3着 2；W False・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 600／損益 -5400／PFS 10.0%
- 参照：{"final_receipt_sha256": "c375ca6cf7e9fc88e7038a77508ad3a57c4b300bd3017e3709080ac28e3890d3", "result_receipt_sha256": "8dbecb5520ae97e5d668ab6ce5a035a94729f097a7d6a4217e8d1454e9bcb574", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "4464c3f8a345396f868e8a70f0c5e94ef2ff0a84ea80b374aed917f86fc3865d", "signed_final_ticket_count": 120, "signed_final_total_investment": 12000, "signed_final_settlement": {"invest": 12000, "refund": 0, "effective_invest": 12000, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-22T06:07:05.525320+00:00", "source_receipt_sha256": "506cbbbd08999d40151aaceb398f28e327e338291e3c4be9430cabebfa28baa4", "signed_final_at": "2026-11-22T06:07:16.432679+00:00", "delivered_ticket_sha256": "c884d54999e1b2e6a6c06df98844e420dae0040df8a6ff5cbf8c32105ed33e1f", "settled_ticket_sha256": "c375ca6cf7e9fc88e7038a77508ad3a57c4b300bd3017e3709080ac28e3890d3"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 5, "TPI-L": 5, "SRI-L": 4, "T3I-L": 8, "HPI-L": 4}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（ハクアイファミリー）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 4, "second_pre_rank": 3, "third_pre_rank": 2, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [1, 3, 2], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CONFIRMED", "ORD |
| TICKET | OK | {"head_local_p2": null, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cov |
| CAPITAL | ISSUE | {"pfs": 10.0, "profit_loss": -5400, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 4, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P1:HIT_BUT_LOSS | P1 | {"pfs": 10.0, "tickets": 60, "payout": 600} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `169983e501cf9051`／Learning State `b7819a048381`</sub>
