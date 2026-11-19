# 2026-11-19 KSM_10 詳細反省（自動・実購入なし）

- 公式着順：3-1-9-5-2（上位3頭 [3, 1, 9]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 5／2着 2／3着 9；W False・P2 True・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "KSM_10.r2", "ticket_sha256": "7e9b5a0e76dfe396ab8903b42d14165852ec7b29eb23d81166c23b219257a722", "frozen_at": "2026-11-19T14:25:01.205137+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 3／2着 2／3着 1；W True・P2 True・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 27710／損益 21710／PFS 461.8%
- 参照：{"final_receipt_sha256": "a5a1fcc65b9d9a4162defc50536a1decc36539431a8407199903b9ed95574bf0", "result_receipt_sha256": "77ce1aa51190875183041ca3d9f4a875fe56c12f33dd09c934521ac8ca0ea0af", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "0f11174ae192cd7e9f96b4d89a72cef3553619824d35c32be6cd7f520cf65afa", "signed_final_ticket_count": 120, "signed_final_total_investment": 12000, "signed_final_settlement": {"invest": 12000, "refund": 0, "effective_invest": 12000, "payout": 27710, "pfs": 230.9}, "effective_revision": "REVISION_1", "source_at": null, "signed_final_at": "2026-11-19T05:28:34.668551+00:00", "delivered_ticket_sha256": "ace4537a2ea00452bc7a8946ac17d0b5d78fcbc843ad4ab16d48e3ef6aca5bae", "settled_ticket_sha256": "a5a1fcc65b9d9a4162defc50536a1decc36539431a8407199903b9ed95574bf0"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 4, "TPI-L": 4, "SRI-L": 3, "T3I-L": 1, "HPI-L": 4}, "ruled_neutral_share": 0.115} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（コパノデーヴィド）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 3, "second_pre_rank": 2, "third_pre_rank": 1, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [3, 1, 9], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CONF |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | OK | {"pfs": 461.8, "profit_loss": 21710, "hit_but_loss": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `e2fc8f780e4fada7`／Learning State `c86c6cb870b1`</sub>
