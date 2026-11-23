# 2026-11-23 MIZ_10 詳細反省（自動・実購入なし）

- 公式着順：10-1-2-8-6（上位3頭 [10, 1, 2]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 2／2着 1／3着 6；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 True
- 投資 900／返還 0／払戻 1740／損益 840／PFS 193.3%
- 参照：{"revision": "MIZ_10.r2", "ticket_sha256": "a902682adfc741d1e43342b3e11f222a730cd8723852da7cafdfd108bde87ed1", "frozen_at": "2026-11-23T16:10:15.610132+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 5／2着 1／3着 2；W False・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 1510／損益 -4490／PFS 25.2%
- 参照：{"final_receipt_sha256": "abe7860c57cce4f495f396e6da2bb8e01cab6baeec707dcacdad3c85c8b2dff7", "result_receipt_sha256": "a7554309baab901b76998e9ba299e209511b0664df9d638d1c1618ced1f0fdf9", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "9f8a888a9db5300d2193d330f248538888933738c085a71ab8aa69ff746c407f", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_1", "source_at": "2026-11-23T07:12:39.533667+00:00", "source_receipt_sha256": "d97bac2bc5c0ac30439769ab79d5377ab187fb89dad8c56f57cd13a073afded5", "signed_final_at": "2026-11-23T07:12:52.672303+00:00", "delivered_ticket_sha256": "227d8677bf336a5ee2a28ee83a2f928fc0f5bbdc8a2a6c8db146001b6366addc", "settled_ticket_sha256": "abe7860c57cce4f495f396e6da2bb8e01cab6baeec707dcacdad3c85c8b2dff7"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 2, "T3I-L": 5, "HPI-L": 2}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 5, "second_pre_rank": 1, "third_pre_rank": 2, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [10, 1, 2], "rescues": ["WINNER_ROLE_RESCUE", "ORDERED_PAIR_RESCUE", "PAI |
| TICKET | OK | {"head_local_p2": null, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cov |
| CAPITAL | ISSUE | {"pfs": 25.2, "profit_loss": -4490, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 5, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P1:HIT_BUT_LOSS | P1 | {"pfs": 25.2, "tickets": 60, "payout": 1510} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `0d95e48c6c30ac05`／Learning State `4411011f8b82`</sub>
