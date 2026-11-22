# 2026-11-22 SAG_09 詳細反省（自動・実購入なし）

- 公式着順：3-12-6-1-4（上位3頭 [3, 12, 6]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 1／2着 3／3着 2；W True・P2 False・P3 False
- Top3捕捉 3／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 520／損益 -180／PFS 74.3%
- 参照：{"revision": "SAG_09.r2", "ticket_sha256": "738951cfd2b4dc07ea088d1849e33c9a1687bdd0f1981bed0c5dd442d5e2237f", "frozen_at": "2026-11-22T18:55:06.216061+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 4／3着 1；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 3470／損益 -2530／PFS 57.8%
- 参照：{"final_receipt_sha256": "6c839f37ba723b44865c30599ff209d37adb85511d33ce0b4e2b82c840e7a25d", "result_receipt_sha256": "3caf69dcbf9aff63a0ec85b600e9fd266e74c5b50f95a336bb03b4aeb48a62aa", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "e2823a2cda62d5c987ad94e943aa33897601401e15b3278e65384ca396f1d359", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 3200, "pfs": 20.5}, "effective_revision": "REVISION_2", "source_at": "2026-11-22T10:30:17.132652+00:00", "source_receipt_sha256": "7cb65fc8409379908251051d9f2f4e603cc79a9a3a191c737fe3a8f08068a22d", "signed_final_at": "2026-11-22T10:30:30.432282+00:00", "delivered_ticket_sha256": "697b94dba1823ca44feea4e72f7a7c8112724696b8510b73309dc60f893c15cf", "settled_ticket_sha256": "6c839f37ba723b44865c30599ff209d37adb85511d33ce0b4e2b82c840e7a25d"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 2, "T3I-L": 6, "HPI-L": 3}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（オダイ）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 4, "third_pre_rank": 1, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [3, 12, 6], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_CONFIRMED", |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 57.8, "profit_loss": -2530, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 57.8, "tickets": 60, "payout": 3470} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `47f55d1e48fa2010`／Learning State `b54c5a3fe168`</sub>
