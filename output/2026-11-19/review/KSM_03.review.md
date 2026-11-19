# 2026-11-19 KSM_03 詳細反省（自動・実購入なし）

- 公式着順：10-3-1-6-9（上位3頭 [10, 3, 1]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 1／2着 6／3着 2；W True・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 False；Pair条件付き3着 None
- 投資 1600／返還 0／払戻 0／損益 -1600／PFS 0.0%
- 参照：{"revision": "KSM_03.r2", "ticket_sha256": "50a1bf38d2546ba9fd8a03bda51650180b3b938b6e0724933eb4d36d106ce51a", "frozen_at": "2026-11-19T10:40:12.920299+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 5／3着 2；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 12910／損益 6910／PFS 215.2%
- 参照：{"final_receipt_sha256": "e77cf0ed9f6d4f46e2a450277278c6dd4bb547cb456ae7d32181eb709cd5c843", "result_receipt_sha256": "195b0b4f2e421c518cd04486ca0e53169f72a171011969d7221132450e0d1212", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "066ca6ecdba063fb11627c0500cb9e70855ecc3298d6b7fdad9f2350f26f1330", "signed_final_ticket_count": 120, "signed_final_total_investment": 12000, "signed_final_settlement": {"invest": 12000, "refund": 0, "effective_invest": 12000, "payout": 12910, "pfs": 107.6}, "effective_revision": "REVISION_2", "source_at": null, "signed_final_at": "2026-11-19T02:15:24.703219+00:00", "delivered_ticket_sha256": "8092552800c46df801ba8c7d8665c437601e5d0c7af8a5800b9f3e12ac993e01", "settled_ticket_sha256": "e77cf0ed9f6d4f46e2a450277278c6dd4bb547cb456ae7d32181eb709cd5c843"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 1, "HPI-L": 1}, "ruled_neutral_share": 0.119} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 5, "third_pre_rank": 2, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [10, 3, 1], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P3_ROLE |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | OK | {"pfs": 215.2, "profit_loss": 6910, "hit_but_loss": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `09f3dce9766a7ee4`／Learning State `58f344137f0d`</sub>
