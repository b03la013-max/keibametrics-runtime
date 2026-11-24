# 2026-11-24 NGY_11 詳細反省（自動・実購入なし）

- 公式着順：12-2-1-6-10（上位3頭 [12, 2, 1]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_P2**
- 正しく判断できた項目：winner_in_W, third_in_P3, winner_is_ticket_head

## PAPER

- 1着の事前順位 3／2着 5／3着 7；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "NGY_11.r2", "ticket_sha256": "bb1d30ad48d8f3d2b4bcc8e1e8fe598f2d4c5305855b2bacb5001eca0e12869f", "frozen_at": "2026-11-24T19:30:15.697731+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 7／3着 3；W True・P2 False・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 False；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "2afbf925c07bb74d6ff5955f69c49db9d1330c5b17e879b79c27129e982f74e5", "result_receipt_sha256": "12413fdcc87e609f0ee32dae6ae56dcd62ed515f733fd5b1c30455b91a144e78", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "646e1e7f5abedafb14ce689ed4298e4fa4be0c2f43e7bd90817561c0d81917dc", "signed_final_ticket_count": 144, "signed_final_total_investment": 14400, "signed_final_settlement": {"invest": 14400, "refund": 0, "effective_invest": 14400, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-24T11:07:21.672743+00:00", "source_receipt_sha256": "8f31c0c93c97aa5129e37e2a6c46223a3351dc5259348787a13dc8aaa4ecdf4d", "signed_final_at": "2026-11-24T11:07:41.089573+00:00", "delivered_ticket_sha256": "9204b08ccc2dadcb04d57c68a1a95bf9aa0dcdde6f748cc774774d302a5f36e0", "settled_ticket_sha256": "2afbf925c07bb74d6ff5955f69c49db9d1330c5b17e879b79c27129e982f74e5"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 2, "HPI-L": 3}, "ruled_neutral_share": 0.072} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 1, "second_pre_rank": 7, "third_pre_rank": 3, "winner_in_W": true, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [12, 2, 1], "rescues": ["P2_ROLE_RESCUE", "ORDERED_PAIR_RESCUE"], "suppor |
| TICKET | ISSUE | {"head_local_p2": false, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 7} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `e241def4fd6338eb`／Learning State `83daa1058314`</sub>
