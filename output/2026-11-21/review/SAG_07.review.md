# 2026-11-21 SAG_07 詳細反省（自動・実購入なし）

- 公式着順：4-2-6-1-5（上位3頭 [4, 2, 6]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 2／2着 1／3着 3；W False・P2 False・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 390／損益 -310／PFS 55.7%
- 参照：{"revision": "SAG_07.r2", "ticket_sha256": "53c188d623b6e8d139eaae176d1ab41038b7c18acd75b174d49afc36e049e93b", "frozen_at": "2026-11-21T17:55:08.196598+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 2／3着 3；W True・P2 True・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 620／損益 -5380／PFS 10.3%
- 参照：{"final_receipt_sha256": "ea3d93ce8734514797b467695dde014aa1d00f05c58d98c1249f78d8dff0b2a6", "result_receipt_sha256": "40aa1cf791fb02e869c14674fdf1d27ad9cb50c200e819aa5674a9c17bbc09d2", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "979ff2b793d8f788d4eb4bede122e0e30af91646779d53dfbb87ea8ca80bb7a7", "signed_final_ticket_count": 144, "signed_final_total_investment": 14400, "signed_final_settlement": {"invest": 14400, "refund": 0, "effective_invest": 14400, "payout": 620, "pfs": 4.3}, "effective_revision": "REVISION_1", "source_at": "2026-11-21T08:58:35.471542+00:00", "source_receipt_sha256": "e9a6c635478dbadc4c1e46a3dcfae85465f9287bac1cfee8ab043ca29d144ce0", "signed_final_at": "2026-11-21T08:58:44.234110+00:00", "delivered_ticket_sha256": "c814b6e451df075eebec55db814eba0f55d1ae9c0c57c1295d730d43dbd943fb", "settled_ticket_sha256": "ea3d93ce8734514797b467695dde014aa1d00f05c58d98c1249f78d8dff0b2a6"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 1, "HPI-L": 1}, "ruled_neutral_share": 0.11} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 2, "third_pre_rank": 3, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [4, 2, 6], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_cov |
| CAPITAL | ISSUE | {"pfs": 10.3, "profit_loss": -5380, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 10.3, "tickets": 60, "payout": 620} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `4a56054a75051f28`／Learning State `0663cffae4d8`</sub>
