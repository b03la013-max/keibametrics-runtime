# 2026-11-24 URW_09 詳細反省（自動・実購入なし）

- 公式着順：7-5-9-6-4（上位3頭 [7, 5, 9]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 2／2着 5／3着 1；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 2400／損益 1700／PFS 342.9%
- 参照：{"revision": "URW_09.r2", "ticket_sha256": "3fbb5dc69a1811878bf87f69883d879daa24497c926e4adb2f31c803dcf4affc", "frozen_at": "2026-11-24T15:50:03.185029+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 3／2着 4／3着 1；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 15320／損益 9320／PFS 255.3%
- 参照：{"final_receipt_sha256": "c9f6c2c325f617550effb02a48daa9c43489d37b3e3ad3ee8576b7cdbf827dfe", "result_receipt_sha256": "1c76fa9ed3a16f688310619b7a8e2f82744b235bdb8912336c15ba8240542a83", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "a08c6b251fd82586ba82ea1163a0d37084a220fd3e2fbc1f403c61db5618c632", "signed_final_ticket_count": 144, "signed_final_total_investment": 14400, "signed_final_settlement": {"invest": 14400, "refund": 0, "effective_invest": 14400, "payout": 13120, "pfs": 91.1}, "effective_revision": "REVISION_2", "source_at": "2026-11-24T07:27:18.663303+00:00", "source_receipt_sha256": "99201ce132e8a4e61b3454c61eb08bd9748d30a0541daec0282fff99f736cfb1", "signed_final_at": "2026-11-24T07:27:32.625206+00:00", "delivered_ticket_sha256": "8c9ae1ca21de973e85704c8de64178a0783c8875b5b1884193028363100b274b", "settled_ticket_sha256": "c9f6c2c325f617550effb02a48daa9c43489d37b3e3ad3ee8576b7cdbf827dfe"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 2, "T3I-L": 7, "HPI-L": 2}, "ruled_neutral_share": 0.003} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 3, "second_pre_rank": 4, "third_pre_rank": 1, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [7, 5, 9], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | OK | {"pfs": 255.3, "profit_loss": 9320, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `bb34dd4325daf1d1`／Learning State `b6886bd7db64`</sub>
