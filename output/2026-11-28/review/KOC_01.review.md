# 2026-11-28 KOC_01 詳細反省（自動・実購入なし）

- 公式着順：6-10-7-8-1（上位3頭 [6, 10, 7]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**PREDICTION_ROLE_P2**
- 正しく判断できた項目：winner_in_W, third_in_P3, winner_is_ticket_head

## PAPER

- 1着の事前順位 1／2着 7／3着 2；W True・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 120／損益 -580／PFS 17.1%
- 参照：{"revision": "KOC_01.r2", "ticket_sha256": "5698e96cd2b3633e79d7f0ac28ba68c4ea72d6221fecad7ad4fda1b4bef953ca", "frozen_at": "2026-11-28T14:10:17.007575+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 8／3着 1；W True・P2 False・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 False；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "21087602d5496d3fc67998ab9683f46b4c6170233e2da2f5d4ff34e02b151dd5", "result_receipt_sha256": "db0fff06a79538cbb505bcbb6eab7296d4e87e56036ced8fcdecd4b2687443eb", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "896f975dcfd2cf0cda3d435fdea53ec0f044649c2c9b820e27dee6bc75bd6d50", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-28T05:47:14.038864+00:00", "source_receipt_sha256": "6d8685a3d978d33b652e603c93f64be3f59c0662bd4179518b0721d29fc725f5", "signed_final_at": "2026-11-28T05:47:25.217641+00:00", "delivered_ticket_sha256": "d9e51ae13fd9f9f4803eaa8ddb0130ff750929212ca4c1ccadb413df1eec652b", "settled_ticket_sha256": "21087602d5496d3fc67998ab9683f46b4c6170233e2da2f5d4ff34e02b151dd5"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 3, "T3I-L": 3, "HPI-L": 1}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（ヤマシュウ）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 2, "second_pre_rank": 8, "third_pre_rank": 1, "winner_in_W": true, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [6, 10, 7], "rescues": ["P2_ROLE_RESCUE", "ORDERED_PAIR_RESCUE", "PAIR_TH |
| TICKET | ISSUE | {"head_local_p2": false, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 8} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `cbc73cc99d6650ab`／Learning State `d291e67f677d`</sub>
