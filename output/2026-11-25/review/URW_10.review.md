# 2026-11-25 URW_10 詳細反省（自動・実購入なし）

- 公式着順：8-1-9-12-2（上位3頭 [8, 1, 9]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 1／2着 3／3着 10；W True・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "URW_10.r2", "ticket_sha256": "f8662fc55ccc530fb1fa1ecc6c255ad942b13ccb59b87815d0ef388544b76dd1", "frozen_at": "2026-11-25T16:25:13.280114+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 3／2着 2／3着 7；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 1070／損益 -4930／PFS 17.8%
- 参照：{"final_receipt_sha256": "d39e319d5c9d95945905a27e98896c4ca8c867b4caf2d0faff9af1985cc9be03", "result_receipt_sha256": "187e90d4a80854f4d723b46fb95ced44672dd969cfdf3a110cce1205abb98c22", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "1c41dfa844a4fa04775fb68fe97660d500d111cc7804f33dd19bb28dadad0b1b", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 9000, "pfs": 57.7}, "effective_revision": "REVISION_2", "source_at": "2026-11-25T08:02:19.517633+00:00", "source_receipt_sha256": "b87c892f7a4e4a5bab1d3ce6201bf70236a92c64eaf618393c7b9e49fde4440d", "signed_final_at": "2026-11-25T08:02:32.288128+00:00", "delivered_ticket_sha256": "035d914e1f6f8ceb68c9cb61c17244eabb621484379438262c8af24b944813f8", "settled_ticket_sha256": "d39e319d5c9d95945905a27e98896c4ca8c867b4caf2d0faff9af1985cc9be03"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 3, "T3I-L": 10, "HPI-L": 1}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（ウェーブスリープス）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 3, "second_pre_rank": 2, "third_pre_rank": 7, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [8, 1, 9], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 17.8, "profit_loss": -4930, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 17.8, "tickets": 60, "payout": 1070} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `0b69a2d55fa7af51`／Learning State `6cc5cf4513a2`</sub>
