# 2026-11-27 URW_11 詳細反省（自動・実購入なし）

- 公式着順：6-4-11-1-13（上位3頭 [6, 4, 11]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：third_in_P3

## PAPER

- 1着の事前順位 8／2着 9／3着 1；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 890／損益 190／PFS 127.1%
- 参照：{"revision": "URW_11.r2", "ticket_sha256": "27b3e815da2e855485753bab3efd344a1c1afb1655cb4180ee4be9ce49cc34a6", "frozen_at": "2026-11-27T17:00:06.778889+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 5／2着 7／3着 1；W False・P2 False・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "0ff96176a54cafc76d2b3f39b982b3d88cfcff07a72cd968b4982c4b28b60951", "result_receipt_sha256": "5c7aef704d841e422d9c9d049fcd51a04e08ca02f6969e142150b9493389901a", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "a7891dbfb0b58dc5662686135386d61420e0db077e5f9610d26041cab44021bf", "signed_final_ticket_count": 180, "signed_final_total_investment": 18000, "signed_final_settlement": {"invest": 18000, "refund": 0, "effective_invest": 18000, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-27T08:37:09.028834+00:00", "source_receipt_sha256": "dd5c6d3b49d2e325e11f7cc7dc5d3bdc6ec2eb36e987fccc48d95bb5ebc94867", "signed_final_at": "2026-11-27T08:37:23.158651+00:00", "delivered_ticket_sha256": "2ecec2677ee82e050d3f1f6fe60a1330c1e0afb5f1b018bfade54130f138db5e", "settled_ticket_sha256": "0ff96176a54cafc76d2b3f39b982b3d88cfcff07a72cd968b4982c4b28b60951"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 6, "TPI-L": 6, "SRI-L": 6, "T3I-L": 8, "HPI-L": 6}, "ruled_neutral_share": 0.002} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補4頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 5, "second_pre_rank": 7, "third_pre_rank": 1, "winner_in_W": false, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [6, 4, 11], "rescues": ["P2_ROLE_RESCUE"], "supports": ["P3_ROLE_CONFIRME |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 5, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `7a02e80dd152203e`／Learning State `e35a1ee1431b`</sub>
