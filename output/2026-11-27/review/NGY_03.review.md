# 2026-11-27 NGY_03 詳細反省（自動・実購入なし）

- 公式着順：2-1-12-6-8（上位3頭 [2, 1, 12]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_P2**
- 正しく判断できた項目：winner_in_W, third_in_P3, winner_is_ticket_head

## PAPER

- 1着の事前順位 1／2着 6／3着 2；W True・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 110／損益 -590／PFS 15.7%
- 参照：{"revision": "NGY_03.r2", "ticket_sha256": "94179f852fd3e497ab6d5b644ec6fabc1572c16d42dd142f55ecdd8ea684b93c", "frozen_at": "2026-11-27T15:05:17.019481+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 9／3着 2；W True・P2 False・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 False；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "b1fd616e006e1f2fc48aa5fc047d1e454a0bd2e009c0738b1c3c2710937c8207", "result_receipt_sha256": "e073cfcc056e9f2701c71a67070a048a617a27201a197934c79d2d337a27361e", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "1720ec288b650e93ae84ce0f58cf09799b5d4c1fd7297a7dbea2c98e46872210", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-27T06:42:13.503607+00:00", "source_receipt_sha256": "2dbcea4bd159342292c6a77568082b2c13c446dd336bf34bb64c0bc0fa8b181a", "signed_final_at": "2026-11-27T06:42:26.613993+00:00", "delivered_ticket_sha256": "71d275c91f8a8f44b75c7134a1f3949fd7cb57551818c7951d3d0a0c17de92d2", "settled_ticket_sha256": "b1fd616e006e1f2fc48aa5fc047d1e454a0bd2e009c0738b1c3c2710937c8207"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 1, "SRI-L": 3, "T3I-L": 2, "HPI-L": 4}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 1, "second_pre_rank": 9, "third_pre_rank": 2, "winner_in_W": true, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [2, 1, 12], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P3_ROLE |
| TICKET | ISSUE | {"head_local_p2": false, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 9} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `03086e81220865d5`／Learning State `de0288385496`</sub>
