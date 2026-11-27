# 2026-11-27 NGY_11 詳細反省（自動・実購入なし）

- 公式着順：1-10-9-6-12（上位3頭 [1, 10, 9]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 2／2着 1／3着 11；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 370／損益 -330／PFS 52.9%
- 参照：{"revision": "NGY_11.r2", "ticket_sha256": "dd61c60d0cfd383797ee20272bfbd9b775487d24b924c32714a115a045134daf", "frozen_at": "2026-11-27T19:30:07.835576+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 11／2着 1／3着 7；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 2010／損益 -3990／PFS 33.5%
- 参照：{"final_receipt_sha256": "874b4235b1825a43c0c6aea5d9c93f6ef68ed108f6714ee5d190ad217d543235", "result_receipt_sha256": "625ae1ad3f0e1f283e1398a68a4d6abbf444ecd5358cd35f334d41493c3799ed", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "0ee3b6aae1dad69e1f0d5017225afaea8b994e85f957585d07bcb6158753e5ab", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_1", "source_at": "2026-11-27T10:34:30.577599+00:00", "source_receipt_sha256": "be6517aa3946d5d371642776eebb6809481f7ab32f5211865c8e268455ce9125", "signed_final_at": "2026-11-27T10:34:45.205019+00:00", "delivered_ticket_sha256": "50f8344b32278548f984a3c4b7f777966586d0c2acb9bbeeee0a18e4734b3468", "settled_ticket_sha256": "874b4235b1825a43c0c6aea5d9c93f6ef68ed108f6714ee5d190ad217d543235"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 9, "TPI-L": 9, "SRI-L": 9, "T3I-L": 11, "HPI-L": 11}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（ウィットビーアビー）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 11, "second_pre_rank": 1, "third_pre_rank": 7, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [1, 10, 9], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CON |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 33.5, "profit_loss": -3990, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 11, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P1:HIT_BUT_LOSS | P1 | {"pfs": 33.5, "tickets": 60, "payout": 2010} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `38658248eb2e69ea`／Learning State `08ade7b49c08`</sub>
