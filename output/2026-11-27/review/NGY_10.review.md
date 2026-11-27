# 2026-11-27 NGY_10 詳細反省（自動・実購入なし）

- 公式着順：5-9-10-3-6（上位3頭 [5, 9, 10]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 5／2着 4／3着 7；W False・P2 False・P3 False
- Top3捕捉 0／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 800／返還 0／払戻 0／損益 -800／PFS 0.0%
- 参照：{"revision": "NGY_10.r2", "ticket_sha256": "ee9de850f0f43da38d6984038b6817a60712db023fb6c5712f127645b531c901", "frozen_at": "2026-11-27T18:55:04.973965+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 7／2着 3／3着 4；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "a144143d5be13003735594c51651a509c3bb95aa6bb5cd57ebeb8bfbe3a3b584", "result_receipt_sha256": "6b5cbb75865de0cbdf38fbec412f8ad3ab08a86c5ba1b06b58e0c899be9c2344", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "6c1278f59e3d2085f0f16df0232d83fb638e3d01a75998081f800cc53ea7ceb9", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_1", "source_at": "2026-11-27T09:59:38.169304+00:00", "source_receipt_sha256": "783cf44c8a17be11e0d63b0634f023bca3ab1c2521412e807c47e9dd31f2917f", "signed_final_at": "2026-11-27T09:59:51.531929+00:00", "delivered_ticket_sha256": "2839f0836d924c6e2246809848555b37f4bc75cd8553d2d0da3ca3f37cf41e18", "settled_ticket_sha256": "a144143d5be13003735594c51651a509c3bb95aa6bb5cd57ebeb8bfbe3a3b584"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 8, "TPI-L": 8, "SRI-L": 7, "T3I-L": 9, "HPI-L": 8}, "ruled_neutral_share": 0.072} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 7, "second_pre_rank": 3, "third_pre_rank": 4, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [5, 9, 10], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CON |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 7, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `1992b9915178f01e`／Learning State `88aa5b744d12`</sub>
