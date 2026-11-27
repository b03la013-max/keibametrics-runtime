# 2026-11-27 URW_06 詳細反省（自動・実購入なし）

- 公式着順：5-2-11-6-4（上位3頭 [5, 2, 11]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 3／2着 4／3着 1；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "URW_06.r2", "ticket_sha256": "8a164e1a509a527bee8b49126bb19155d7a7a1851493ce8d17676a1320b12b37", "frozen_at": "2026-11-27T14:05:06.939600+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 2／3着 4；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 22710／損益 16710／PFS 378.5%
- 参照：{"final_receipt_sha256": "1cecdfd9614fa17bcfdba88fd8c4e05b04f769b26490c8daefcf06f871df47ab", "result_receipt_sha256": "38fc4e176dbe11a28994d579bfb9d586d4b8e493d7067f85ab7515baf1f44ab9", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "47782e83e6c6f24ecb4038b8298376c028f2c52d73597ee4aeef727c52c12bdd", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 22710, "pfs": 145.6}, "effective_revision": "REVISION_2", "source_at": "2026-11-27T05:42:10.638514+00:00", "source_receipt_sha256": "bb902dfede5b92941a050faa03bedec3c3bf921ae0f43e455ca6bb1b85fdc29e", "signed_final_at": "2026-11-27T05:42:24.243178+00:00", "delivered_ticket_sha256": "fffd765eb0b4e38b77167491f2860ddd0d3200b3b2a7557184c20f2680ebde14", "settled_ticket_sha256": "1cecdfd9614fa17bcfdba88fd8c4e05b04f769b26490c8daefcf06f871df47ab"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 3, "SRI-L": 3, "T3I-L": 2, "HPI-L": 2}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補6頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 2, "third_pre_rank": 4, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [5, 2, 11], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_cov |
| CAPITAL | OK | {"pfs": 378.5, "profit_loss": 16710, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `234da185667efd0a`／Learning State `e231a9696e1b`</sub>
