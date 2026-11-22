# 2026-11-22 MIZ_08 詳細反省（自動・実購入なし）

- 公式着順：12-2-4-3-9（上位3頭 [12, 2, 4]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 1／2着 2／3着 3；W True・P2 True・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 2070／損益 1370／PFS 295.7%
- 参照：{"revision": "MIZ_08.r2", "ticket_sha256": "01a02c607048c3b222d3a93d6df2109f4e2bfa1c24aa43b1b556a25fb2ed8d5d", "frozen_at": "2026-11-22T15:20:10.754533+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 2／3着 5；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 6650／損益 650／PFS 110.8%
- 参照：{"final_receipt_sha256": "a00db139c0bdbc4d635beed1531b4968f1b184c70e00ddf1f42878b76b626334", "result_receipt_sha256": "6e51a33d8cff8d6a8b6c8eb265e98f4dd44d57eade1a294d2ee7920685f3a492", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "59c384a17cba1bc00ffc09fadc04cc04ceb768474b559c768972ffc19cacfb9a", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 4730, "pfs": 30.3}, "effective_revision": "REVISION_2", "source_at": "2026-11-22T06:57:18.419361+00:00", "source_receipt_sha256": "f60deb896473adb7e150ebe63828cf335610b7fea57e935c9509f9483f27fbf1", "signed_final_at": "2026-11-22T06:57:31.328121+00:00", "delivered_ticket_sha256": "ff7cde37f44483c4f58f3afc3f9c9c1690d8580d31b76743915205a715b7d2c0", "settled_ticket_sha256": "a00db139c0bdbc4d635beed1531b4968f1b184c70e00ddf1f42878b76b626334"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 2, "HPI-L": 1}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 2, "third_pre_rank": 5, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [12, 2, 4], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | OK | {"pfs": 110.8, "profit_loss": 650, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `457999ab7b173ed8`／Learning State `468562d6e211`</sub>
