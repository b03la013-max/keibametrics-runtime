# 2026-11-20 KSM_01 詳細反省（自動・実購入なし）

- 公式着順：7-6-2-4-5（上位3頭 [7, 6, 2]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 1／2着 2／3着 3；W True・P2 True・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 480／損益 -220／PFS 68.6%
- 参照：{"revision": "KSM_01.r2", "ticket_sha256": "23aae1a447a1dec244e4594d490d24882046bfdfd274b1822be5c32d410aa7ff", "frozen_at": "2026-11-20T09:41:08.872312+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 3／2着 2／3着 5；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 1160／損益 -4840／PFS 19.3%
- 参照：{"final_receipt_sha256": "3e8acf47ac60bf28ddd9de741ea81862bcbfc71502d6068fd58553d1f0ea7636", "result_receipt_sha256": "25f0298a7f4e1fdd0e0fcf5d65a756fb7f8d4f9b3608e6534391888254745cb8", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "84c01beb8650a76b8f252315eef89115b907561641f790584305911aa111c81d", "signed_final_ticket_count": 90, "signed_final_total_investment": 9000, "signed_final_settlement": {"invest": 9000, "refund": 0, "effective_invest": 9000, "payout": 1160, "pfs": 12.9}, "effective_revision": "REVISION_1", "source_at": "2026-11-20T00:45:05.820001+00:00", "source_receipt_sha256": "6115f2a42e77665474eabc32b852ab58921df3564992d0bf24c819c0e3ca8d4d", "signed_final_at": "2026-11-20T00:45:12.635181+00:00", "delivered_ticket_sha256": "6e1bb70bb6f5a9c468aa363191b346b34083e5230cf085ead1cc03c7e706701c", "settled_ticket_sha256": "3e8acf47ac60bf28ddd9de741ea81862bcbfc71502d6068fd58553d1f0ea7636"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 3, "SRI-L": 3, "T3I-L": 2, "HPI-L": 3}, "ruled_neutral_share": 0.197} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（ブラックレイシ）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 3, "second_pre_rank": 2, "third_pre_rank": 5, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [7, 6, 2], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CONFIRMED", "ORD |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_cov |
| CAPITAL | ISSUE | {"pfs": 19.3, "profit_loss": -4840, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 19.3, "tickets": 60, "payout": 1160} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | {"ruled_neutral_share": 0.197} | ruled-neutral share falls below 15% without source changes | per-venue observation rate in forward_summary | CALCULATED share |

<sub>review sha256 `73f7a1e2cdf82b1c`／Learning State `a1fbcef67220`</sub>
