# 2026-11-19 OHI_06 詳細反省（自動・実購入なし）

- 公式着順：1-7-10-8-13（上位3頭 [1, 7, 10]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 1／2着 3／3着 11；W True・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 1600／返還 0／払戻 520／損益 -1080／PFS 32.5%
- 参照：{"revision": "OHI_06.r2", "ticket_sha256": "1a966092b067bad904f8c2397c10ec78e3b3387aeae8e13dc6d9f1d6287af326", "frozen_at": "2026-11-19T16:27:01.944819+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 3／3着 12；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 520／損益 -5480／PFS 8.7%
- 参照：{"final_receipt_sha256": "cb0ae65101a5976d7ca583de17dee03dd5dcbeae5a4bf7d57db1853ba87f10f9", "result_receipt_sha256": "123ca3894775c9fa05dddcf70a36406582f6bd1150fcf90c47df839f0fb8d25e", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "1c2389e0c7969ee403cc3e24616487917bfb518302aedcc42f387f887a7d75c6", "signed_final_ticket_count": 180, "signed_final_total_investment": 18000, "signed_final_settlement": {"invest": 18000, "refund": 0, "effective_invest": 18000, "payout": 27120, "pfs": 150.7}, "effective_revision": "REVISION_2", "source_at": null, "signed_final_at": "2026-11-19T08:03:47.671674+00:00", "delivered_ticket_sha256": "b5ecd1bf909eb957a5232a8ee099a1f8f6329f784960e3279d97e7cc9d863a7b", "settled_ticket_sha256": "cb0ae65101a5976d7ca583de17dee03dd5dcbeae5a4bf7d57db1853ba87f10f9"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 1, "HPI-L": 1}, "ruled_neutral_share": 0.111} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 3, "third_pre_rank": 12, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [1, 7, 10], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_co |
| CAPITAL | ISSUE | {"pfs": 8.7, "profit_loss": -5480, "hit_but_loss": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 8.7, "tickets": 60, "payout": 520} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `4a47cf428a01d474`／Learning State `ab2bbcd07e1d`</sub>
