# 2026-11-20 OHI_09 詳細反省（自動・実購入なし）

- 公式着順：11-9-4-3-1（上位3頭 [11, 9, 4]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 1／2着 2／3着 7；W True・P2 True・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 120／損益 -580／PFS 17.1%
- 参照：{"revision": "OHI_09.r2", "ticket_sha256": "3459a94f29872c7fe1047ee0f79b6ed948aef771c585698459466e418a068f9d", "frozen_at": "2026-11-20T18:11:25.202503+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 3／2着 1／3着 8；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 210／損益 -5790／PFS 3.5%
- 参照：{"final_receipt_sha256": "53ac2e0dab05881229457679a209daac6d3f7c7171e8c63ba87609e8ac1652b2", "result_receipt_sha256": "8056058968551443a557ecd9aed8cc753898fc9bede06c9f9a889566834582e6", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "3f7f01c93baef3dbd7e2886666453c1a24f4b2005d13439b54e30bf34370175f", "signed_final_ticket_count": 144, "signed_final_total_investment": 14400, "signed_final_settlement": {"invest": 14400, "refund": 0, "effective_invest": 14400, "payout": 1160, "pfs": 8.1}, "effective_revision": "REVISION_1", "source_at": "2026-11-20T09:15:47.461570+00:00", "source_receipt_sha256": "eb55381cafead4447a1596f00f204db7cae60465ebcac017a2828fd13785d52f", "signed_final_at": "2026-11-20T09:15:56.772573+00:00", "delivered_ticket_sha256": "ae2221636e7c26171667c24e879265889192badb8a264d8388c0793c44dd37ca", "settled_ticket_sha256": "53ac2e0dab05881229457679a209daac6d3f7c7171e8c63ba87609e8ac1652b2"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 2, "SRI-L": 3, "T3I-L": 3, "HPI-L": 4}, "ruled_neutral_share": 0.116} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 3, "second_pre_rank": 1, "third_pre_rank": 8, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [11, 9, 4], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CON |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 3.5, "profit_loss": -5790, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 3.5, "tickets": 60, "payout": 210} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `dac8562edce7da17`／Learning State `b00d4985f418`</sub>
