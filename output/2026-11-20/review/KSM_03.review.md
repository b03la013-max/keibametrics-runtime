# 2026-11-20 KSM_03 詳細反省（自動・実購入なし）

- 公式着順：2-7-6-8-4（上位3頭 [2, 7, 6]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 1／2着 3／3着 4；W True・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 6250／損益 5550／PFS 892.9%
- 参照：{"revision": "KSM_03.r2", "ticket_sha256": "3903fac61daca805fe1a9027e8cca586d7c17933bf47a8fe4ed202d1bcd1fa97", "frozen_at": "2026-11-20T10:41:35.891909+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 4／3着 5；W True・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 12340／損益 6340／PFS 205.7%
- 参照：{"final_receipt_sha256": "7b225c058db4f28247a35c9cb389c3f715270e895a3bec0ef9f0d3c3085a494f", "result_receipt_sha256": "e02388cfe67b52767b76903dfa2b85bdd5908eb1e5939a53b621e24738b5f5ed", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "6803878cf9aa5ec264c6d91e9526be7eb369fead309aad699ed280d72fdb5d23", "signed_final_ticket_count": 105, "signed_final_total_investment": 10500, "signed_final_settlement": {"invest": 10500, "refund": 0, "effective_invest": 10500, "payout": 12340, "pfs": 117.5}, "effective_revision": "REVISION_1", "source_at": "2026-11-20T01:43:58.331667+00:00", "source_receipt_sha256": "a55563d44cc129124e39a17932882b5bd427826484490eae50c0317e0b3e52a0", "signed_final_at": "2026-11-20T01:44:05.367015+00:00", "delivered_ticket_sha256": "b5257aaa85a642261f8ff45c549bb33eb6560938feb03293c59a982940d61258", "settled_ticket_sha256": "7b225c058db4f28247a35c9cb389c3f715270e895a3bec0ef9f0d3c3085a494f"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 1, "HPI-L": 1}, "ruled_neutral_share": 0.112} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 4, "third_pre_rank": 5, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [2, 7, 6], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_cov |
| CAPITAL | OK | {"pfs": 205.7, "profit_loss": 6340, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `88d014d610ffe280`／Learning State `98fc463aa5fc`</sub>
