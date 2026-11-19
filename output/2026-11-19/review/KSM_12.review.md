# 2026-11-19 KSM_12 詳細反省（自動・実購入なし）

- 公式着順：6-9-2-1-8（上位3頭 [6, 9, 2]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：third_in_P3

## PAPER

- 1着の事前順位 3／2着 6／3着 1；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "KSM_12.r2", "ticket_sha256": "e28c18d32087ee6b4d11daeb204fe3a03ea3a9e8935fade4eba9e3690a833704", "frozen_at": "2026-11-19T15:35:05.342121+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 4／2着 9／3着 2；W False・P2 False・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "5b4665fd87abf22514ca42ca5cca38686021486ff046f40f7eb0939dbd964cee", "result_receipt_sha256": "e11cbcc36958f6c20fdf4db55d39499d9b07c336be8e98a43d67b0aeb1704715", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "61760fc5cfc7c6cf2472d746cbc521e12289d069eaa9a41be6a841190034e1de", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_1", "source_at": null, "signed_final_at": "2026-11-19T06:38:15.870947+00:00", "delivered_ticket_sha256": "1857a6729926b4db04964f3d88318e8f77d5d98cafbf102fa5faf9b827ac0847", "settled_ticket_sha256": "5b4665fd87abf22514ca42ca5cca38686021486ff046f40f7eb0939dbd964cee"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 3, "SRI-L": 4, "T3I-L": 4, "HPI-L": 4}, "ruled_neutral_share": 0.124} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（サートゥリア）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 4, "second_pre_rank": 9, "third_pre_rank": 2, "winner_in_W": false, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [6, 9, 2], "rescues": ["WINNER_ROLE_RESCUE"], "supports": ["P3_ROLE_CONFI |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": true, "ordered_exact_ticket_co |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 4, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `08c2df1828922db6`／Learning State `5c228c26be83`</sub>
