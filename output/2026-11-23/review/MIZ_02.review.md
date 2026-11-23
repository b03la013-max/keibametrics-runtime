# 2026-11-23 MIZ_02 詳細反省（自動・実購入なし）

- 公式着順：3-6-5-7-2（上位3頭 [3, 6, 5]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**PREDICTION_ROLE_P2**
- 正しく判断できた項目：winner_in_W, third_in_P3, winner_is_ticket_head

## PAPER

- 1着の事前順位 1／2着 9／3着 7；W True・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 2120／損益 1420／PFS 302.9%
- 参照：{"revision": "MIZ_02.r2", "ticket_sha256": "0f26cacdedb257db51565e2837298e8294887907d56629dfe47e8a47050a15be", "frozen_at": "2026-11-23T11:26:04.955338+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 9／3着 7；W True・P2 False・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 False；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "226fe55731c02f655ed67f759df0e8c11ee2349cf47b8fd3ec63450afbd67005", "result_receipt_sha256": "5cfb5b8ce56d5cb9273c1c2a028f225d15f399f7ddf7c8ac593be113c965a697", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "203ffc402143bc49ba6e2ac8eca5862226dab7969b24a0958e83b508e3503c27", "signed_final_ticket_count": 120, "signed_final_total_investment": 12000, "signed_final_settlement": {"invest": 12000, "refund": 0, "effective_invest": 12000, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-23T03:02:11.519162+00:00", "source_receipt_sha256": "14a86709453f2de85f4d2b0d1f22d7623c8d266bab1ad7bf31d9a33429d0432a", "signed_final_at": "2026-11-23T03:02:23.112128+00:00", "delivered_ticket_sha256": "6fff82a37d3ed2d426f6fa115106387a09eef1ee2a6890dd400c393ddf767d1a", "settled_ticket_sha256": "226fe55731c02f655ed67f759df0e8c11ee2349cf47b8fd3ec63450afbd67005"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 1, "HPI-L": 2}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 1, "second_pre_rank": 9, "third_pre_rank": 7, "winner_in_W": true, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [3, 6, 5], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "ORDERED_ |
| TICKET | ISSUE | {"head_local_p2": false, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 9} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `0973e6f7cd0e8dd1`／Learning State `155df8d000a5`</sub>
