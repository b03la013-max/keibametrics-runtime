# 2026-11-19 KSM_06 詳細反省（自動・実購入なし）

- 公式着順：1-5-6-7-9（上位3頭 [1, 5, 6]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 4／2着 3／3着 2；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "KSM_06.r2", "ticket_sha256": "66b6b13b369904567194c3e302b548ef6b623e3c4485ec78eebd003fa340a383", "frozen_at": "2026-11-19T12:15:12.690133+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 3／3着 4；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 19100／損益 13100／PFS 318.3%
- 参照：{"final_receipt_sha256": "30cec064096d860904c59fb3d1ca28dfe89373c6b19fb43878ebe07add9f751e", "result_receipt_sha256": "832611270f626aabae70078fd6ad1ce94207874235969f5aeb14b4c3bacf514f", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "1c97d9678fba694751d2de0533c04ef2cfea5d606efeb95a03993e70e41666ce", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 19100, "pfs": 144.7}, "effective_revision": "REVISION_2", "source_at": null, "signed_final_at": "2026-11-19T03:50:25.080952+00:00", "delivered_ticket_sha256": "6d576455607f41b619ebe7a98c151f1cca5909a77dae233ce84938d5aaee750e", "settled_ticket_sha256": "30cec064096d860904c59fb3d1ca28dfe89373c6b19fb43878ebe07add9f751e"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 2, "T3I-L": 5, "HPI-L": 2}, "ruled_neutral_share": 0.114} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（オパールテソーロ）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 3, "third_pre_rank": 4, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [1, 5, 6], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_CONFIRMED",  |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | OK | {"pfs": 318.3, "profit_loss": 13100, "hit_but_loss": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `4a0f538d3adc5ccb`／Learning State `47007b788d24`</sub>
