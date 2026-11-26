# 2026-11-26 URW_03 詳細反省（自動・実購入なし）

- 公式着順：6-11-1-4-3（上位3頭 [6, 11, 1]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 2／2着 1／3着 3；W False・P2 False・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 890／損益 190／PFS 127.1%
- 参照：{"revision": "URW_03.r2", "ticket_sha256": "ae3c4ce5852384eddda117a5f85396030872060aa522f09cc85adc15df430c8f", "frozen_at": "2026-11-26T12:36:06.725102+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 3／3着 1；W True・P2 True・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 1220／損益 -4780／PFS 20.3%
- 参照：{"final_receipt_sha256": "82d3aa81f9c43fc25c47755cedf4f0c0f4234ebe72dbd72a8c24720aed34a4d0", "result_receipt_sha256": "56710abc134a97cc045d16aeed6364fd6f930eeb82807abda778c3713f5fac11", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "c27ae66aa0a6cda68418a51bc5bba25734fcc8e236fc20f8c0b217e9d2da8452", "signed_final_ticket_count": 144, "signed_final_total_investment": 14400, "signed_final_settlement": {"invest": 14400, "refund": 0, "effective_invest": 14400, "payout": 3210, "pfs": 22.3}, "effective_revision": "REVISION_1", "source_at": "2026-11-26T03:40:08.942982+00:00", "source_receipt_sha256": "c234eeb61b9cbbae379315fd8a394c445b198a6f09ab318e1e7ab5997e3f816a", "signed_final_at": "2026-11-26T03:40:18.239103+00:00", "delivered_ticket_sha256": "fde64df1727eb91467d914384622aeb4cf1866530c1bee87e64711ed9f341c0b", "settled_ticket_sha256": "82d3aa81f9c43fc25c47755cedf4f0c0f4234ebe72dbd72a8c24720aed34a4d0"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 3, "HPI-L": 1}, "ruled_neutral_share": 0.075} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 3, "third_pre_rank": 1, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [6, 11, 1], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 20.3, "profit_loss": -4780, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 20.3, "tickets": 60, "payout": 1220} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `777e846598cf82a9`／Learning State `6c6da13d9017`</sub>
