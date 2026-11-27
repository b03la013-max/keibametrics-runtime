# 2026-11-27 NGY_06 詳細反省（自動・実購入なし）

- 公式着順：12-7-10-9-3（上位3頭 [12, 7, 10]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 4／2着 1／3着 3；W False・P2 False・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "NGY_06.r2", "ticket_sha256": "00cc3c035ed29aeb89dd95b776f7417a728a4f4b078b03cc2a5f565a99a7e5b2", "frozen_at": "2026-11-27T16:45:03.558120+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 2／3着 4；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 4220／損益 -1780／PFS 70.3%
- 参照：{"final_receipt_sha256": "7e0c41edb6859aeb41e2e391b40619fb7a3ba77cfe1509c29487e70529a414f7", "result_receipt_sha256": "d76f77a883eb8c37cd84bea7b766256193c11fd19fc187bd05066921793ba935", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "999cdf59058f0c3dd378ada425437e6531a1ae3cf207f41c3243f127d8a1d4e8", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 4220, "pfs": 27.1}, "effective_revision": "REVISION_1", "source_at": "2026-11-27T07:47:30.323165+00:00", "source_receipt_sha256": "743831f463238f26f65e4dc83839c8a1cea08e5aa0294605431458d45d625e00", "signed_final_at": "2026-11-27T07:47:42.575968+00:00", "delivered_ticket_sha256": "5d57bcbd761226bc0bd967b49a1735be85eabdba61d47f949fdf8269652dd6bd", "settled_ticket_sha256": "7e0c41edb6859aeb41e2e391b40619fb7a3ba77cfe1509c29487e70529a414f7"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 1, "HPI-L": 1}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 2, "third_pre_rank": 4, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [12, 7, 10], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROL |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_cov |
| CAPITAL | ISSUE | {"pfs": 70.3, "profit_loss": -1780, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 70.3, "tickets": 60, "payout": 4220} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `36b95f15bb189e32`／Learning State `2fdcba10c2ae`</sub>
