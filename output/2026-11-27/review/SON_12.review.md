# 2026-11-27 SON_12 詳細反省（自動・実購入なし）

- 公式着順：7-2-8-1-6（上位3頭 [7, 2, 8]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 2／2着 3／3着 1；W False・P2 False・P3 False
- Top3捕捉 3／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 1150／損益 450／PFS 164.3%
- 参照：{"revision": "SON_12.r2", "ticket_sha256": "2e015248c261e9e658af6bd7ce8f61151b76fa741cd4f4ef4e9214612c969b5d", "frozen_at": "2026-11-27T16:01:26.171888+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 4／2着 5／3着 1；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "03573f31a2228db55a6d5b9b3462afaa1a7ca81f9d126d073d5448795df52c99", "result_receipt_sha256": "7e87abc99f65a350971019909bce360f1bb6b3966b398b5e20a06a57d9ff5111", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "06d4a3d385600a6c38710f8b07154808aa2f3b3249b25c8fd8e5bd833404e000", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-27T07:36:14.360129+00:00", "source_receipt_sha256": "c7f8a65c1cd5d72b18ae2c59f1ad237536f70ee98a79cfbe2bdad83ad1f85b1e", "signed_final_at": "2026-11-27T07:36:27.496855+00:00", "delivered_ticket_sha256": "b055f2bdc585a504b26a36cb6343b4799dc301513d35a8b230b85f9d366b0c85", "settled_ticket_sha256": "03573f31a2228db55a6d5b9b3462afaa1a7ca81f9d126d073d5448795df52c99"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 1, "HPI-L": 1}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 4, "second_pre_rank": 5, "third_pre_rank": 1, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [7, 2, 8], "rescues": ["WINNER_ROLE_RESCUE", "ORDERED_PAIR_RESCUE", "PAIR |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 4, "alternative_signals_that_had_winner_top": ["F3S-L ranked the winner #1", "TPI-L ranked the winne | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `def815ca51d37621`／Learning State `4fe0417efc96`</sub>
