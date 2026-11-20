# 2026-11-20 OHI_12 詳細反省（自動・実購入なし）

- 公式着順：4-5-13-2-12（上位3頭 [4, 5, 13]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 3／2着 4／3着 5；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "OHI_12.r2", "ticket_sha256": "5b68fa7b5a1983cc221617b073e69acfefe861fcd97b00e590b6187e4536e1ac", "frozen_at": "2026-11-20T20:06:39.394210+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 4／3着 3；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 9130／損益 3130／PFS 152.2%
- 参照：{"final_receipt_sha256": "c674faa38bc18f7d661806a55d5075face1b6fff80fcd3df1d7016c9bd7e1760", "result_receipt_sha256": "7ed12bf1d83445eeab8827836c1bc227e17c692422cb1ebe1010b23778171bfc", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "13aa1a2996ec7fecafdf3a4b11ac1ba867d94328965e031cb4727c16886ade14", "signed_final_ticket_count": 180, "signed_final_total_investment": 18000, "signed_final_settlement": {"invest": 18000, "refund": 0, "effective_invest": 18000, "payout": 9130, "pfs": 50.7}, "effective_revision": "REVISION_1", "source_at": "2026-11-20T11:10:45.913663+00:00", "source_receipt_sha256": "0e08c14089789c1bc8819ee3e971f208eaffba2dbb241345e920cf9fb51db9f1", "signed_final_at": "2026-11-20T11:10:57.126527+00:00", "delivered_ticket_sha256": "8fa994642ee963f4df00bb50b73c5dc54ac24b6969355a90ef9a5521a543ba55", "settled_ticket_sha256": "c674faa38bc18f7d661806a55d5075face1b6fff80fcd3df1d7016c9bd7e1760"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 2, "T3I-L": 1, "HPI-L": 2}, "ruled_neutral_share": 0.113} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 4, "third_pre_rank": 3, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [4, 5, 13], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_cov |
| CAPITAL | OK | {"pfs": 152.2, "profit_loss": 3130, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `b986b9c5b4155c41`／Learning State `81fc570ec1b2`</sub>
