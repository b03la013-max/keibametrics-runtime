# 2026-11-18 OHI_04 詳細反省（自動・実購入なし）

- 公式着順：2-6-10-13-12（上位3頭 [2, 6, 10]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**EXACT_ORIENTATION**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 1／2着 6／3着 5；W True・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "OHI_04.r2", "ticket_sha256": "e9945a383eb00261f6330755e5f2a9174c1796f4bff66c5c5f5c2f1c5a6c521a", "frozen_at": "2026-11-18T15:23:08.394129+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 6／3着 10；W True・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 740／損益 -5260／PFS 12.3%
- 参照：{"final_receipt_sha256": "445e8fddf78e990bdc1458416b8898f5d4c2bdeee102cd7930a8d320c12ded2c", "result_receipt_sha256": "5ecd8c5886225f0d963991ff4645bb5355086a6548d6e4c94aa1d5d74206ba21", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "2a2f02b4d2991cd49febc152e6c0f31f3f4c3147577996f4563a71e115f2f4d7", "signed_final_ticket_count": 168, "signed_final_total_investment": 16800, "signed_final_settlement": {"invest": 16800, "refund": 0, "effective_invest": 16800, "payout": 3850, "pfs": 22.9}}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 3, "HPI-L": 1}, "ruled_neutral_share": 0.109} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補4頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 6, "third_pre_rank": 10, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [2, 6, 10], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P3_ROLE |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_co |
| CAPITAL | ISSUE | {"pfs": 12.3, "profit_loss": -5260, "hit_but_loss": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 12.3, "tickets": 60, "payout": 740} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `0b4b369d8c7ad0e3`／Learning State `a73d51024be3`</sub>
