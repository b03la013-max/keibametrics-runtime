# 2026-11-20 KSM_11 詳細反省（自動・実購入なし）

- 公式着順：4-10-1-9-11（上位3頭 [4, 10, 1]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 1／2着 4／3着 5；W True・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "KSM_11.r2", "ticket_sha256": "b61c63a86352409321953d7aeaf97bdb997527988660e47a47d2e8327af637f7", "frozen_at": "2026-11-20T15:00:49.547733+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 3／3着 6；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 3440／損益 -2560／PFS 57.3%
- 参照：{"final_receipt_sha256": "1c0cee05184d7c0004883fa89d54912ea9f98e36581bc90612c51c7516e1cb39", "result_receipt_sha256": "1a36599b4ae44b74c0c940ce4ba2b9bdadc0d4080bf797af25a38639e460f37b", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "b8b9a7fd8b36fb0806543e977eb9b1b1f2b96a5454a0fd41dc54f7db9f5f8611", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 3440, "pfs": 22.1}, "effective_revision": "REVISION_2", "source_at": "2026-11-20T06:36:09.307367+00:00", "source_receipt_sha256": "4bd935ffcf245c8920ef5796c225e3b126f1c0bf8e0b744f2acd505ad44c2a8b", "signed_final_at": "2026-11-20T06:36:19.558793+00:00", "delivered_ticket_sha256": "28b0208225362bd2d73a9892734dd82d6d3459800a46dfeccce6535b19271944", "settled_ticket_sha256": "1c0cee05184d7c0004883fa89d54912ea9f98e36581bc90612c51c7516e1cb39"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 5, "HPI-L": 1}, "ruled_neutral_share": 0.115} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 3, "third_pre_rank": 6, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [4, 10, 1], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_cov |
| CAPITAL | ISSUE | {"pfs": 57.3, "profit_loss": -2560, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 57.3, "tickets": 60, "payout": 3440} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `c6f06d0456514c1f`／Learning State `63d2cfa23baf`</sub>
