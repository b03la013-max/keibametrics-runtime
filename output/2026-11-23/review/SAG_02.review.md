# 2026-11-23 SAG_02 詳細反省（自動・実購入なし）

- 公式着順：10-5-6-8-3（上位3頭 [10, 5, 6]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 3／2着 5／3着 4；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "SAG_02.r2", "ticket_sha256": "7c80a26b53da4226b69dd2e3ac9d705e2de0be05d8e800d3d0075f47b74019e8", "frozen_at": "2026-11-23T15:15:07.961321+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 3／2着 1／3着 4；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 4360／損益 -1640／PFS 72.7%
- 参照：{"final_receipt_sha256": "222c15eaa7796558c08d5a77985be26fe4432401e319ce6f747efaa54f658f79", "result_receipt_sha256": "9d025031d3aa11ad39866d1e81c39fb321080e287c9b168224e9dab0dee081c3", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "c06295e113354c3cc48732c7641321236a063b7310e7c8817aadcbfa2c72d4ab", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 3280, "pfs": 24.8}, "effective_revision": "REVISION_2", "source_at": "2026-11-23T06:52:16.565740+00:00", "source_receipt_sha256": "0770ec9a8dc86169207be14aa3bb5a3c37f86420f90ae584f3a46bcbdb8b48dc", "signed_final_at": "2026-11-23T06:52:30.991474+00:00", "delivered_ticket_sha256": "b112f3a7e1804f82514b4b127215fcb1f64d50d640ca03b63f00f5e04530758a", "settled_ticket_sha256": "222c15eaa7796558c08d5a77985be26fe4432401e319ce6f747efaa54f658f79"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 4, "TPI-L": 3, "SRI-L": 4, "T3I-L": 5, "HPI-L": 3}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（ラヴァルス）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 3, "second_pre_rank": 1, "third_pre_rank": 4, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [10, 5, 6], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_CONFIRMED", |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 72.7, "profit_loss": -1640, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 72.7, "tickets": 60, "payout": 4360} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `24624e1bbc05b540`／Learning State `098264150af5`</sub>
