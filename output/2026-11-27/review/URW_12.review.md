# 2026-11-27 URW_12 詳細反省（自動・実購入なし）

- 公式着順：8-3-2-5-7（上位3頭 [8, 3, 2]）
- 距離帯：MIDDLE(1701-2100)／第一実質失敗：**PREDICTION_ROLE_P2**
- 正しく判断できた項目：winner_in_W, third_in_P3, winner_is_ticket_head

## PAPER

- 1着の事前順位 3／2着 8／3着 1；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 900／返還 0／払戻 0／損益 -900／PFS 0.0%
- 参照：{"revision": "URW_12.r2", "ticket_sha256": "2b1dd849edb87ffcd6e2ef9608cff643956cc080daf806fb01dfe4526dffddac", "frozen_at": "2026-11-27T17:35:06.730423+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 3／2着 12／3着 1；W True・P2 False・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 False；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "1b5644bca2e8ee1aa40ff58ffe3d08ea75f95986ea4bc083a64b19cfd1258862", "result_receipt_sha256": "03e419ce6a6b74bfe1e6c8b484d5b99da0bc5a100de72a79339cc21e6b1dd1e2", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "8faf34f4c5f7fbd93187b598ad5b848d496bed0db08e5e2748d063d8c33a3dbe", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 6600, "pfs": 42.3}, "effective_revision": "REVISION_2", "source_at": "2026-11-27T09:11:10.191368+00:00", "source_receipt_sha256": "5e660591dc55412a286355e527efd5273ac1d9175d1114cb4fe48915d7c990c7", "signed_final_at": "2026-11-27T09:11:22.821186+00:00", "delivered_ticket_sha256": "c6b35526d6409fe3571b2fdaf7957f0b9ef8605a3caafc1a3aaba877b224f711", "settled_ticket_sha256": "1b5644bca2e8ee1aa40ff58ffe3d08ea75f95986ea4bc083a64b19cfd1258862"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 7, "TPI-L": 7, "SRI-L": 7, "T3I-L": 6, "HPI-L": 9}, "ruled_neutral_share": 0.003} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補5頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 3, "second_pre_rank": 12, "third_pre_rank": 1, "winner_in_W": true, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [8, 3, 2], "rescues": [], "supports": ["P3_ROLE_CONFIRMED"], "misses": [" |
| TICKET | ISSUE | {"head_local_p2": false, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 12} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `e9ef068674d35f97`／Learning State `fff5be866010`</sub>
