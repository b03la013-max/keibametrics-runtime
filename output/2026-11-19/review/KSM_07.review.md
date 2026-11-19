# 2026-11-19 KSM_07 詳細反省（自動・実購入なし）

- 公式着順：10-8-4-5-7（上位3頭 [10, 8, 4]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 2／2着 3／3着 1；W False・P2 False・P3 False
- Top3捕捉 3／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 1050／損益 350／PFS 150.0%
- 参照：{"revision": "KSM_07.r2", "ticket_sha256": "cc8baa7451c73796d918442700379aaac7bb0862e7eba8a349ed6576f45f71da", "frozen_at": "2026-11-19T12:45:07.691258+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 3／3着 1；W True・P2 True・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 9880／損益 3880／PFS 164.7%
- 参照：{"final_receipt_sha256": "01e75fc5dc7b3b0761078622f2daee9ee0e828f7430ad7c0891c2a06da0eca60", "result_receipt_sha256": "3e6a74e4efdf8fba97d926a78c377dd4ff8713d50fbda2865aedbe3a87c0bd71", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "9385b9a9ae8ba636e3144cd2b696ec02e52bf1e8ef8076a3d5eebb9edec936ba", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 9880, "pfs": 74.8}, "effective_revision": "REVISION_2", "source_at": null, "signed_final_at": "2026-11-19T04:22:14.482848+00:00", "delivered_ticket_sha256": "bec8439f058285a47ec1d97613b6d1dd8ea748ce28f1fcceb990a12f5a2cf4b5", "settled_ticket_sha256": "01e75fc5dc7b3b0761078622f2daee9ee0e828f7430ad7c0891c2a06da0eca60"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 2, "T3I-L": 2, "HPI-L": 1}, "ruled_neutral_share": 0.107} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 3, "third_pre_rank": 1, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [10, 8, 4], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | OK | {"pfs": 164.7, "profit_loss": 3880, "hit_but_loss": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `0802b3857d2761e5`／Learning State `3750446c68c1`</sub>
