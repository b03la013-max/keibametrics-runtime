# 2026-11-24 NGY_12 詳細反省（自動・実購入なし）

- 公式着順：9-4-1-12-3（上位3頭 [9, 4, 1]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 3／2着 2／3着 1；W False・P2 True・P3 False
- Top3捕捉 3／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 1260／損益 560／PFS 180.0%
- 参照：{"revision": "NGY_12.r2", "ticket_sha256": "2da2d304abd294806b05616253962b5bb9037ce1ff96c298733d85fefea2abbc", "frozen_at": "2026-11-24T20:05:18.270106+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 1／3着 9；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 2690／損益 -3310／PFS 44.8%
- 参照：{"final_receipt_sha256": "0e8b765aa34b29cb3e3a3cae7ad058f2f26816c6ee1c45a2f614eabc7001c8ca", "result_receipt_sha256": "d1151ae9ec7626c59f34e57e58663927a56092603515c284420f6198f4a5e67e", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "052c4a4a7a201eb0975d9c8104d9dc16205dd31996a2eff79b496214e0d66705", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 11710, "pfs": 75.1}, "effective_revision": "REVISION_2", "source_at": "2026-11-24T11:44:19.086234+00:00", "source_receipt_sha256": "614699960714784859d417be02f5d28bf3d43dac0147441168642abbfb3ece69", "signed_final_at": "2026-11-24T11:44:40.221508+00:00", "delivered_ticket_sha256": "376583bc173afbfba179eac0713880f6427a849cd444a94ea6c6a312df91cfc4", "settled_ticket_sha256": "0e8b765aa34b29cb3e3a3cae7ad058f2f26816c6ee1c45a2f614eabc7001c8ca"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 1, "T3I-L": 4, "HPI-L": 5}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（ニホンピロデルマー）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 1, "third_pre_rank": 9, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [9, 4, 1], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 44.8, "profit_loss": -3310, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 44.8, "tickets": 60, "payout": 2690} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `e76b096bbf42a7a8`／Learning State `a0262fa1be1b`</sub>
