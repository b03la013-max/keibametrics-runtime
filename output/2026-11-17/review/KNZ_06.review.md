# 2026-11-17 KNZ_06 詳細反省（自動・実購入なし）

- 公式着順：8-5-4-1-2（上位3頭 [8, 5, 4]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**EXACT_ORIENTATION**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 3／2着 1／3着 7；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "KNZ_06.r2", "ticket_sha256": "1ecdf8a7e0fdacf4a3f580ea924c6d36ab0b6966c9a96a783480d014e3c64f1f", "frozen_at": "2026-11-17T16:20:07.632037+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 2／3着 11；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 480／損益 -5520／PFS 8.0%
- 参照：{"final_receipt_sha256": "34ca2085c3df84d2308a20ec9f8f5a77008321188795e1b84fb60725547ec3b7", "result_receipt_sha256": "9d6eec382160a06ed4e04bc718a981eae2746657445d32efb99558d800e23436", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "28794bb6233050e22207e56a203bd5794d7fdba270eb10d5bf1cf16750840f9b", "signed_final_ticket_count": 144, "signed_final_total_investment": 14400, "signed_final_settlement": {"invest": 14400, "refund": 0, "effective_invest": 14400, "payout": 840, "pfs": 5.8}}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 2, "SRI-L": 2, "T3I-L": 2, "HPI-L": 1}, "ruled_neutral_share": 0.11} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（ケーズグロリア）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 2, "third_pre_rank": 11, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [8, 5, 4], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_CONFIRMED",  |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_co |
| CAPITAL | ISSUE | {"pfs": 8.0, "profit_loss": -5520, "hit_but_loss": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 8.0, "tickets": 60, "payout": 480} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `bf5315d36cd9fcb0`／Learning State `699cfbf57703`</sub>
