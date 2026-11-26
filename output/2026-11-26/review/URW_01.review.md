# 2026-11-26 URW_01 詳細反省（自動・実購入なし）

- 公式着順：1-2-12-3-5（上位3頭 [1, 2, 12]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_P2**
- 正しく判断できた項目：winner_in_W, third_in_P3, winner_is_ticket_head

## PAPER

- 1着の事前順位 1／2着 9／3着 5；W True・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "URW_01.r2", "ticket_sha256": "ff4c310f001be1b075e8c7c9e56ce09cf08b71f32ffe4532fa5fb18f2f1054e0", "frozen_at": "2026-11-26T11:35:15.128335+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 3／2着 11／3着 6；W True・P2 False・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 False；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "094b0682ee6262673bb35a14254088b8c0d4a489ca489b8b2a237d5975c0de3f", "result_receipt_sha256": "8cbfa623c6563363ac2d0162aa0a2d8d93e70724a2e24a942c778d6af23e8765", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "8dff953b71f39deca48dcdebfd670afb3ee70a66bc3b65c5dfc07d9ad7df1b7d", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 2740, "pfs": 17.6}, "effective_revision": "REVISION_2", "source_at": "2026-11-26T03:11:14.639622+00:00", "source_receipt_sha256": "3fd0e100c700d389e6eba72426282a8162eb135953e8f7a8ef5c4661732bc605", "signed_final_at": "2026-11-26T03:11:27.485160+00:00", "delivered_ticket_sha256": "0608c0106b538f6e3d8e24eff79ce9ee1a27b8b1cd3138a366f5759ee57913da", "settled_ticket_sha256": "094b0682ee6262673bb35a14254088b8c0d4a489ca489b8b2a237d5975c0de3f"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 2, "SRI-L": 5, "T3I-L": 5, "HPI-L": 2}, "ruled_neutral_share": 0.072} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 3, "second_pre_rank": 11, "third_pre_rank": 6, "winner_in_W": true, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [1, 2, 12], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P3_ROLE |
| TICKET | ISSUE | {"head_local_p2": false, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 11} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `1f0b630f5e8aed3d`／Learning State `36315b300c6b`</sub>
