# 2026-11-27 URW_08 詳細反省（自動・実購入なし）

- 公式着順：2-11-3-10-1（上位3頭 [2, 11, 3]）
- 距離帯：MIDDLE(1701-2100)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 1／2着 3／3着 4；W True・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 1200／損益 500／PFS 171.4%
- 参照：{"revision": "URW_08.r2", "ticket_sha256": "fcdd617fea109f0dc26296d868522f265ac2e83386c69f03386c85367ca67e3a", "frozen_at": "2026-11-27T15:15:07.495613+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 2／3着 3；W True・P2 True・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 8690／損益 2690／PFS 144.8%
- 参照：{"final_receipt_sha256": "d5808a33aef27750ac3b0e429f2b4cce1f220c6655df28ff9a2bdc31b767cf9f", "result_receipt_sha256": "f34a9ca3b9a447a063b3a0fab39a849f2515c856702375c483f8fe37f613d3b7", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "f13322fefd7f4b738e0572882536df8014e624f0c57a7ca17c03f0c0837354b9", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 8690, "pfs": 55.7}, "effective_revision": "REVISION_2", "source_at": "2026-11-27T06:52:05.730931+00:00", "source_receipt_sha256": "61c6ce5b29d7ff702e119d70991263282c2166ecdf8fc575c4d48688e741fee1", "signed_final_at": "2026-11-27T06:52:18.650571+00:00", "delivered_ticket_sha256": "d9dd38718a8090649f1782cdb5ec1bb3bc2b539e926bcb947e35b64ee1315e88", "settled_ticket_sha256": "d5808a33aef27750ac3b0e429f2b4cce1f220c6655df28ff9a2bdc31b767cf9f"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 2, "T3I-L": 4, "HPI-L": 1}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 2, "third_pre_rank": 3, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [2, 11, 3], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_cov |
| CAPITAL | OK | {"pfs": 144.8, "profit_loss": 2690, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `f7619e4db5926383`／Learning State `90984787c2a1`</sub>
