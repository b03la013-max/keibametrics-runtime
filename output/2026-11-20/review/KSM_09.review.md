# 2026-11-20 KSM_09 詳細反省（自動・実購入なし）

- 公式着順：7-5-2-4-3（上位3頭 [7, 5, 2]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：third_in_P3

## PAPER

- 1着の事前順位 2／2着 6／3着 8；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "KSM_09.r2", "ticket_sha256": "e03b44ff9fe4eab3c8a6373f205fd499af69bd2a13724ae87a1e091abb7988c2", "frozen_at": "2026-11-20T13:50:47.795062+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 4／2着 8／3着 7；W False・P2 False・P3 True
- Top3捕捉 0／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "69734133966d6018bbf996756b2501b2ffd387e1eb1abf23352d5e04d192f8b2", "result_receipt_sha256": "eda8e9fa0ccb321832b69a75138576ef9fd46a5e958c40505a7fe6f8067927b3", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "ba106fde9d9bff29c049ed959bb6691220749b29705da628096f62e559f99545", "signed_final_ticket_count": 105, "signed_final_total_investment": 10500, "signed_final_settlement": {"invest": 10500, "refund": 0, "effective_invest": 10500, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_1", "source_at": "2026-11-20T04:55:11.789249+00:00", "source_receipt_sha256": "c1663ff814bc1cbba64c67007eac46b3d9e1921b2e6c6a80fff95255ac0c56b9", "signed_final_at": "2026-11-20T04:55:18.944360+00:00", "delivered_ticket_sha256": "d1b2f62a9e4c5220b18f40bcefd7ba5dbb7a38959f017577102c29d278f15b6d", "settled_ticket_sha256": "69734133966d6018bbf996756b2501b2ffd387e1eb1abf23352d5e04d192f8b2"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 4, "T3I-L": 4, "HPI-L": 1}, "ruled_neutral_share": 0.125} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（オギフシノネガイ）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 4, "second_pre_rank": 8, "third_pre_rank": 7, "winner_in_W": false, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [7, 5, 2], "rescues": ["WINNER_ROLE_RESCUE"], "supports": ["ORDERED_PAIR_ |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 4, "alternative_signals_that_had_winner_top": ["HPI-L ranked the winner #1"]} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `4b4b94007d28aa54`／Learning State `83d076b659f4`</sub>
