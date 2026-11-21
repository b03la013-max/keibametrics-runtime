# 2026-11-21 SAG_09 詳細反省（自動・実購入なし）

- 公式着順：3-7-9-10-4（上位3頭 [3, 7, 9]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_P2**
- 正しく判断できた項目：winner_in_W, third_in_P3, winner_is_ticket_head

## PAPER

- 1着の事前順位 1／2着 5／3着 6；W True・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "SAG_09.r2", "ticket_sha256": "635f2a18465e93716a5785d7a362792f2a30d9d0934aff65d46b18477d66b4b2", "frozen_at": "2026-11-21T18:55:05.775906+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 9／3着 3；W True・P2 False・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 False；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "b533fb3e0a03b1ce3ba71c4c5a0736fb738cb833896c46d60c82cafcb0d0bbe9", "result_receipt_sha256": "14b18d5448e447a7f190bb489938cb7db759d3bd3d7a6f9f2846505589fb7e6a", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "04789e034014b63a19f8a74c3cadb975c4b53a51bde1850592ba450ce490a6d6", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-21T10:30:12.735981+00:00", "source_receipt_sha256": "8b6dc90f5f610aa2058b44227759ba505c1aa34cbcaa9746a47bfea2d12a8c25", "signed_final_at": "2026-11-21T10:30:21.234204+00:00", "delivered_ticket_sha256": "fa4e2dc49a887be4e62ca008cc9ae8a1fa96cfcb72526665b079243be5591311", "settled_ticket_sha256": "b533fb3e0a03b1ce3ba71c4c5a0736fb738cb833896c46d60c82cafcb0d0bbe9"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 3, "HPI-L": 1}, "ruled_neutral_share": 0.124} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（ダバイシュクレ）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 1, "second_pre_rank": 9, "third_pre_rank": 3, "winner_in_W": true, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [3, 7, 9], "rescues": ["P2_ROLE_RESCUE", "ORDERED_PAIR_RESCUE"], "support |
| TICKET | ISSUE | {"head_local_p2": false, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 9} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `9860f20c918aa530`／Learning State `23e511f8a6e0`</sub>
