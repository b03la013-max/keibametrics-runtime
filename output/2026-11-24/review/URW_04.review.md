# 2026-11-24 URW_04 詳細反省（自動・実購入なし）

- 公式着順：3-2-1-4-6（上位3頭 [3, 2, 1]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 1／2着 6／3着 3；W True・P2 False・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 4840／損益 4140／PFS 691.4%
- 参照：{"revision": "URW_04.r2", "ticket_sha256": "1f9e5309edf27cc2d97f3d6f96079a33ca36133b5eef3e92a6cc1429bcaff174", "frozen_at": "2026-11-24T13:06:24.296450+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 3／2着 4／3着 5；W True・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 8660／損益 2660／PFS 144.3%
- 参照：{"final_receipt_sha256": "2d01a73c773c88327fdd9525b9320acf137d359739f52ad49dec1db266871ae9", "result_receipt_sha256": "a76779212d88bdf15cc54f9b97ae274ea334330a94d4dd174ea8f936181af54e", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "2638f5b2a50535acfbc1a5bc97039895ffaf18e24b75301192d54660ba37f920", "signed_final_ticket_count": 75, "signed_final_total_investment": 7500, "signed_final_settlement": {"invest": 7500, "refund": 0, "effective_invest": 7500, "payout": 23250, "pfs": 310.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-24T04:41:31.408545+00:00", "source_receipt_sha256": "0cc8b286488746e017f2e12e7bf564b6d8687f7d35542fafa487bbed965b5b96", "signed_final_at": "2026-11-24T04:41:40.713342+00:00", "delivered_ticket_sha256": "5a2ee6ed515e0cfe7f0fff2cf3b1977991cb3dbba74f6cc7421084e453d23a12", "settled_ticket_sha256": "2d01a73c773c88327fdd9525b9320acf137d359739f52ad49dec1db266871ae9"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 5, "TPI-L": 4, "SRI-L": 4, "T3I-L": 5, "HPI-L": 4}, "ruled_neutral_share": 0.247} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 3, "second_pre_rank": 4, "third_pre_rank": 5, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [3, 2, 1], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CONF |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | OK | {"pfs": 144.3, "profit_loss": 2660, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | {"ruled_neutral_share": 0.247} | ruled-neutral share falls below 15% without source changes | per-venue observation rate in forward_summary | CALCULATED share |

<sub>review sha256 `0e5dcbc80905ed1a`／Learning State `31e542c0053c`</sub>
