# 2026-11-17 OHI_12 詳細反省（自動・実購入なし）

- 公式着順：13-8-9-3-10（上位3頭 [13, 8, 9]）
- 距離帯：MIDDLE(1701-2100)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 5／2着 4／3着 8；W False・P2 False・P3 False
- Top3捕捉 0／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 900／返還 0／払戻 0／損益 -900／PFS 0.0%
- 参照：{"revision": "OHI_12.r2", "ticket_sha256": "071dacc4a7e4ad590a41459911f46ed65c3298d194d8ae8ab09888f26b78f1b2", "frozen_at": "2026-11-17T20:05:07.739622+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 3／2着 6／3着 9；W True・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 5840／損益 -160／PFS 97.3%
- 参照：{"final_receipt_sha256": "57ffb8d2f4440e64c30cee4f23b9cb699720d5df66bbe90fd796d4ac2e23d733", "result_receipt_sha256": "d25097d6081d745105dd3a777541d16bf02eedc1cf6875f1540d412ea57233da", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "308a2eeaec89881a8cdc76c40fb9ec5e273aca655114af0fcadb2d05f2059e92", "signed_final_ticket_count": 192, "signed_final_total_investment": 19200, "signed_final_settlement": {"invest": 19200, "refund": 0, "effective_invest": 19200, "payout": 27250, "pfs": 141.9}}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 4, "TPI-L": 4, "SRI-L": 4, "T3I-L": 6, "HPI-L": 5}, "ruled_neutral_share": 0.108} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補6頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 3, "second_pre_rank": 6, "third_pre_rank": 9, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [13, 8, 9], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CON |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_co |
| CAPITAL | ISSUE | {"pfs": 97.3, "profit_loss": -160, "hit_but_loss": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 97.3, "tickets": 60, "payout": 5840} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `de2b56df4890db7d`／Learning State `43e632300bf6`</sub>
