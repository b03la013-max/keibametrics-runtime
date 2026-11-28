# 2026-11-28 KOC_06 詳細反省（自動・実購入なし）

- 公式着順：1-7-2-3-6（上位3頭 [1, 7, 2]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 2／2着 7／3着 1；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 260／損益 -440／PFS 37.1%
- 参照：{"revision": "KOC_06.r2", "ticket_sha256": "958c5cc6bc381cf4738492a5b6530ad9379af75626509127a3f6ff664a55c1b0", "frozen_at": "2026-11-28T17:00:12.610174+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 6／3着 1；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 42350／損益 36350／PFS 705.8%
- 参照：{"final_receipt_sha256": "45d50d8a8a81c1936d13b36d8f040d6a637aec635093265b9f6952f599e2e12a", "result_receipt_sha256": "f002b89ce22a18087520da9193295d7d6f9bee70b3f108ca0fb50d6ce8bbaf49", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "512aad31367db013f381f3dc377626039612af61dbf4df7e7a172270cd79f9c4", "signed_final_ticket_count": 120, "signed_final_total_investment": 12000, "signed_final_settlement": {"invest": 12000, "refund": 0, "effective_invest": 12000, "payout": 42350, "pfs": 352.9}, "effective_revision": "REVISION_1", "source_at": "2026-11-28T08:04:41.452824+00:00", "source_receipt_sha256": "1e3d309ca8d1552ff4befe280e6e83afdfbf90f321e821849dafb66cf2696811", "signed_final_at": "2026-11-28T08:04:52.067797+00:00", "delivered_ticket_sha256": "30b356beee93d2b70f26d0aeb08af140c4fdad3d6631fb2d3551e47009e79362", "settled_ticket_sha256": "45d50d8a8a81c1936d13b36d8f040d6a637aec635093265b9f6952f599e2e12a"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 2, "T3I-L": 6, "HPI-L": 2}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 6, "third_pre_rank": 1, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [1, 7, 2], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_CONFIRMED",  |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_cov |
| CAPITAL | OK | {"pfs": 705.8, "profit_loss": 36350, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `7520297907a51fb2`／Learning State `b6b689f7424b`</sub>
