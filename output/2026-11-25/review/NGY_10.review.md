# 2026-11-25 NGY_10 詳細反省（自動・実購入なし）

- 公式着順：10-2-4-7-9（上位3頭 [10, 2, 4]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：third_in_P3

## PAPER

- 1着の事前順位 9／2着 3／3着 2；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "NGY_10.r2", "ticket_sha256": "8027627d31c00cafbc692e6436c449d8ad006202be0abe4fba7049df94fd8fd4", "frozen_at": "2026-11-25T18:55:15.871916+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 12／2着 9／3着 2；W False・P2 False・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "3616a648702d2d3bd5c9a15824cfd754c464b23678d51e02e623dc4405391565", "result_receipt_sha256": "8c71de289b1ab17834af24a0faa60f8421df36c0f3a9b6406a911067d68b97fb", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "8bf35dabbebb540e323697d718bca69674fd1ffde9b8d2dfd7e08f7c7536edfa", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-25T10:32:09.895930+00:00", "source_receipt_sha256": "8732da445e855fc92a145d87cb1e20a7f44b41768dab83034086c7fb4be239fb", "signed_final_at": "2026-11-25T10:32:28.678870+00:00", "delivered_ticket_sha256": "036f9624be589294169017a0d8f1c949008cbc7cbe2e7402715c84c2e6e5685c", "settled_ticket_sha256": "3616a648702d2d3bd5c9a15824cfd754c464b23678d51e02e623dc4405391565"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 12, "TPI-L": 12, "SRI-L": 12, "T3I-L": 12, "HPI-L": 10}, "ruled_neutral_share": 0.078} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（マローソ）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 12, "second_pre_rank": 9, "third_pre_rank": 2, "winner_in_W": false, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [10, 2, 4], "rescues": [], "supports": ["P3_ROLE_CONFIRMED"], "misses": [ |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 12, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `573c95b2ce7f2424`／Learning State `16b1dee16ff2`</sub>
