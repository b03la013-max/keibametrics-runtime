# 2026-11-28 SAG_06 詳細反省（自動・実購入なし）

- 公式着順：1-4-6-9-7（上位3頭 [1, 4, 6]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 1／2着 3／3着 7；W True・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "SAG_06.r2", "ticket_sha256": "3431856b20576a5696f7039f82bfe89c8c277637caac9c72fe6fec2bb3d67cc7", "frozen_at": "2026-11-28T16:50:13.183830+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 5／2着 4／3着 2；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 3750／損益 -2250／PFS 62.5%
- 参照：{"final_receipt_sha256": "71f55833ab1ccbfc6212b10877aa0dd16898b8d3036668cebe1667ae23f91ef6", "result_receipt_sha256": "a2cb79e0a2e7c63ac7042cac58923f6fbf6ad893dce742aee0dcb24b9a68a964", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "39d347292c32391ffb124a44d9c4070a4d984b2838638d307f6800e185c403f5", "signed_final_ticket_count": 144, "signed_final_total_investment": 14400, "signed_final_settlement": {"invest": 14400, "refund": 0, "effective_invest": 14400, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-28T08:25:10.868808+00:00", "source_receipt_sha256": "4b61e37875e6f64779d39ece0d48de9e7b7b6f7fdc93ed695fa7b8e169ba5299", "signed_final_at": "2026-11-28T08:25:22.986308+00:00", "delivered_ticket_sha256": "bd9e3cf80da87faa3f063cc70a380a1a5ca7f4ea0832fac7368c240f9f605d3b", "settled_ticket_sha256": "71f55833ab1ccbfc6212b10877aa0dd16898b8d3036668cebe1667ae23f91ef6"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 5, "TPI-L": 5, "SRI-L": 6, "T3I-L": 2, "HPI-L": 8}, "ruled_neutral_share": 0.072} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（ミッキースワン）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 5, "second_pre_rank": 4, "third_pre_rank": 2, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [1, 4, 6], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CONF |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_cov |
| CAPITAL | ISSUE | {"pfs": 62.5, "profit_loss": -2250, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 5, "alternative_signals_that_had_winner_top": ["PAPER ◎ was the winner"]} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P1:HIT_BUT_LOSS | P1 | {"pfs": 62.5, "tickets": 60, "payout": 3750} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `d0b9c2d424ca3989`／Learning State `0661470503ce`</sub>
