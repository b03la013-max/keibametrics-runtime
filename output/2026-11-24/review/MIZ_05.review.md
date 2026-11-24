# 2026-11-24 MIZ_05 詳細反省（自動・実購入なし）

- 公式着順：8-2-10-9-3（上位3頭 [8, 2, 10]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**PREDICTION_ROLE_P2**
- 正しく判断できた項目：winner_in_W, third_in_P3, winner_is_ticket_head

## PAPER

- 1着の事前順位 1／2着 7／3着 9；W True・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "MIZ_05.r2", "ticket_sha256": "830b56763c1983a82f64821c61804de9fba283a3c86640fec82ab4c9bf21de01", "frozen_at": "2026-11-24T13:16:28.591566+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 8／3着 10；W True・P2 False・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 False；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "ecc231f3732d1907ce1a65f5fe2473cd742997d6a76bf8c3e61899defec921ea", "result_receipt_sha256": "a77e059a6723243b065ca5ff34128ed41aa5e2f6cd3a44c234638e2923fe31a6", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "4a1f84c7b7ebf6ac4e92265ef71b335cb0062e4b06fc07c701d850092db439b5", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-24T04:52:43.098342+00:00", "source_receipt_sha256": "b59e5ce836f2c861fa78a97a7cbefa643220f8acc965adfcd95dac66641ee113", "signed_final_at": "2026-11-24T04:52:56.203084+00:00", "delivered_ticket_sha256": "9a4bd99665ac6fe987c415a0df468ca969730aafe4d3ae68317a33c3c82eef81", "settled_ticket_sha256": "ecc231f3732d1907ce1a65f5fe2473cd742997d6a76bf8c3e61899defec921ea"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 3, "T3I-L": 4, "HPI-L": 1}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 2, "second_pre_rank": 8, "third_pre_rank": 10, "winner_in_W": true, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [8, 2, 10], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED"], "misses": ["P2_ROLE |
| TICKET | ISSUE | {"head_local_p2": false, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 8} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `0fdc95a71827b771`／Learning State `4a5c673baf26`</sub>
