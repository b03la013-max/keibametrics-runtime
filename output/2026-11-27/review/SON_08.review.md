# 2026-11-27 SON_08 詳細反省（自動・実購入なし）

- 公式着順：6-5-4-7-3（上位3頭 [6, 5, 4]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 1／2着 2／3着 4；W True・P2 True・P3 False
- Top3捕捉 2／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 2110／損益 1410／PFS 301.4%
- 参照：{"revision": "SON_08.r2", "ticket_sha256": "fa621ed359aac5c4077db6e7ff2e424877e1b4c7645a2b90068c49e6d0aa15d5", "frozen_at": "2026-11-27T13:45:09.974557+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 5／3着 3；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 580／損益 -5420／PFS 9.7%
- 参照：{"final_receipt_sha256": "198478b5db668ca675e0983d75beb14c0b9dc804804fe57a53920b07828a5aa3", "result_receipt_sha256": "2943801592a3866b05c4bcf61c8aa265e89e421a911a950651f202dd3d83dce6", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "68d5e97d3a03dda3f4c95dac4c29ed4a46e5d7cd645154305c2b2c3cbe72f355", "signed_final_ticket_count": 90, "signed_final_total_investment": 9000, "signed_final_settlement": {"invest": 9000, "refund": 0, "effective_invest": 9000, "payout": 6260, "pfs": 69.6}, "effective_revision": "REVISION_1", "source_at": "2026-11-27T04:46:35.058320+00:00", "source_receipt_sha256": "9781e18ed52db1dc27580c60efbe6790cb7c01ca3b5a711fcb69cce19e207993", "signed_final_at": "2026-11-27T04:46:44.641259+00:00", "delivered_ticket_sha256": "cb89dff2f257af2b9961c463c3a5f29a1ca6d7e7c67984509a1d6dba1d4f51da", "settled_ticket_sha256": "198478b5db668ca675e0983d75beb14c0b9dc804804fe57a53920b07828a5aa3"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 2, "HPI-L": 1}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 5, "third_pre_rank": 3, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [6, 5, 4], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P3_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 9.7, "profit_loss": -5420, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 9.7, "tickets": 60, "payout": 580} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `91f24970ed42937b`／Learning State `4abcab2fa5eb`</sub>
