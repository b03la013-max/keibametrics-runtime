# 2026-11-27 SON_04 詳細反省（自動・実購入なし）

- 公式着順：9-5-2-10-3（上位3頭 [9, 5, 2]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 4／2着 2／3着 1；W False・P2 True・P3 False
- Top3捕捉 2／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 490／損益 -210／PFS 70.0%
- 参照：{"revision": "SON_04.r2", "ticket_sha256": "b8b3f6057f92bb5225c96b4454d74e0944bb1e7af5f1bbe8c76f8bf62f09954d", "frozen_at": "2026-11-27T11:25:10.360886+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 3／2着 2／3着 1；W True・P2 True・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 2840／損益 -3160／PFS 47.3%
- 参照：{"final_receipt_sha256": "17754ac3c68dc073a1001fe3f5e9b69aa6e8a9076066d18a0e99f18244eef9d3", "result_receipt_sha256": "2bf86efe8869a8eec6b030765dab1335cbd9b0364d9342ebe111b39f9b806d46", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "1ece3ad416cedef09c0247c9bbd289bcef98cb06cffd2c2da82f7e736b6305d8", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 2840, "pfs": 21.5}, "effective_revision": "REVISION_2", "source_at": "2026-11-27T03:02:17.391679+00:00", "source_receipt_sha256": "fb56559de3ebb328e755faa374d348fe80c202e9d4421b17af79869205f63a01", "signed_final_at": "2026-11-27T03:02:28.519380+00:00", "delivered_ticket_sha256": "08a317266bb0bc7091432a6edf1b275ccc27cf4ff01785d4a07d01635170b59b", "settled_ticket_sha256": "17754ac3c68dc073a1001fe3f5e9b69aa6e8a9076066d18a0e99f18244eef9d3"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 3, "SRI-L": 3, "T3I-L": 4, "HPI-L": 5}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（ウインリフレクト）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 3, "second_pre_rank": 2, "third_pre_rank": 1, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [9, 5, 2], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CONF |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_cov |
| CAPITAL | ISSUE | {"pfs": 47.3, "profit_loss": -3160, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 47.3, "tickets": 60, "payout": 2840} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `a65531059b00b5a2`／Learning State `fbebef1744be`</sub>
