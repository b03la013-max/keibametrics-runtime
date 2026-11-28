# 2026-11-28 KOC_02 詳細反省（自動・実購入なし）

- 公式着順：8-7-11-6-5（上位3頭 [8, 7, 11]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 2／2着 1／3着 4；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 440／損益 -260／PFS 62.9%
- 参照：{"revision": "KOC_02.r2", "ticket_sha256": "94d6ec58b0036d7d3d88b5d0c17a65b5d21b3c29aef5c11b2543ab6d9a5bc1e4", "frozen_at": "2026-11-28T14:45:12.075812+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 2／3着 6；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 1830／損益 -4170／PFS 30.5%
- 参照：{"final_receipt_sha256": "7297c441d82e0fdcadb26404cc2f1f1364d064ff13b1578cdbc60d1c3b13713f", "result_receipt_sha256": "24fdc40a7b02ea3048047f967f21f2ee1b16cf07ea4cb3b3746760feb4b2a58c", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "3605ffed2a0fb13f8175a20230fa06886ee1df5ac1c4347adbd483b6fb8c1162", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 5930, "pfs": 44.9}, "effective_revision": "REVISION_2", "source_at": "2026-11-28T06:22:05.039977+00:00", "source_receipt_sha256": "2241a28321ed27ef51d88d7c4fa5cfb88c0693ab21a66bf6801071a97262a077", "signed_final_at": "2026-11-28T06:22:19.137796+00:00", "delivered_ticket_sha256": "efc2fa6f4391278b725ce4947ee1e076581ed35b5f0fec4b82f1d0707858bd05", "settled_ticket_sha256": "7297c441d82e0fdcadb26404cc2f1f1364d064ff13b1578cdbc60d1c3b13713f"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 1, "SRI-L": 1, "T3I-L": 4, "HPI-L": 4}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 2, "third_pre_rank": 6, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [8, 7, 11], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CON |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 30.5, "profit_loss": -4170, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 30.5, "tickets": 60, "payout": 1830} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `1c2ec8f76c4cf9d4`／Learning State `65a062e51d25`</sub>
