# 2026-11-28 KOC_07 詳細反省（自動・実購入なし）

- 公式着順：3-2-9-7-5（上位3頭 [3, 2, 9]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 3／2着 1／3着 2；W False・P2 False・P3 False
- Top3捕捉 3／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 1240／損益 540／PFS 177.1%
- 参照：{"revision": "KOC_07.r2", "ticket_sha256": "79b0270fae09d1c499b84b375b0241843118e4d30bab16ed09caef5f2138969d", "frozen_at": "2026-11-28T17:30:11.045178+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 3／2着 1／3着 2；W True・P2 True・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 12330／損益 6330／PFS 205.5%
- 参照：{"final_receipt_sha256": "9ee27cce0e9ae6c876f298bfe5269acab9e4c51e693d61b60a2680f09339fd59", "result_receipt_sha256": "38734ca37a9bd4ef4a3b105f4090d3d6cafcca2234f274937b41d512e8da11b0", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "f4e549d046afe7528e3718a7f3ddaf791df5fe9f30760b20f60ac17c40036665", "signed_final_ticket_count": 120, "signed_final_total_investment": 12000, "signed_final_settlement": {"invest": 12000, "refund": 0, "effective_invest": 12000, "payout": 12330, "pfs": 102.8}, "effective_revision": "REVISION_2", "source_at": "2026-11-28T09:05:06.191341+00:00", "source_receipt_sha256": "cc85931bb12a37621a85eabfbd8ee24e52ef65cb8a745b721007b75af6609c48", "signed_final_at": "2026-11-28T09:05:17.050542+00:00", "delivered_ticket_sha256": "3297096e2665bda29114e188436c991e8543dc1ab4ff11b3962b6bbab5f49577", "settled_ticket_sha256": "9ee27cce0e9ae6c876f298bfe5269acab9e4c51e693d61b60a2680f09339fd59"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 4, "TPI-L": 4, "SRI-L": 4, "T3I-L": 5, "HPI-L": 4}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（アイアンサイズ）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 3, "second_pre_rank": 1, "third_pre_rank": 2, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [3, 2, 9], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CONF |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_cov |
| CAPITAL | OK | {"pfs": 205.5, "profit_loss": 6330, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `65b89ec7bc39d3f6`／Learning State `76b83e6fad2a`</sub>
