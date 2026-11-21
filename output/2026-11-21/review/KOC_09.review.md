# 2026-11-21 KOC_09 詳細反省（自動・実購入なし）

- 公式着順：10-9-8-6-2（上位3頭 [10, 9, 8]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 2／2着 4／3着 5；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 800／返還 0／払戻 0／損益 -800／PFS 0.0%
- 参照：{"revision": "KOC_09.r2", "ticket_sha256": "903ae7ba987d64d638c6ed7bf9e8670483fc9a32cea408eaa6e3850402efb7e1", "frozen_at": "2026-11-21T18:35:09.879919+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 5／3着 3；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 9610／損益 3610／PFS 160.2%
- 参照：{"final_receipt_sha256": "490fc0326c3d8fed9cd31dcaf839acec7e584f2802db9f668af6a6c536e794c2", "result_receipt_sha256": "159c54b6fc582a401f1a7e34d5d4af8b0278a355b45f390b65195ebfa55d5396", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "05e4c50ba0d066e11e70a7c3c617975081c3d7cfe6c000576b84aec4170d0dca", "signed_final_ticket_count": 144, "signed_final_total_investment": 14400, "signed_final_settlement": {"invest": 14400, "refund": 0, "effective_invest": 14400, "payout": 9610, "pfs": 66.7}, "effective_revision": "REVISION_2", "source_at": "2026-11-21T10:10:05.976736+00:00", "source_receipt_sha256": "74f77a0f8a26716f8a4c562c3a628d0d29d441bddfdaf19f5ac53b8071e0c461", "signed_final_at": "2026-11-21T10:10:15.751068+00:00", "delivered_ticket_sha256": "a61a10bedd5f23514514d0dbff5f0aef62db5b401fba06c139a9a4eb071ad8c2", "settled_ticket_sha256": "490fc0326c3d8fed9cd31dcaf839acec7e584f2802db9f668af6a6c536e794c2"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 4, "TPI-L": 4, "SRI-L": 2, "T3I-L": 7, "HPI-L": 4}, "ruled_neutral_share": 0.122} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 5, "third_pre_rank": 3, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [10, 9, 8], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CON |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_cov |
| CAPITAL | OK | {"pfs": 160.2, "profit_loss": 3610, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `1a9613eeb260b86d`／Learning State `cc0ff244c770`</sub>
