# 2026-11-21 KOC_06 詳細反省（自動・実購入なし）

- 公式着順：3-8-10-1-7（上位3頭 [3, 8, 10]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 1／2着 2／3着 3；W True・P2 True・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 790／損益 90／PFS 112.9%
- 参照：{"revision": "KOC_06.r2", "ticket_sha256": "2decdf3918db87ed83bd05e65c875e219d67b2473ff2f0e92631cd22affffbc0", "frozen_at": "2026-11-21T17:00:07.197814+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 1／3着 3；W True・P2 True・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 7010／損益 1010／PFS 116.8%
- 参照：{"final_receipt_sha256": "8bd5755bbe0f62165895581e8c1622f8a0c1da0da43b82ed8087364fbd49fe56", "result_receipt_sha256": "ba085e3e2702b218c63a0766dd910c242e0c506aaf131dd6976e85b585ecb157", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "eaf58c8d24e90e02815c370ae7d26571a365eaf9d195d80f809a6ebd465d1c9a", "signed_final_ticket_count": 144, "signed_final_total_investment": 14400, "signed_final_settlement": {"invest": 14400, "refund": 0, "effective_invest": 14400, "payout": 7010, "pfs": 48.7}, "effective_revision": "REVISION_1", "source_at": "2026-11-21T08:02:29.688063+00:00", "source_receipt_sha256": "7897849bcc22dbc19c572956461706db85fd8713447c783f3bd56bbdd1b797da", "signed_final_at": "2026-11-21T08:02:38.965989+00:00", "delivered_ticket_sha256": "0b7f83b04c7d04acf551f7206da9cf85eb0287c3f4fae82b74f92fd8444ea87c", "settled_ticket_sha256": "8bd5755bbe0f62165895581e8c1622f8a0c1da0da43b82ed8087364fbd49fe56"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 2, "SRI-L": 1, "T3I-L": 2, "HPI-L": 2}, "ruled_neutral_share": 0.116} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 1, "third_pre_rank": 3, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [3, 8, 10], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_cov |
| CAPITAL | OK | {"pfs": 116.8, "profit_loss": 1010, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `fbcc1e9783659362`／Learning State `4439fb557515`</sub>
