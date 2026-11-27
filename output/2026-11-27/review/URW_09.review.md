# 2026-11-27 URW_09 詳細反省（自動・実購入なし）

- 公式着順：5-3-2-4-9（上位3頭 [5, 3, 2]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 2／2着 3／3着 5；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "URW_09.r2", "ticket_sha256": "f5001dfcb4baf51a76b9c8380702dbc4b34faf862ea0708e7d6eaf27cad6919a", "frozen_at": "2026-11-27T15:50:03.812328+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 5／3着 7；W True・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 1290／損益 -4710／PFS 21.5%
- 参照：{"final_receipt_sha256": "4c78f4527b57779a35aa39974154cf82a2ff5a57bee6c00f90c7ed90caa86490", "result_receipt_sha256": "4cfe683adad5c2da7b82fd7e07ef6324529a18ce92325c418fa9764a798cb889", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "340fcaf5a71bc8c7d24709b411edfecd46fcbec5e8fe77dfb4bec80809b33ef3", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 15260, "pfs": 97.8}, "effective_revision": "REVISION_2", "source_at": "2026-11-27T07:27:19.656926+00:00", "source_receipt_sha256": "2ef55e464dfc5d983043b74649ad0ae44d7e45723f9a9908440c18f4e18014e2", "signed_final_at": "2026-11-27T07:27:32.131692+00:00", "delivered_ticket_sha256": "a63571ad1ed29fe57479715da62d1eb93278364932eb656dd54fde9a86151e1d", "settled_ticket_sha256": "4c78f4527b57779a35aa39974154cf82a2ff5a57bee6c00f90c7ed90caa86490"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 2, "T3I-L": 1, "HPI-L": 1}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 5, "third_pre_rank": 7, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [5, 3, 2], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 21.5, "profit_loss": -4710, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 21.5, "tickets": 60, "payout": 1290} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `6df6224ef5f21e74`／Learning State `5ddd10d28715`</sub>
