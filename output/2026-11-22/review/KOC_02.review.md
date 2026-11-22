# 2026-11-22 KOC_02 詳細反省（自動・実購入なし）

- 公式着順：10-9-7-5-4（上位3頭 [10, 9, 7]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 2／2着 1／3着 6；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 True
- 投資 900／返還 0／払戻 1780／損益 880／PFS 197.8%
- 参照：{"revision": "KOC_02.r2", "ticket_sha256": "3e1a0367c231f71ed832c38cb4306d09c4438165b2ef6a21f16dbfd7bd8f11f6", "frozen_at": "2026-11-22T15:15:13.053989+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 1／3着 3；W True・P2 True・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 5590／損益 -410／PFS 93.2%
- 参照：{"final_receipt_sha256": "f1be25b2544496d3b1b726f949add6c755afdb22b22b9f408a6155368b168819", "result_receipt_sha256": "879713292e556c944a241d6e8ee6dd3cd7a450a257c27fb1b77a08746e683352", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "116688428224c13a9dade70a58523cde318359590f696201e9f5c7c334e758ff", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 3950, "pfs": 29.9}, "effective_revision": "REVISION_2", "source_at": "2026-11-22T06:52:05.512879+00:00", "source_receipt_sha256": "7aa7ccad2ffae44fa869646ca0558a2f6d75f20d23ea632aafba58fba095f0e1", "signed_final_at": "2026-11-22T06:52:18.100399+00:00", "delivered_ticket_sha256": "0f178f809c3ca56ebab8fc8a7e182334949fcc7f2a12bf54b147bae8d21141ae", "settled_ticket_sha256": "f1be25b2544496d3b1b726f949add6c755afdb22b22b9f408a6155368b168819"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 3, "T3I-L": 3, "HPI-L": 3}, "ruled_neutral_share": 0.072} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 1, "third_pre_rank": 3, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [10, 9, 7], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 93.2, "profit_loss": -410, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 93.2, "tickets": 60, "payout": 5590} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `ef9f620bb2c54782`／Learning State `273dedfa636d`</sub>
