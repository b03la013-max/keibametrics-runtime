# 2026-11-22 SAG_03 詳細反省（自動・実購入なし）

- 公式着順：5-3-1-6-4（上位3頭 [5, 3, 1]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 2／2着 4／3着 5；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "SAG_03.r2", "ticket_sha256": "98184c33100683c323a87fc102cd09fa4c01baa55748ceee5cc35fe21ac90566", "frozen_at": "2026-11-22T15:40:01.426787+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 3／3着 4；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 20060／損益 14060／PFS 334.3%
- 参照：{"final_receipt_sha256": "f1f84bd6239187acfac7d7d99237ae090f720ba7ef9ef11c56f3e37761be343d", "result_receipt_sha256": "f6753dfa906dea48f11c8b336783a273428e67f72c81ede45ec0d7f0a3f53042", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "9fa7bc2622dc399cbcfa46c38654abe8ce63404f2edb1ba9a18bfbe48067348a", "signed_final_ticket_count": 105, "signed_final_total_investment": 10500, "signed_final_settlement": {"invest": 10500, "refund": 0, "effective_invest": 10500, "payout": 16170, "pfs": 154.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-22T07:17:20.093656+00:00", "source_receipt_sha256": "33e0460785b4d3bdcf27d130fe7418f76263c2e9933142afc7a4f9dba5d82cc3", "signed_final_at": "2026-11-22T07:17:30.528539+00:00", "delivered_ticket_sha256": "271ff1294ffefe959385e04dddfc96c4eaf5be7c257a29a60ffc8c3445e9624c", "settled_ticket_sha256": "f1f84bd6239187acfac7d7d99237ae090f720ba7ef9ef11c56f3e37761be343d"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 2, "HPI-L": 2}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（グランディオーソ）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 3, "third_pre_rank": 4, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [5, 3, 1], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_CONFIRMED",  |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | OK | {"pfs": 334.3, "profit_loss": 14060, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `497496129697751c`／Learning State `52a48f3b4265`</sub>
