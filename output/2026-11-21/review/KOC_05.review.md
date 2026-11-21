# 2026-11-21 KOC_05 詳細反省（自動・実購入なし）

- 公式着順：10-8-12-3-11（上位3頭 [10, 8, 12]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_P2**
- 正しく判断できた項目：winner_in_W, third_in_P3, winner_is_ticket_head

## PAPER

- 1着の事前順位 3／2着 6／3着 11；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "KOC_05.r2", "ticket_sha256": "edb2a3300c08f66593912e34d3244107f61023631a425d111acc51d2758f8db2", "frozen_at": "2026-11-21T16:31:09.642679+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 3／2着 8／3着 7；W True・P2 False・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 False；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "f74dd9f232965a455a43cf4f5a87e9c91c7edf85d2f613eb47d753e5b88ec08a", "result_receipt_sha256": "746e1d00d2f682fc9ddc2bbc834cc1226eea4d29ef220c148460203ed7a42144", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "e739e8b1cec7ef550769a949ee0d87608ef006dec060803f554f616be4a1d8a9", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-21T08:05:03.080678+00:00", "source_receipt_sha256": "2b5e9613d72e3b354ab8b34bef926aa59b4900251faf3c6d0ac93e5c1f5d31d5", "signed_final_at": "2026-11-21T08:05:12.599819+00:00", "delivered_ticket_sha256": "dd16d5e1dd17a35d80ce5bf65cb47273057b4cc9c5f692eb7d78ee9e91db9a82", "settled_ticket_sha256": "f74dd9f232965a455a43cf4f5a87e9c91c7edf85d2f613eb47d753e5b88ec08a"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 2, "T3I-L": 7, "HPI-L": 2}, "ruled_neutral_share": 0.124} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 3, "second_pre_rank": 8, "third_pre_rank": 7, "winner_in_W": true, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [10, 8, 12], "rescues": ["P2_ROLE_RESCUE", "ORDERED_PAIR_RESCUE"], "suppo |
| TICKET | ISSUE | {"head_local_p2": false, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 8} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `229db561b48d1355`／Learning State `8e89fc07429f`</sub>
