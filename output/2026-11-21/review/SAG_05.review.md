# 2026-11-21 SAG_05 詳細反省（自動・実購入なし）

- 公式着順：2-11-5-3-4（上位3頭 [2, 11, 5]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 1／2着 7／3着 4；W True・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 False；Pair条件付き3着 None
- 投資 1600／返還 0／払戻 0／損益 -1600／PFS 0.0%
- 参照：{"revision": "SAG_05.r2", "ticket_sha256": "e3b3ad782e2edb11d0c2bd0539e2869f99add5b41de94f38b31848da2e8f914f", "frozen_at": "2026-11-21T16:50:08.458323+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 4／2着 6／3着 9；W False・P2 True・P3 True
- Top3捕捉 0／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "da6148665b1a2f01c5a35b154b73272b7d678f615baf5c7fe5567d907144acb6", "result_receipt_sha256": "cbe2ecbfebf780e0eb8e302d6e8ef655ecd1405174edd22fd5ea4a7889a49377", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "7c66112ae6243a4d0a5566235aee86c5dc6d6f91b463c7a9a9918498af1049b0", "signed_final_ticket_count": 144, "signed_final_total_investment": 14400, "signed_final_settlement": {"invest": 14400, "refund": 0, "effective_invest": 14400, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-21T08:27:11.259490+00:00", "source_receipt_sha256": "2384b12547730ee52d72597aefee9dcc9f97b67d7d88b19102ed555fb704b950", "signed_final_at": "2026-11-21T08:27:20.343300+00:00", "delivered_ticket_sha256": "f0fc3cfb574f2f45a98054f079c2fba9d090c3396ec04d02c9ae4298982baebc", "settled_ticket_sha256": "da6148665b1a2f01c5a35b154b73272b7d678f615baf5c7fe5567d907144acb6"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 7, "SRI-L": 3, "T3I-L": 4, "HPI-L": 10}, "ruled_neutral_share": 0.129} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 4, "second_pre_rank": 6, "third_pre_rank": 9, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [2, 11, 5], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CON |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 4, "alternative_signals_that_had_winner_top": ["PAPER ◎ was the winner"]} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `f6331326bea21d00`／Learning State `fd12cc743589`</sub>
