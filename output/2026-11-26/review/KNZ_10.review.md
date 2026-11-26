# 2026-11-26 KNZ_10 詳細反省（自動・実購入なし）

- 公式着順：6-4-1-9-8（上位3頭 [6, 4, 1]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 2／2着 8／3着 4；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "KNZ_10.r2", "ticket_sha256": "aa99428dd7f467ee1259db5d5a86e2692ce80224c5dd7256c3a2f904e27b9460", "frozen_at": "2026-11-26T18:40:19.230826+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 6／3着 1；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 2870／損益 -3130／PFS 47.8%
- 参照：{"final_receipt_sha256": "c9468709d3e341cbeaf2490ca346f33637005e3278812d1a4961bac329bc6ca0", "result_receipt_sha256": "6ce0e6a680ad939b34460795a508d6227fc8fd9764e7b9008693fa38b60fc710", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "0947a06eb9e9162e01b3ddd2e83e986660c4bd37c885c2899643ce2ec3428105", "signed_final_ticket_count": 120, "signed_final_total_investment": 12000, "signed_final_settlement": {"invest": 12000, "refund": 0, "effective_invest": 12000, "payout": 7390, "pfs": 61.6}, "effective_revision": "REVISION_2", "source_at": "2026-11-26T10:17:19.351570+00:00", "source_receipt_sha256": "0110c39fd67ef353fb597e043d571be513b0045ba563e61870184d03a071f4fa", "signed_final_at": "2026-11-26T10:17:32.955542+00:00", "delivered_ticket_sha256": "9a33f9bf7a2fc14b88401990d798ca5a64076900a87f968b835af70f9ae45008", "settled_ticket_sha256": "c9468709d3e341cbeaf2490ca346f33637005e3278812d1a4961bac329bc6ca0"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 3, "SRI-L": 3, "T3I-L": 4, "HPI-L": 3}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（ビスクウィザード）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 6, "third_pre_rank": 1, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [6, 4, 1], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P3_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 47.8, "profit_loss": -3130, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 47.8, "tickets": 60, "payout": 2870} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `55db4482c70934e4`／Learning State `8268f4d4775e`</sub>
