# 2026-11-26 URW_07 詳細反省（自動・実購入なし）

- 公式着順：11-5-10-13-1（上位3頭 [11, 5, 10]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 4／2着 2／3着 1；W False・P2 True・P3 False
- Top3捕捉 2／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 900／返還 0／払戻 1780／損益 880／PFS 197.8%
- 参照：{"revision": "URW_07.r2", "ticket_sha256": "61b4f5c0c6a51a89bef92b7d400c70b038ae677b3e5d0cf61bf6a75595e729a2", "frozen_at": "2026-11-26T14:40:16.359449+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 8／2着 3／3着 2；W False・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "81dab1f0ea312da9f45f5252246da00c5eb16265009203ce9deed3ea5746caf5", "result_receipt_sha256": "a9170c3110d50319893905019d7df6812bac05da1c0a2b6049c8fec6ef9a24b5", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "ae9368bc41520f088bc6eb64628823f656b4f77e0250aed2e1c60a4ade797d48", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_1", "source_at": "2026-11-26T05:45:30.798470+00:00", "source_receipt_sha256": "ac79a8f9b2c58d63c12e33c700cec5d30ce792f072e72be61084630bfad198c7", "signed_final_at": "2026-11-26T05:45:43.753939+00:00", "delivered_ticket_sha256": "8d98f560d592cee05a064e7f613e813e7e76807fa311e3230b61ee469dcfd14e", "settled_ticket_sha256": "81dab1f0ea312da9f45f5252246da00c5eb16265009203ce9deed3ea5746caf5"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 6, "TPI-L": 7, "SRI-L": 6, "T3I-L": 10, "HPI-L": 5}, "ruled_neutral_share": 0.003} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補4頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 8, "second_pre_rank": 3, "third_pre_rank": 2, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [11, 5, 10], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CO |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 8, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `210075579b84b12a`／Learning State `8ee6a8426c91`</sub>
