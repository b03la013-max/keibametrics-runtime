# 2026-11-24 NGY_07 詳細反省（自動・実購入なし）

- 公式着順：1-4-11-2-10（上位3頭 [1, 4, 11]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 2／2着 5／3着 9；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "NGY_07.r2", "ticket_sha256": "618cbad3b83817414d00550c5c76bb4092ea83da6e313be49e649dbc6c218a47", "frozen_at": "2026-11-24T17:10:13.324975+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 2／3着 9；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 12500／損益 6500／PFS 208.3%
- 参照：{"final_receipt_sha256": "61ac53e37985e68815ae67af34437b95a784aef30be3335f2f782e6f37f7c1ee", "result_receipt_sha256": "95eb42112115b3793877996fb10394f6c24df937acb30f5e7381093cfd2d5a6d", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "53d7c009d13a712084949167166854ec254d4c6ca611b042e2cfbf972eba3621", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 78500, "pfs": 503.2}, "effective_revision": "REVISION_2", "source_at": "2026-11-24T08:46:09.698800+00:00", "source_receipt_sha256": "a90337ead5a7c9f5772da704c680c18e41fc8fb327b4e512936ec109a1d72d9a", "signed_final_at": "2026-11-24T08:46:25.336117+00:00", "delivered_ticket_sha256": "bf42897168fc34863d730091e45e1b582f9d782415de7b54291a7304fed44c6f", "settled_ticket_sha256": "61ac53e37985e68815ae67af34437b95a784aef30be3335f2f782e6f37f7c1ee"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 1, "HPI-L": 1}, "ruled_neutral_share": 0.072} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 2, "third_pre_rank": 9, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [1, 4, 11], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | OK | {"pfs": 208.3, "profit_loss": 6500, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `205538326d8ed596`／Learning State `035ae7b867ad`</sub>
