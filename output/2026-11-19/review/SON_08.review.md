# 2026-11-19 SON_08 詳細反省（自動・実購入なし）

- 公式着順：1-4-6-8-3（上位3頭 [1, 4, 6]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 2／2着 1／3着 5；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 140／損益 -560／PFS 20.0%
- 参照：{"revision": "SON_08.r2", "ticket_sha256": "79989c3712131ea178bae081a004866802da30eb4f087478c96997a4098c7186", "frozen_at": "2026-11-19T13:25:09.024678+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 8／2着 1／3着 2；W False・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "f0727f974dffef4f8585e08d640066aaa6aa843828fbee7549a9288ae89f8682", "result_receipt_sha256": "f3a89e766b68d9432618f7c6421b079e88db52bf31d70b3d8d0d38598883ac7c", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "234f7099e18d06bd06a6e523f9edf282721d63d36d2d37527696deefec4b3ec2", "signed_final_ticket_count": 105, "signed_final_total_investment": 10500, "signed_final_settlement": {"invest": 10500, "refund": 0, "effective_invest": 10500, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_1", "source_at": null, "signed_final_at": "2026-11-19T04:25:36.969735+00:00", "delivered_ticket_sha256": "b7510c6bb7a84088a581f03c7ead2dcb78a25845acbade7cf78406bef0865e75", "settled_ticket_sha256": "f0727f974dffef4f8585e08d640066aaa6aa843828fbee7549a9288ae89f8682"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 5, "TPI-L": 4, "SRI-L": 8, "T3I-L": 8, "HPI-L": 3}, "ruled_neutral_share": 0.116} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補4頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 8, "second_pre_rank": 1, "third_pre_rank": 2, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [1, 4, 6], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CONF |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": true, "ordered_exact_ticket_co |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 8, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `73883d3c772015dc`／Learning State `5f85a554801e`</sub>
