# 2026-11-25 URW_03 詳細反省（自動・実購入なし）

- 公式着順：3-11-8-12-5（上位3頭 [3, 11, 8]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 3／2着 2／3着 11；W False・P2 True・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "URW_03.r2", "ticket_sha256": "24edb138319242a4c99a84db9b2ffcd195d08a36416e214d375b0b55e6974a43", "frozen_at": "2026-11-25T12:36:07.320671+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 3／3着 12；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 1860／損益 -4140／PFS 31.0%
- 参照：{"final_receipt_sha256": "2c336c6951da6e645b8220493a07d1eb9f581fa99915c8a50edcd384beb61b7c", "result_receipt_sha256": "b8cc66147e4c0c4698d74b868f40b646d5738bfaea8f9ae05607dcb73f918994", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "941851dda77384e9ec7f9378e0d382befe2088d41352c82e6e0d3f4e7985f10e", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 13670, "pfs": 87.6}, "effective_revision": "REVISION_2", "source_at": "2026-11-25T04:11:03.708199+00:00", "source_receipt_sha256": "d9c0afe978020911d6f3b19ef287a3306d6fe2a37450e8fae1dd14c0298a268c", "signed_final_at": "2026-11-25T04:11:13.513146+00:00", "delivered_ticket_sha256": "d342ca14256989c816cd47fa6ddee2452e1307ea71c18266e573d1c5d879a22f", "settled_ticket_sha256": "2c336c6951da6e645b8220493a07d1eb9f581fa99915c8a50edcd384beb61b7c"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 3, "HPI-L": 4}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補4頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 3, "third_pre_rank": 12, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [3, 11, 8], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED"], "misses |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 31.0, "profit_loss": -4140, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 31.0, "tickets": 60, "payout": 1860} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `dc165f6436ee34dc`／Learning State `d982cd12508f`</sub>
