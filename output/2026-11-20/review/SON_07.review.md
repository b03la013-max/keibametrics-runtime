# 2026-11-20 SON_07 詳細反省（自動・実購入なし）

- 公式着順：1-4-3-2-6（上位3頭 [1, 4, 3]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 1／2着 2／3着 7；W True・P2 True・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 230／損益 -470／PFS 32.9%
- 参照：{"revision": "SON_07.r2", "ticket_sha256": "a0857d28ecaf737c5d518c74b9b62b4d49fb67877fd84995a549998f2ca04b5a", "frozen_at": "2026-11-20T12:56:33.286659+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 2／3着 5；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 11050／損益 5050／PFS 184.2%
- 参照：{"final_receipt_sha256": "c5a0114782167c5e55eb01cdebe03ad9a5594410163eddf8e8aba2215e8f8cbf", "result_receipt_sha256": "b57432849f91a8371428691d95a160c7120e08a88d13808b65fdb667c873b75c", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "4c98441e288f40020b360801d8418fe8b2cbc7ff9da4b454a84d69a672cceb88", "signed_final_ticket_count": 90, "signed_final_total_investment": 9000, "signed_final_settlement": {"invest": 9000, "refund": 0, "effective_invest": 9000, "payout": 11050, "pfs": 122.8}, "effective_revision": "REVISION_1", "source_at": "2026-11-20T03:58:54.469265+00:00", "source_receipt_sha256": "6a1b5180be8dc103d47ecac1252944025dfe1f1ab1cf0acfcf9cc880084a2373", "signed_final_at": "2026-11-20T03:59:01.229101+00:00", "delivered_ticket_sha256": "ec9e0a85462770de47ce270a2a29477dedbb02f6fbf16fdab610d84c277f68da", "settled_ticket_sha256": "c5a0114782167c5e55eb01cdebe03ad9a5594410163eddf8e8aba2215e8f8cbf"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 1, "HPI-L": 3}, "ruled_neutral_share": 0.118} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 2, "third_pre_rank": 5, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [1, 4, 3], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_CONFIRMED",  |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_cov |
| CAPITAL | OK | {"pfs": 184.2, "profit_loss": 5050, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `ff2ad325e5e49506`／Learning State `7b88412744d3`</sub>
