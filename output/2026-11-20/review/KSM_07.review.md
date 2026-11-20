# 2026-11-20 KSM_07 詳細反省（自動・実購入なし）

- 公式着順：2-4-7-8-1（上位3頭 [2, 4, 7]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 2／2着 1／3着 3；W False・P2 False・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 930／損益 230／PFS 132.9%
- 参照：{"revision": "KSM_07.r2", "ticket_sha256": "edfb222d2e5bfc40b1f89e447d186908677dedd1cf5ca80d14f7a0c241e3856c", "frozen_at": "2026-11-20T12:45:43.887508+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 3／2着 4／3着 9；W True・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 1250／損益 -4750／PFS 20.8%
- 参照：{"final_receipt_sha256": "7696cf5ab38cbe3d498533dd5b0960c1d6f8d4abae49847f9b6cc322da299f9b", "result_receipt_sha256": "8ae7ebbe63668a2bc5f2270ca246b16f444e1bd5ba008e5b13ca2d758fd35d07", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "48f09b1625dc065709dbdeffaf28ffbf1c1bdbb4128375f4c2356ce3f55040c4", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 7170, "pfs": 54.3}, "effective_revision": "REVISION_1", "source_at": "2026-11-20T03:50:07.706549+00:00", "source_receipt_sha256": "6e60b9f501d6d9c1b5e3e18797b88f72ed2db85a10e39a6f0a667d7989e5fda0", "signed_final_at": "2026-11-20T03:50:15.941681+00:00", "delivered_ticket_sha256": "5042246b5e71fe0b835787c232d996ee09c5653b38345997acf08379f78bd877", "settled_ticket_sha256": "7696cf5ab38cbe3d498533dd5b0960c1d6f8d4abae49847f9b6cc322da299f9b"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 2, "SRI-L": 2, "T3I-L": 3, "HPI-L": 2}, "ruled_neutral_share": 0.117} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（ヤマニントゥルシー）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 3, "second_pre_rank": 4, "third_pre_rank": 9, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [2, 4, 7], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 20.8, "profit_loss": -4750, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 20.8, "tickets": 60, "payout": 1250} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `4abc479361ef948a`／Learning State `4076a2feae01`</sub>
