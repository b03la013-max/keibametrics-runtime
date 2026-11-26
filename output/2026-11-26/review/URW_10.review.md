# 2026-11-26 URW_10 詳細反省（自動・実購入なし）

- 公式着順：12-8-10-5-1（上位3頭 [12, 8, 10]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 6／2着 1／3着 5；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "URW_10.r2", "ticket_sha256": "1be9385a97ec1d0cc28755b69dcfb752798be9cbf8909a6748d4fe3a7db5e728", "frozen_at": "2026-11-26T16:25:24.761424+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 4／2着 1／3着 3；W False・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 1520／損益 -4480／PFS 25.3%
- 参照：{"final_receipt_sha256": "c930264fc2255a5377eaa562e45b9a2972939dd9aa8860e727692fb45c52499f", "result_receipt_sha256": "403980cebc432f81cbc8d5cb118e25de4a384744a4883fa2ea6d67533cfbebe4", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "16c12ff0e23fc8b2340170c21909bbe3930e23dd7672f0e62780df79e1075274", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-26T08:01:05.372974+00:00", "source_receipt_sha256": "4bfaa79a10d7d6dd0e0380c53c564c81d8ad84258ed0e15092d3cb045bd84660", "signed_final_at": "2026-11-26T08:01:17.918265+00:00", "delivered_ticket_sha256": "78f8d250afa71927d61badf4017c667b6678fec71e983de653e34dfc9bd340c0", "settled_ticket_sha256": "c930264fc2255a5377eaa562e45b9a2972939dd9aa8860e727692fb45c52499f"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 5, "TPI-L": 5, "SRI-L": 5, "T3I-L": 7, "HPI-L": 7}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補4頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 4, "second_pre_rank": 1, "third_pre_rank": 3, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [12, 8, 10], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CO |
| TICKET | OK | {"head_local_p2": null, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cov |
| CAPITAL | ISSUE | {"pfs": 25.3, "profit_loss": -4480, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 4, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P1:HIT_BUT_LOSS | P1 | {"pfs": 25.3, "tickets": 60, "payout": 1520} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `975bf7dc3b92196d`／Learning State `af283c2f4ad3`</sub>
