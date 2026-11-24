# 2026-11-24 NGY_05 詳細反省（自動・実購入なし）

- 公式着順：3-4-6-1-12（上位3頭 [3, 4, 6]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 1／2着 5／3着 7；W True・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "NGY_05.r2", "ticket_sha256": "6be64b236b6c5a2d6e7daa75d6dbef7f1b31ca8734210aff5a39ffd508c6c73b", "frozen_at": "2026-11-24T16:00:11.368261+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 4／3着 7；W True・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 1750／損益 -4250／PFS 29.2%
- 参照：{"final_receipt_sha256": "db9ace94c28c4cd51dd66b53ab0bb5cbdf0ce3bfcb30ba4b2fd75f97cda64f7d", "result_receipt_sha256": "65585e78cdf08ba5dd35a424bac49164c550c7adecdc17e2cf76e594c5f3c960", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "01764c23e628a159d767b6801d1fd0a017ee10e1155fe4946388f66105df9076", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 8720, "pfs": 66.1}, "effective_revision": "REVISION_2", "source_at": "2026-11-24T07:37:23.450534+00:00", "source_receipt_sha256": "f2ae0c3593f5f4cda71418f3371a77d46305fca07362d0c49c46a1a729461dc8", "signed_final_at": "2026-11-24T07:37:37.604451+00:00", "delivered_ticket_sha256": "d26a39b64e2fe9143e1a2050f66e064ebaaa141b6d1932e1d259f80f185b8ad7", "settled_ticket_sha256": "db9ace94c28c4cd51dd66b53ab0bb5cbdf0ce3bfcb30ba4b2fd75f97cda64f7d"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 3, "HPI-L": 1}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（シュタットパーク）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 4, "third_pre_rank": 7, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [3, 4, 6], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 29.2, "profit_loss": -4250, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 29.2, "tickets": 60, "payout": 1750} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `5a59cf01d50441e6`／Learning State `e1f3fea2befe`</sub>
