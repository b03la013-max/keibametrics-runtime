# 2026-11-24 MIZ_10 詳細反省（自動・実購入なし）

- 公式着順：10-3-9-4-2（上位3頭 [10, 3, 9]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 1／2着 3／3着 2；W True・P2 False・P3 False
- Top3捕捉 3／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 1600／返還 0／払戻 1100／損益 -500／PFS 68.8%
- 参照：{"revision": "MIZ_10.r2", "ticket_sha256": "325b119c4faa2c6b02022fe9f901ff89f05b39fa7e028feb300a5416230521b9", "frozen_at": "2026-11-24T16:10:20.206432+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 2／3着 3；W True・P2 True・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 1100／損益 -4900／PFS 18.3%
- 参照：{"final_receipt_sha256": "ddc87548eb82229cd0863f0a6c012b7611e22abf5cac4e66b760ddd38ef09313", "result_receipt_sha256": "7533b9d7e5301a21702eb4c4e7743503bd99e68157f7847c85947908c9babef4", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "31bb8403d9fefc31062ffdafa8e1c77f2637d9cd39347fc52f74cd28fda3a1c8", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 860, "pfs": 6.5}, "effective_revision": "REVISION_2", "source_at": "2026-11-24T07:47:09.873418+00:00", "source_receipt_sha256": "a2dc0b11acd723680c309272d37355edcb7a9308c9ef72debda8a47f2ff0e080", "signed_final_at": "2026-11-24T07:47:24.025214+00:00", "delivered_ticket_sha256": "0c508ee8c6f61407ef9acb2d2d639e21858cec393653602e3301bd88caef1b80", "settled_ticket_sha256": "ddc87548eb82229cd0863f0a6c012b7611e22abf5cac4e66b760ddd38ef09313"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 2, "T3I-L": 3, "HPI-L": 2}, "ruled_neutral_share": 0.072} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 2, "third_pre_rank": 3, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [10, 3, 9], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_CONFIRMED", |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 18.3, "profit_loss": -4900, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 18.3, "tickets": 60, "payout": 1100} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `2eef2893d1e87e8d`／Learning State `c23399a6a7d8`</sub>
