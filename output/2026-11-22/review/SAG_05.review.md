# 2026-11-22 SAG_05 詳細反省（自動・実購入なし）

- 公式着順：7-10-1-8-11（上位3頭 [7, 10, 1]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 4／2着 1／3着 2；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 2670／損益 1970／PFS 381.4%
- 参照：{"revision": "SAG_05.r2", "ticket_sha256": "5e8c75d8a0211a6c225ff8c6cf9c474d13e863e0c2deae7058090a86f44a18fb", "frozen_at": "2026-11-22T16:50:13.300094+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 2／3着 4；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 2650／損益 -3350／PFS 44.2%
- 参照：{"final_receipt_sha256": "8ae506f0dc663f22a8fa03e0ca7005c04bef19ae281cc6922c0168595f259b79", "result_receipt_sha256": "d2988968cc07a136f4f5df790773fa66356742c3aa0a11effcdfd44cb2d07fcd", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "ce716ac596503f11b07f1ce7aeb2ed785a913f3e1f3b217a97d31d27ed54ab68", "signed_final_ticket_count": 144, "signed_final_total_investment": 14400, "signed_final_settlement": {"invest": 14400, "refund": 0, "effective_invest": 14400, "payout": 4980, "pfs": 34.6}, "effective_revision": "REVISION_1", "source_at": "2026-11-22T07:53:39.671504+00:00", "source_receipt_sha256": "c11ec86159db90b52abb902e292acb61541545fc4b3ee216451300368e04b740", "signed_final_at": "2026-11-22T07:53:53.190119+00:00", "delivered_ticket_sha256": "622590b096e4d4e98a24cb0f52b96ac53a3c4dc0a0b8181db8d78beb30ae9a49", "settled_ticket_sha256": "8ae506f0dc663f22a8fa03e0ca7005c04bef19ae281cc6922c0168595f259b79"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 2, "SRI-L": 1, "T3I-L": 2, "HPI-L": 1}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 2, "third_pre_rank": 4, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [7, 10, 1], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_CONFIRMED", |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 44.2, "profit_loss": -3350, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 44.2, "tickets": 60, "payout": 2650} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `97c916bc34c0dbaf`／Learning State `80c56293c353`</sub>
