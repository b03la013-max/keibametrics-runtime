# 2026-11-28 SAG_11 詳細反省（自動・実購入なし）

- 公式着順：4-8-1-5-2（上位3頭 [4, 8, 1]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 1／2着 3／3着 4；W True・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 1290／損益 590／PFS 184.3%
- 参照：{"revision": "SAG_11.r2", "ticket_sha256": "e4d7de112835561c641ab0695d01ea3433c07454cf3aecc86c432a77f21d5909", "frozen_at": "2026-11-28T19:25:11.897672+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 4／3着 3；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 6440／損益 440／PFS 107.3%
- 参照：{"final_receipt_sha256": "cce28b88eed36c1f435bedf1c0240888919e9ebd20e38d6994ba5580ad692e30", "result_receipt_sha256": "6486222b1ae1940891749a876b2edc8da1ed1c10d3850266647abb54c69a37f4", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "6a16c369a240db7497a422dfd76e45bec1fd7a73fa5f4a3882e4b8897332e267", "signed_final_ticket_count": 105, "signed_final_total_investment": 10500, "signed_final_settlement": {"invest": 10500, "refund": 0, "effective_invest": 10500, "payout": 6440, "pfs": 61.3}, "effective_revision": "REVISION_2", "source_at": "2026-11-28T11:00:06.769985+00:00", "source_receipt_sha256": "15190ae8b72e922bf521c776fa554bd7d3d4cac141220e0e2b67cab4bd541081", "signed_final_at": "2026-11-28T11:00:17.516754+00:00", "delivered_ticket_sha256": "33c6ef95d2f376ff82662e881da984065b1b8c3060ca00510ba58ad7a5e2b575", "settled_ticket_sha256": "cce28b88eed36c1f435bedf1c0240888919e9ebd20e38d6994ba5580ad692e30"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 3, "HPI-L": 1}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（テクノダイヤモンド）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 4, "third_pre_rank": 3, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [4, 8, 1], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_CONFIRMED",  |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_cov |
| CAPITAL | OK | {"pfs": 107.3, "profit_loss": 440, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `e07e032762efe8ba`／Learning State `9330ac85106b`</sub>
