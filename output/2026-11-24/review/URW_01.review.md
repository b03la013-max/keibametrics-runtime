# 2026-11-24 URW_01 詳細反省（自動・実購入なし）

- 公式着順：8-5-3-4-1（上位3頭 [8, 5, 3]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 1／2着 4／3着 6；W True・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 180／損益 -520／PFS 25.7%
- 参照：{"revision": "URW_01.r2", "ticket_sha256": "23f07feebea35d6542d0d32f78c83de0b7942e78c8172b92757f69b57afe2d42", "frozen_at": "2026-11-24T11:36:13.647575+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 3／3着 5；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 940／損益 -5060／PFS 15.7%
- 参照：{"final_receipt_sha256": "66d0f5b5618c25bbe4bd5712d0070cc454d855e84b33ceef02ee1440b6510aba", "result_receipt_sha256": "79ce07817188ea62446eb1ea77077e833feea08e4cee4abc5942df61ad383272", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "f4e124ad9584aa627de63d9e2c1b4fb330efd497873be7e8fb2551e2674148d3", "signed_final_ticket_count": 120, "signed_final_total_investment": 12000, "signed_final_settlement": {"invest": 12000, "refund": 0, "effective_invest": 12000, "payout": 1760, "pfs": 14.7}, "effective_revision": "REVISION_1", "source_at": "2026-11-24T02:40:21.086909+00:00", "source_receipt_sha256": "d0a8426b61dd1e8a3a8564be14216e10d69f96c751d90fedd982fa4ec5a89a9f", "signed_final_at": "2026-11-24T02:40:33.302426+00:00", "delivered_ticket_sha256": "ecbd9fd43b00abb8cc65cc559d3c5b1388b329cf72e6491aa5915f1a48ab036d", "settled_ticket_sha256": "66d0f5b5618c25bbe4bd5712d0070cc454d855e84b33ceef02ee1440b6510aba"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 2, "T3I-L": 1, "HPI-L": 2}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補5頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 3, "third_pre_rank": 5, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [8, 5, 3], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_CONFIRMED",  |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 15.7, "profit_loss": -5060, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 15.7, "tickets": 60, "payout": 940} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `79f97732c0a64920`／Learning State `b92cd1f46792`</sub>
