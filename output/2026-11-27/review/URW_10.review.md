# 2026-11-27 URW_10 詳細反省（自動・実購入なし）

- 公式着順：1-7-4-6-11（上位3頭 [1, 7, 4]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_P2**
- 正しく判断できた項目：winner_in_W, third_in_P3, winner_is_ticket_head

## PAPER

- 1着の事前順位 1／2着 7／3着 3；W True・P2 False・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 900／返還 0／払戻 2110／損益 1210／PFS 234.4%
- 参照：{"revision": "URW_10.r2", "ticket_sha256": "dfdd23637830972fcf9295f0bbe64cb17df8f2059249cbcadf6426402bb0e309", "frozen_at": "2026-11-27T16:25:17.687957+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 8／3着 4；W True・P2 False・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 False；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "427fe2625cfbeca16b2de9f929a030acead5134fec366a9baaee2e3879d57b92", "result_receipt_sha256": "49a16aa99c08731995f15753ecc67f9a5c1c1b5a31092a2c17a1563a566f8635", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "01ad92f2d9dedc8d300122fce74ef2775aac51d779fad4ee2026f7aa04a24311", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_1", "source_at": "2026-11-27T07:28:20.327504+00:00", "source_receipt_sha256": "ff9a70d87478385089999384264f1cd08a65c0608dfaab689e155ff4ec746b73", "signed_final_at": "2026-11-27T07:28:32.844082+00:00", "delivered_ticket_sha256": "86dabe2ef940cee73d78dd3672e0434c804dbe91438178cce97bb72d7fa36a4a", "settled_ticket_sha256": "427fe2625cfbeca16b2de9f929a030acead5134fec366a9baaee2e3879d57b92"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 2, "HPI-L": 3}, "ruled_neutral_share": 0.003} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 2, "second_pre_rank": 8, "third_pre_rank": 4, "winner_in_W": true, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [1, 7, 4], "rescues": ["P2_ROLE_RESCUE", "ORDERED_PAIR_RESCUE"], "support |
| TICKET | ISSUE | {"head_local_p2": false, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 8} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `fc25a93de2127dce`／Learning State `62be6bdb2593`</sub>
