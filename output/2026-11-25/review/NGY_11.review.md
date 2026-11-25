# 2026-11-25 NGY_11 詳細反省（自動・実購入なし）

- 公式着順：4-6-8-12-9（上位3頭 [4, 6, 8]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_P2**
- 正しく判断できた項目：winner_in_W, third_in_P3, winner_is_ticket_head

## PAPER

- 1着の事前順位 3／2着 12／3着 6；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 800／返還 0／払戻 0／損益 -800／PFS 0.0%
- 参照：{"revision": "NGY_11.r2", "ticket_sha256": "1eb307ae0685fc64fd9161378bd75189642d9d89fefdcfa6b5452e9ce017b462", "frozen_at": "2026-11-25T19:30:07.735652+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 10／3着 6；W True・P2 False・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 False；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "6fb91320913c3a444dc6b5ad1c86c30c0357fede95cbb3c5fd13c02c1ab3b9a7", "result_receipt_sha256": "b32899362e4fa92d9ce2d0df0aa9bdd20c31959556b0e45b9693d43d65d5e214", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "bdc4dad1601864f4ecf3c4ba4a5b7e608acfe9ed997a05df960406b9c4a2b947", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 31840, "pfs": 204.1}, "effective_revision": "REVISION_2", "source_at": "2026-11-25T11:07:06.873347+00:00", "source_receipt_sha256": "a12c347da75cc3bda73332b7d83716434d53c0c2969335525dda5c9d3a2ea88b", "signed_final_at": "2026-11-25T11:07:21.022339+00:00", "delivered_ticket_sha256": "a694ecd4f9b13d37ec7df64ba151205c02e57d68f5eff6a589756e152ad0ef73", "settled_ticket_sha256": "6fb91320913c3a444dc6b5ad1c86c30c0357fede95cbb3c5fd13c02c1ab3b9a7"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 2, "HPI-L": 1}, "ruled_neutral_share": 0.072} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 2, "second_pre_rank": 10, "third_pre_rank": 6, "winner_in_W": true, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [4, 6, 8], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P3_ROLE_ |
| TICKET | ISSUE | {"head_local_p2": false, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 10} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `3653dfca723b7f69`／Learning State `e228529b660a`</sub>
