# 2026-11-26 NGY_04 詳細反省（自動・実購入なし）

- 公式着順：4-1-12-7-11（上位3頭 [4, 1, 12]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 2／2着 1／3着 4；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 8050／損益 7350／PFS 1150.0%
- 参照：{"revision": "NGY_04.r2", "ticket_sha256": "c9690a98d41f37490c391b7d41b2126807ed5342d5ae198bd1711cd1de3b169f", "frozen_at": "2026-11-26T15:40:12.368014+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 1／3着 5；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 13650／損益 7650／PFS 227.5%
- 参照：{"final_receipt_sha256": "63a3da53b086fef3bebb68cbba3949c2a4d3f5f68ace26a13c938164a28701bd", "result_receipt_sha256": "5985fb37847061bd2b7c4eba50614dcf77c65b030165ab3f945d06803f6e64f9", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "5fe123374a64e4d70ffd9eb471bdb89140fec1e27dd2d6ffc91848b0dfa386bf", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 51000, "pfs": 326.9}, "effective_revision": "REVISION_2", "source_at": "2026-11-26T07:17:14.445406+00:00", "source_receipt_sha256": "399eb852a84539a9c003308e2a62701402addfc91f4b5718a1309d5345da2f41", "signed_final_at": "2026-11-26T07:17:27.854599+00:00", "delivered_ticket_sha256": "19e6b7cdfc7a2f7cfb474943b158b0566543dfbf4824bdacf40048632e03353c", "settled_ticket_sha256": "63a3da53b086fef3bebb68cbba3949c2a4d3f5f68ace26a13c938164a28701bd"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 2, "T3I-L": 3, "HPI-L": 1}, "ruled_neutral_share": 0.075} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 1, "third_pre_rank": 5, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [4, 1, 12], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | OK | {"pfs": 227.5, "profit_loss": 7650, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `f0205e91b7648732`／Learning State `307ae7b72a15`</sub>
