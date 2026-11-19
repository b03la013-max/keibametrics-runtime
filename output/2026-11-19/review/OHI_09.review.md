# 2026-11-19 OHI_09 詳細反省（自動・実購入なし）

- 公式着順：8-13-4-5-14（上位3頭 [8, 13, 4]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**PREDICTION_ROLE_P2**
- 正しく判断できた項目：winner_in_W, third_in_P3, winner_is_ticket_head

## PAPER

- 1着の事前順位 3／2着 7／3着 6；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 900／返還 0／払戻 0／損益 -900／PFS 0.0%
- 参照：{"revision": "OHI_09.r2", "ticket_sha256": "46bd7babb0723a04fc75f36f563ad6bc919e26d53a0b3548e0fb67b2be647ec8", "frozen_at": "2026-11-19T18:10:05.161090+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 9／3着 5；W True・P2 False・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 False；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "efd2d592a2bad2d2f5b709af91c4ace518c162cddd1e79947773ae207b2deb8d", "result_receipt_sha256": "b17180a0282633cd3b726f0e800f2ba267ab57cff9dd49b5145c12069592fcf8", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "6f0d78ae3cda34d31c4510e123ee187338651a72eba3d631d8b12ee6b02066bf", "signed_final_ticket_count": 192, "signed_final_total_investment": 19200, "signed_final_settlement": {"invest": 19200, "refund": 0, "effective_invest": 19200, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": null, "signed_final_at": "2026-11-19T09:47:24.238190+00:00", "delivered_ticket_sha256": "ce6c22aadc44214509798358c3de9ff84d58ff76402b7ca6a699b4a8e9be6192", "settled_ticket_sha256": "efd2d592a2bad2d2f5b709af91c4ace518c162cddd1e79947773ae207b2deb8d"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 1, "HPI-L": 1}, "ruled_neutral_share": 0.113} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 1, "second_pre_rank": 9, "third_pre_rank": 5, "winner_in_W": true, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [8, 13, 4], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P3_ROLE |
| TICKET | ISSUE | {"head_local_p2": false, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": true, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 9} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `0df1b896dd7c1e03`／Learning State `783f1f91d306`</sub>
