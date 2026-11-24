# 2026-11-24 NGY_10 詳細反省（自動・実購入なし）

- 公式着順：3-8-12-1-4（上位3頭 [3, 8, 12]）
- 距離帯：MIDDLE(1701-2100)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 1／2着 3／3着 10；W True・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "NGY_10.r2", "ticket_sha256": "f6e3672fb90f6c44924c72c19143a3340a2fe15a9df96bbe37899a06cc6db65c", "frozen_at": "2026-11-24T18:55:15.762603+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 1／3着 6；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 8110／損益 2110／PFS 135.2%
- 参照：{"final_receipt_sha256": "110b75e7c2cf430e5e48458b82c88a0f3b8f9f5573e4e2320516bc777191509f", "result_receipt_sha256": "514a71b73260238227c0badbd5cbde6cd1b3c09141ae36d641b783eb168b2958", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "b1e15159180e0cbf814a13a41573077d2f433b85d4f1f9993d2ac0ab907f90e5", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 6400, "pfs": 41.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-24T10:32:17.724132+00:00", "source_receipt_sha256": "b9a9f88aeddbb88b9201b3b8561562b98d9c2b279019d06bedf877a90739669a", "signed_final_at": "2026-11-24T10:32:33.024365+00:00", "delivered_ticket_sha256": "8f4343b013fa26feee7f6237b0aac552afdd9a0074bf1c16b1b18a90c4339d8e", "settled_ticket_sha256": "110b75e7c2cf430e5e48458b82c88a0f3b8f9f5573e4e2320516bc777191509f"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 3, "SRI-L": 3, "T3I-L": 7, "HPI-L": 2}, "ruled_neutral_share": 0.072} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 1, "third_pre_rank": 6, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [3, 8, 12], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | OK | {"pfs": 135.2, "profit_loss": 2110, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `e819edb89688cfcd`／Learning State `98f8b25d7544`</sub>
