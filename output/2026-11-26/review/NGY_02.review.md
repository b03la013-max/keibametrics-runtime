# 2026-11-26 NGY_02 詳細反省（自動・実購入なし）

- 公式着順：5-10-9-3-2（上位3頭 [5, 10, 9]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_P2**
- 正しく判断できた項目：winner_in_W, third_in_P3, winner_is_ticket_head

## PAPER

- 1着の事前順位 8／2着 11／3着 5；W False・P2 False・P3 False
- Top3捕捉 0／Top4捕捉 0；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "NGY_02.r2", "ticket_sha256": "bbc861c3c2399832d319ea60e7e1320ca64db8702bf4aac6ced9fcaf67dcbaa4", "frozen_at": "2026-11-26T14:30:19.381881+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 3／2着 8／3着 2；W True・P2 False・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 False；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "fee7844d40896c8d598a3566cbab1e008d0ababea80e8c01a6adb1f1a271c714", "result_receipt_sha256": "6ba4bc388167126a229042b6af6cf1a2d72c81bf4b3cec8a72662b754ad6e2d6", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "3c4099358b2ee21f6b0ba3b55eb1942aefd2256eb841d8870fd7e278acb99868", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-26T06:07:09.077531+00:00", "source_receipt_sha256": "9089956315c9e923357ac109751d67f05b98321277f15d8e5271db486f3c328e", "signed_final_at": "2026-11-26T06:07:22.542238+00:00", "delivered_ticket_sha256": "4aab113dd6c8cec0df68f8de4df92ca43a28b1454b58939992d2834b68e751f4", "settled_ticket_sha256": "fee7844d40896c8d598a3566cbab1e008d0ababea80e8c01a6adb1f1a271c714"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 4, "SRI-L": 2, "T3I-L": 5, "HPI-L": 3}, "ruled_neutral_share": 0.072} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 3, "second_pre_rank": 8, "third_pre_rank": 2, "winner_in_W": true, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [5, 10, 9], "rescues": ["P2_ROLE_RESCUE", "ORDERED_PAIR_RESCUE", "PAIR_TH |
| TICKET | ISSUE | {"head_local_p2": false, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 8} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `7e633ddc0e644f55`／Learning State `0c1892f3fd8e`</sub>
