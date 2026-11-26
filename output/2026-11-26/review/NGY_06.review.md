# 2026-11-26 NGY_06 詳細反省（自動・実購入なし）

- 公式着順：11-9-5-1-8（上位3頭 [11, 9, 5]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_P2**
- 正しく判断できた項目：winner_in_W, third_in_P3, winner_is_ticket_head

## PAPER

- 1着の事前順位 6／2着 3／3着 10；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "NGY_06.r2", "ticket_sha256": "8fa7975eddc6d2f697662f255356413b213e373ce4150e9a28d1101293ed818f", "frozen_at": "2026-11-26T16:45:05.784668+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 3／2着 7／3着 5；W True・P2 False・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 False；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "4dbfbbb6c7f2e44f8f4802cb519d16e0e9b315d147a484dbce0ea1414c32fe08", "result_receipt_sha256": "5a95f90be8c7c1a7de6e3cb0a22cf41aaeab8c2b7534d609a55330fd36f48157", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "aecba3137ba2ad6e6a4d89e68e874566c97ea241335548ac4e97a32aaff0ac1d", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-26T08:22:22.021039+00:00", "source_receipt_sha256": "b3f7d63dcbcb6630f33a7995320744607e1fa75b63b90effbfb12462c5512f2e", "signed_final_at": "2026-11-26T08:22:35.715968+00:00", "delivered_ticket_sha256": "1dafb7882141eaff65396bb0daf07f8b23fcbf62b972c9c9e518a307b135bbd3", "settled_ticket_sha256": "4dbfbbb6c7f2e44f8f4802cb519d16e0e9b315d147a484dbce0ea1414c32fe08"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 2, "T3I-L": 1, "HPI-L": 2}, "ruled_neutral_share": 0.072} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（ファストフィール）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 3, "second_pre_rank": 7, "third_pre_rank": 5, "winner_in_W": true, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [11, 9, 5], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P3_ROLE |
| TICKET | ISSUE | {"head_local_p2": false, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 7} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `2ba915a07622b061`／Learning State `395f4e5a5db7`</sub>
