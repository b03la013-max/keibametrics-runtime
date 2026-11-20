# 2026-11-20 OHI_04 詳細反省（自動・実購入なし）

- 公式着順：9-1-5-10-8（上位3頭 [9, 1, 5]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 1／2着 7／3着 8；W True・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 False；Pair条件付き3着 None
- 投資 1600／返還 0／払戻 0／損益 -1600／PFS 0.0%
- 参照：{"revision": "OHI_04.r2", "ticket_sha256": "29c82749a5372ffcce76b886f3d6c8f12c33e8921faa330ab963ffc38264f52b", "frozen_at": "2026-11-20T15:22:55.463455+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 5／3着 8；W True・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 1810／損益 -4190／PFS 30.2%
- 参照：{"final_receipt_sha256": "b71a6da80e57804e6f98e3971288746f78a7fe406fffa3bf2d4a58a33cb9c15b", "result_receipt_sha256": "27bda3523a7daa2e100a48d68913e2f5ee3da3302b6574948408a2514dd40284", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "6dc56afca5ea0ef0419908b1d85fb4462e53cb4fd9dce3bb3c9030e7383be82e", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 11000, "pfs": 83.3}, "effective_revision": "REVISION_2", "source_at": "2026-11-20T07:00:03.970037+00:00", "source_receipt_sha256": "f87a6805aa45285a4496befaf930642c9ae47324b550e49433d731f05f8adf26", "signed_final_at": "2026-11-20T07:00:12.239368+00:00", "delivered_ticket_sha256": "962b65c8b628c48f40a91532506540438b4650e679050538838d1541b9b0b86a", "settled_ticket_sha256": "b71a6da80e57804e6f98e3971288746f78a7fe406fffa3bf2d4a58a33cb9c15b"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 2, "T3I-L": 2, "HPI-L": 2}, "ruled_neutral_share": 0.11} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 5, "third_pre_rank": 8, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [9, 1, 5], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "ORDERED_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 30.2, "profit_loss": -4190, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 30.2, "tickets": 60, "payout": 1810} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `f91caddc56c606e0`／Learning State `f4c9228407ec`</sub>
