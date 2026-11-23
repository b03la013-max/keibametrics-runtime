# 2026-11-23 KNZ_06 詳細反省（自動・実購入なし）

- 公式着順：7-5-6-3-4（上位3頭 [7, 5, 6]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 6／2着 1／3着 3；W False・P2 False・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 900／返還 0／払戻 0／損益 -900／PFS 0.0%
- 参照：{"revision": "KNZ_06.r2", "ticket_sha256": "fc969a3a6baa992b8221f5de991cd85a1f9b4e66f56788e52454e328e1712670", "frozen_at": "2026-11-23T15:45:11.959192+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 10／2着 1／3着 2；W False・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "3d0e071776c1ed96a6b77e6f5a4ae135e8e0038d1437af5ac864c918c37f66c0", "result_receipt_sha256": "2c0d3c460e3410db320bdfde6c8617a33ac860fc7ab183052ce8a035a2f90d3a", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "6c64a6790304a646d2fd9f6167929717e065cfdc83b64eb8dc6a34fdcef802e3", "signed_final_ticket_count": 144, "signed_final_total_investment": 14400, "signed_final_settlement": {"invest": 14400, "refund": 0, "effective_invest": 14400, "payout": 480, "pfs": 3.3}, "effective_revision": "REVISION_2", "source_at": "2026-11-23T07:23:16.629558+00:00", "source_receipt_sha256": "4e3f3a03967a7530851c2d42556985d1d0667045b59034d0166d0a484b27ea44", "signed_final_at": "2026-11-23T07:23:30.163021+00:00", "delivered_ticket_sha256": "9b0e90c4c1953296ff87f81a7d033777e1d9e9955347ae262cdd9bbf78836d90", "settled_ticket_sha256": "3d0e071776c1ed96a6b77e6f5a4ae135e8e0038d1437af5ac864c918c37f66c0"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 10, "TPI-L": 7, "SRI-L": 10, "T3I-L": 6, "HPI-L": 7}, "ruled_neutral_share": 0.072} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（レグナム）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 10, "second_pre_rank": 1, "third_pre_rank": 2, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [7, 5, 6], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CONF |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 10, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `c5719f46108f5d22`／Learning State `3a29a34548e7`</sub>
