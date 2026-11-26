# 2026-11-26 KNZ_05 詳細反省（自動・実購入なし）

- 公式着順：1-2-5-6-8（上位3頭 [1, 2, 5]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 2／2着 4／3着 6；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "KNZ_05.r2", "ticket_sha256": "4849f7143f83e733a194aa1b74bd84bfc3d538866f993331c2c50ddb9c77b77f", "frozen_at": "2026-11-26T15:45:11.734848+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 2／3着 7；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 3570／損益 -2430／PFS 59.5%
- 参照：{"final_receipt_sha256": "94b1b65dc0f69a397dc1e87e3de6805cdbb614e77ef06aa22c1f7c307314d1fe", "result_receipt_sha256": "d98943af7a30d39d0621218e672356595d986e8a489c566549bb0e651a99f774", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "90e42bcf98a15380db266551a24b2b892d46fcd25fd6b49454e8d307b19f575b", "signed_final_ticket_count": 105, "signed_final_total_investment": 10500, "signed_final_settlement": {"invest": 10500, "refund": 0, "effective_invest": 10500, "payout": 3570, "pfs": 34.0}, "effective_revision": "REVISION_1", "source_at": "2026-11-26T06:48:40.823025+00:00", "source_receipt_sha256": "5119eb64b73ba8443710d5b3b73011a0dc34f875f73c87e23526b15a9aafc8a5", "signed_final_at": "2026-11-26T06:48:51.375908+00:00", "delivered_ticket_sha256": "29ed261005b6ca22bc21a1b8a947a33f7542b95512943706bd51d02d3e048cba", "settled_ticket_sha256": "94b1b65dc0f69a397dc1e87e3de6805cdbb614e77ef06aa22c1f7c307314d1fe"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 2, "HPI-L": 1}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（リバージュエル）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 2, "third_pre_rank": 7, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [1, 2, 5], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_CONFIRMED",  |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_cov |
| CAPITAL | ISSUE | {"pfs": 59.5, "profit_loss": -2430, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 59.5, "tickets": 60, "payout": 3570} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `6991af7c8bc8a9f3`／Learning State `edcf40998ce6`</sub>
