# 2026-11-27 NGY_09 詳細反省（自動・実購入なし）

- 公式着順：9-12-6-2-1（上位3頭 [9, 12, 6]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_P2**
- 正しく判断できた項目：winner_in_W, third_in_P3, winner_is_ticket_head

## PAPER

- 1着の事前順位 2／2着 5／3着 1；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 470／損益 -230／PFS 67.1%
- 参照：{"revision": "NGY_09.r2", "ticket_sha256": "0d5170d5cb18b836069017a85056e6148484e60b928a76c3e15e4f0fe9760c32", "frozen_at": "2026-11-27T18:20:16.737257+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 12／3着 2；W True・P2 False・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 False；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "7473e033be6dbc0a02a46338d5c16698b0b89f0cb839881ad0035da6138e25dd", "result_receipt_sha256": "d72d93d063cf0e8c9b80839000322467c3833794befb71c4df392e1e1460c4d5", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "162c313ba78ad7c78815d7048fa9e08dbc7a38bece21f6ed5e96e40debbf2c30", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 330, "pfs": 2.1}, "effective_revision": "REVISION_2", "source_at": "2026-11-27T09:57:07.551469+00:00", "source_receipt_sha256": "c6973b605bf06a05078ef03be800e322b9fb1b282027691ee19393b03bd440d2", "signed_final_at": "2026-11-27T09:57:20.434835+00:00", "delivered_ticket_sha256": "7f0bd898f6d1c27fccd3c6cab591bf443c93fffa95180cf241c3710685b31e39", "settled_ticket_sha256": "7473e033be6dbc0a02a46338d5c16698b0b89f0cb839881ad0035da6138e25dd"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 1, "SRI-L": 1, "T3I-L": 3, "HPI-L": 1}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（マサハヤルージュ）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 1, "second_pre_rank": 12, "third_pre_rank": 2, "winner_in_W": true, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [9, 12, 6], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P3_ROLE_CONFIRMED"] |
| TICKET | ISSUE | {"head_local_p2": false, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 12} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `60aba6660e14fc95`／Learning State `b38f0ce7094c`</sub>
