# 2026-11-24 URW_08 詳細反省（自動・実購入なし）

- 公式着順：3-11-9-5-6（上位3頭 [3, 11, 9]）
- 距離帯：MIDDLE(1701-2100)／第一実質失敗：**PREDICTION_ROLE_P2**
- 正しく判断できた項目：winner_in_W, third_in_P3, winner_is_ticket_head

## PAPER

- 1着の事前順位 2／2着 12／3着 1；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 900／返還 0／払戻 280／損益 -620／PFS 31.1%
- 参照：{"revision": "URW_08.r2", "ticket_sha256": "0cc8c43e82e7cb1cba207d35e82adcf428e4cc5690341a1c7e8c4ddc00d55247", "frozen_at": "2026-11-24T15:16:23.397562+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 9／3着 2；W True・P2 False・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 False；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "af5cf7c64b4e107857dfc3ac4c17c612acfb833d6c38983c1f7c57fd3769280a", "result_receipt_sha256": "7549fdb9c73521b7a07db3933b60f0297db6df15d92c2f9e1eb5e93705b28eb6", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "924f07d21fc8be78026769f113fcda4003c6dde2bb7bd2b48b995266263c73f4", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-24T06:52:05.662414+00:00", "source_receipt_sha256": "76859d14c04ad649dd0eb49be87c5c598b10b5ca834fd4663b10bc1cb11f717f", "signed_final_at": "2026-11-24T06:52:20.343478+00:00", "delivered_ticket_sha256": "f6c3c4ae5fd3598abcfa4984a050f988127e6da1314189601141a755783b8d52", "settled_ticket_sha256": "af5cf7c64b4e107857dfc3ac4c17c612acfb833d6c38983c1f7c57fd3769280a"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 1, "HPI-L": 1}, "ruled_neutral_share": 0.003} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 1, "second_pre_rank": 9, "third_pre_rank": 2, "winner_in_W": true, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [3, 11, 9], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P3_ROLE |
| TICKET | ISSUE | {"head_local_p2": false, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 9} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `89f9ffe90eda7467`／Learning State `ebbf3fc2d514`</sub>
