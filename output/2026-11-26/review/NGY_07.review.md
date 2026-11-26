# 2026-11-26 NGY_07 詳細反省（自動・実購入なし）

- 公式着順：12-2-1-6-8（上位3頭 [12, 2, 1]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 10／2着 1／3着 2；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 1670／損益 970／PFS 238.6%
- 参照：{"revision": "NGY_07.r2", "ticket_sha256": "1667c78850549c2c4d3378baadf4831fd778aa23d047f89c1abd0d6b81bf6e4e", "frozen_at": "2026-11-26T17:20:19.964375+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 9／2着 6／3着 7；W False・P2 True・P3 True
- Top3捕捉 0／Top4捕捉 0；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "4245e46929c7fa0b99500a36f3656ba6d256a22284ea11cd85bd5c0c7627ff5b", "result_receipt_sha256": "76b15a4e9a647d73c04f504f269dde49a89cb113b3d7c3043280fe9e48bb5de7", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "83df4b81abb82ca55f3072a3b44b933724184645690043a44aab17b09ac4f6d0", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-26T08:55:09.230437+00:00", "source_receipt_sha256": "7973e02a19e18357b15e2689e39293b9872c83e76f5b3f85d7c4ffe141dd2ae5", "signed_final_at": "2026-11-26T08:55:22.470039+00:00", "delivered_ticket_sha256": "201edcb4205713b94e56d7ced2ff2168e7c8eb83576e111ba47dd828253fd7bb", "settled_ticket_sha256": "4245e46929c7fa0b99500a36f3656ba6d256a22284ea11cd85bd5c0c7627ff5b"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 9, "TPI-L": 10, "SRI-L": 10, "T3I-L": 10, "HPI-L": 12}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（ノブエイト）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 9, "second_pre_rank": 6, "third_pre_rank": 7, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [12, 2, 1], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CON |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 9, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `9152ce727729eca1`／Learning State `552cd8779e41`</sub>
