# 2026-11-19 OHI_02 詳細反省（自動・実購入なし）

- 公式着順：9-4-5-11-10（上位3頭 [9, 4, 5]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 1／2着 3／3着 2；W True・P2 False・P3 False
- Top3捕捉 3／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 1600／返還 0／払戻 3960／損益 2360／PFS 247.5%
- 参照：{"revision": "OHI_02.r2", "ticket_sha256": "8f90b4b14d6950319f5a53ca35d38df843f9e604fabe515be049270a503111ac", "frozen_at": "2026-11-19T14:17:03.655965+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 3／3着 1；W True・P2 True・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 3060／損益 -2940／PFS 51.0%
- 参照：{"final_receipt_sha256": "20e8c9653e068b7ae2c4093245a30703e46194e6f3a6d187fbe3b8c74536131a", "result_receipt_sha256": "017f77b8cb9a87b5327e27b41c62dd5cdde15c35d214fb5f4764fa215ebd5a6a", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "3c865e92a8f9ae92b893c9d8ee34ba3fe4a07fb8fb660f40dda3c5010989ab58", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 3060, "pfs": 19.6}, "effective_revision": "REVISION_2", "source_at": null, "signed_final_at": "2026-11-19T05:53:43.916972+00:00", "delivered_ticket_sha256": "5282ed6944f7cd0088934f3572c2e202a48018b98512c06060868bce8d819e66", "settled_ticket_sha256": "20e8c9653e068b7ae2c4093245a30703e46194e6f3a6d187fbe3b8c74536131a"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 4, "HPI-L": 1}, "ruled_neutral_share": 0.112} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（サルトゥス）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 3, "third_pre_rank": 1, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [9, 4, 5], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 51.0, "profit_loss": -2940, "hit_but_loss": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 51.0, "tickets": 60, "payout": 3060} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `c85780926fd6fe4c`／Learning State `3fab9537a86d`</sub>
