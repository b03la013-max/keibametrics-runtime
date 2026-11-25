# 2026-11-25 NGY_03 詳細反省（自動・実購入なし）

- 公式着順：8-9-10-12-5（上位3頭 [8, 9, 10]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 2／2着 1／3着 3；W False・P2 False・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 560／損益 -140／PFS 80.0%
- 参照：{"revision": "NGY_03.r2", "ticket_sha256": "2daa60ff22f54f8b980d10af6ea857a4b22673120abc4df3a75b07f2f56985ce", "frozen_at": "2026-11-25T15:05:15.683346+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 1／3着 4；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 1240／損益 -4760／PFS 20.7%
- 参照：{"final_receipt_sha256": "80542b59d3fd7624c5f302df5392646a117344b644c681ac607f39223b2aaa36", "result_receipt_sha256": "ace29f64223b61c9d2e70370f22fdd71b3c26dfd3cdf374b1230373bfb149252", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "7f56287d92a236dd2e77681b4e2449e378ae29d9872f8fd9ec07ae6e9c2169ab", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 800, "pfs": 5.1}, "effective_revision": "REVISION_2", "source_at": "2026-11-25T06:42:08.718545+00:00", "source_receipt_sha256": "3538815912de7c651d9b4fe25b0a3d8105b69f0b1cf75d89c349ebb4e008a578", "signed_final_at": "2026-11-25T06:42:22.108803+00:00", "delivered_ticket_sha256": "46170a55fed269b5655ca6a2dbc0c89e44dc04f02b4d50e5f21deca417d7836e", "settled_ticket_sha256": "80542b59d3fd7624c5f302df5392646a117344b644c681ac607f39223b2aaa36"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 3, "SRI-L": 5, "T3I-L": 2, "HPI-L": 3}, "ruled_neutral_share": 0.072} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 1, "third_pre_rank": 4, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [8, 9, 10], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 20.7, "profit_loss": -4760, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 20.7, "tickets": 60, "payout": 1240} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `572011f115aa0c6f`／Learning State `1489c7a76dc9`</sub>
