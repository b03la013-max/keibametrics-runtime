# 2026-11-27 NGY_12 詳細反省（自動・実購入なし）

- 公式着順：12-6-4-11-7（上位3頭 [12, 6, 4]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：third_in_P3, winner_is_ticket_head

## PAPER

- 1着の事前順位 4／2着 5／3着 8；W False・P2 False・P3 False
- Top3捕捉 0／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 900／返還 0／払戻 0／損益 -900／PFS 0.0%
- 参照：{"revision": "NGY_12.r2", "ticket_sha256": "fcede65d6f723da0c09ac33fd4ed87881f2941cadc1b8e6704059f52e787a81c", "frozen_at": "2026-11-27T20:05:18.408229+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 10／2着 7／3着 1；W False・P2 False・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 False；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "db4d6475735844add96867e06924c1b0183a41a4bec700bcf8256b0976837c5e", "result_receipt_sha256": "b478fce0e0580609b09544807b98e2c369deb7d8f743fe751e3a73ea408046ff", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "7cacd104b2a078b376c82b0bbb66376d5a1525e297c7869e4c86f97bde97ad48", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-27T11:41:09.262542+00:00", "source_receipt_sha256": "c9e0edefd0f881985aae88a92f31d08a09b95b253b9352fbbb2b344e889d5442", "signed_final_at": "2026-11-27T11:41:23.112733+00:00", "delivered_ticket_sha256": "ebc9daf24448df7e3ba6a40f760029cbf43635277839385108baf5ab57395587", "settled_ticket_sha256": "db4d6475735844add96867e06924c1b0183a41a4bec700bcf8256b0976837c5e"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 8, "TPI-L": 8, "SRI-L": 8, "T3I-L": 10, "HPI-L": 6}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 10, "second_pre_rank": 7, "third_pre_rank": 1, "winner_in_W": false, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [12, 6, 4], "rescues": [], "supports": ["P3_ROLE_CONFIRMED"], "misses": [ |
| TICKET | ISSUE | {"head_local_p2": false, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 10, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `e7b6b9ff9186c33c`／Learning State `8c40c57b949a`</sub>
