# 2026-11-27 SON_07 詳細反省（自動・実購入なし）

- 公式着順：7-6-10-3-9（上位3頭 [7, 6, 10]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 3／2着 1／3着 5；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "SON_07.r2", "ticket_sha256": "805818d346f5b87ca2579bb51884880957da29f6cc48b4f436a779e9dc34f04a", "frozen_at": "2026-11-27T13:15:11.012879+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 3／3着 4；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 1210／損益 -4790／PFS 20.2%
- 参照：{"final_receipt_sha256": "5ecfa36bd7b777f719cd42d3f5074fddc6d601542fe8ac0ed3af975f84807910", "result_receipt_sha256": "d5421bcf27e44196f6b4ec0660738c25ca603e6df34fec01860284cce96647b1", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "f90b66668749292cc4fecc972eb2104be20774baeb2397faced09a8855838771", "signed_final_ticket_count": 120, "signed_final_total_investment": 12000, "signed_final_settlement": {"invest": 12000, "refund": 0, "effective_invest": 12000, "payout": 12310, "pfs": 102.6}, "effective_revision": "REVISION_2", "source_at": "2026-11-27T04:50:16.892294+00:00", "source_receipt_sha256": "223bdb0b82d58d08925521056dbd2bb693585e7361199718b1ab0eb9c5258453", "signed_final_at": "2026-11-27T04:50:28.452648+00:00", "delivered_ticket_sha256": "28413c816b7a359ed7784ff32129c5940d553840d2a3284905f0224c35140c49", "settled_ticket_sha256": "5ecfa36bd7b777f719cd42d3f5074fddc6d601542fe8ac0ed3af975f84807910"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 2, "HPI-L": 2}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補4頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 3, "third_pre_rank": 4, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [7, 6, 10], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 20.2, "profit_loss": -4790, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 20.2, "tickets": 60, "payout": 1210} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `6e0bf9fcb5367287`／Learning State `60a8cfd5e74c`</sub>
