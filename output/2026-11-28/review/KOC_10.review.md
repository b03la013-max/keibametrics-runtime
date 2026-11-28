# 2026-11-28 KOC_10 詳細反省（自動・実購入なし）

- 公式着順：11-4-6-5-12（上位3頭 [11, 4, 6]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 1／2着 3／3着 10；W True・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "KOC_10.r2", "ticket_sha256": "54fa1c6d949aa2988ffc5dd5dccec191328b692089890fbc0f48311b8a9a4a1c", "frozen_at": "2026-11-28T19:00:15.531171+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 2／3着 5；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 119370／損益 113370／PFS 1989.5%
- 参照：{"final_receipt_sha256": "6eb58cebaa6e02ca01e4025b742615a0bbdc9b4a0aeb73cb54e6ee1a70bb0ac9", "result_receipt_sha256": "5dcd0ffda6639f9f02821e4119b952437d22ee8b1eedf38162d8b1449432c37a", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "6d91ae1c12484c01b961d77e2b3703a9d68e9c6e7dcb2fe879767e124c45eddd", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 119370, "pfs": 765.2}, "effective_revision": "REVISION_2", "source_at": "2026-11-28T10:37:06.454178+00:00", "source_receipt_sha256": "02d8cd861532f981deafcc024f9237c475607191a7e00000920e2a4cb340b426", "signed_final_at": "2026-11-28T10:37:19.236326+00:00", "delivered_ticket_sha256": "4ab9e6ae74239556fd8a653111dd010537bdf0a4d3145557fb5c0d8c2257fdcb", "settled_ticket_sha256": "6eb58cebaa6e02ca01e4025b742615a0bbdc9b4a0aeb73cb54e6ee1a70bb0ac9"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 3, "SRI-L": 3, "T3I-L": 1, "HPI-L": 4}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 2, "third_pre_rank": 5, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [11, 4, 6], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_cov |
| CAPITAL | OK | {"pfs": 1989.5, "profit_loss": 113370, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `e9775347878953d9`／Learning State `6a1d5bf2c5dc`</sub>
