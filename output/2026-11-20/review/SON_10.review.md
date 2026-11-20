# 2026-11-20 SON_10 詳細反省（自動・実購入なし）

- 公式着順：7-10-11-5-2（上位3頭 [7, 10, 11]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 6／2着 2／3着 12；W False・P2 True・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "SON_10.r2", "ticket_sha256": "9283dde2b0ee47adfe8ac1475c1b98dcbf2da214fa7990cc9128fb15a94d571d", "frozen_at": "2026-11-20T14:35:51.534202+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 9／2着 1／3着 8；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "9348551224b5b3a1f8402e609f168a5d75ccde6fcee358ca0b6683bf3db439e1", "result_receipt_sha256": "8aba11c0f2c28ec3add1312f2fd58a962f8b5b8e697e86246384850531fb3dc4", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "8df60d2a048a578dbd9730951eec84a8fa9b95bf39f780ffd9bdfe91976108ab", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-20T06:13:34.088949+00:00", "source_receipt_sha256": "4825badafa4e2f7c4ebc933053e70a111a3253f19eb40e4f01b6ef65a78a661c", "signed_final_at": "2026-11-20T06:13:43.394877+00:00", "delivered_ticket_sha256": "3f95fa100d97ce6b41aa2c11f30e1e51c4aa486cade19ba1c5b5847f9d283061", "settled_ticket_sha256": "9348551224b5b3a1f8402e609f168a5d75ccde6fcee358ca0b6683bf3db439e1"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 6, "TPI-L": 5, "SRI-L": 8, "T3I-L": 3, "HPI-L": 5}, "ruled_neutral_share": 0.112} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補5頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 9, "second_pre_rank": 1, "third_pre_rank": 8, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [7, 10, 11], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CO |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 9, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `00ac584fa7bd01c2`／Learning State `f85c482f898c`</sub>
