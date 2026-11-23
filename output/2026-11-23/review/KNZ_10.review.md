# 2026-11-23 KNZ_10 詳細反省（自動・実購入なし）

- 公式着順：6-3-4-9-1（上位3頭 [6, 3, 4]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 2／2着 5／3着 4；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "KNZ_10.r2", "ticket_sha256": "f10d3f8c590232e88637a38cd6a2d014afec7c7ee05fc231ea02eeccb6d60acb", "frozen_at": "2026-11-23T18:11:10.403841+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 3／2着 4／3着 6；W True・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 47770／損益 41770／PFS 796.2%
- 参照：{"final_receipt_sha256": "65ef958fc4ab9faed6c033b26f8d6cdd54667b8a15d5a6ae1f331494d583a8dc", "result_receipt_sha256": "326ff8cfc7307a2a5113789b460d3892ca208da308c6f09d130172306c58330f", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "69070867c475b0e2db89fe5593e8eca803b0bfbfa10b93b6dc9060f6e1606b02", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 176920, "pfs": 1134.1}, "effective_revision": "REVISION_2", "source_at": "2026-11-23T09:46:14.128341+00:00", "source_receipt_sha256": "3adb16e5704300eefee5f92377c11445d79b8f14520a36edd08c3d6e7be52ee6", "signed_final_at": "2026-11-23T09:46:29.820818+00:00", "delivered_ticket_sha256": "d8a506c61a37138e41d4b2334fab05fa34e3b6e2d75ab5d0c698a521d03bdb6f", "settled_ticket_sha256": "65ef958fc4ab9faed6c033b26f8d6cdd54667b8a15d5a6ae1f331494d583a8dc"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 2, "SRI-L": 4, "T3I-L": 4, "HPI-L": 2}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 3, "second_pre_rank": 4, "third_pre_rank": 6, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [6, 3, 4], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | OK | {"pfs": 796.2, "profit_loss": 41770, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `1c476d2abd43dfdc`／Learning State `631ff26e20b5`</sub>
