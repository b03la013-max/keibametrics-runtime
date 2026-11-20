# 2026-11-20 KSM_05 詳細反省（自動・実購入なし）

- 公式着順：7-10-4-2-5（上位3頭 [7, 10, 4]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 1／2着 5／3着 7；W True・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 False；Pair条件付き3着 None
- 投資 1600／返還 0／払戻 0／損益 -1600／PFS 0.0%
- 参照：{"revision": "KSM_05.r2", "ticket_sha256": "f7b06356c596f34bea0083aeae0f1e9ae66f1c2f805fa536f02f66d48b3e3649", "frozen_at": "2026-11-20T11:41:36.844524+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 2／3着 6；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 1890／損益 -4110／PFS 31.5%
- 参照：{"final_receipt_sha256": "c37ccb2d8f4d5b9949a10d95a94471e7b73122ad8a7625ee561e3b6c523f192b", "result_receipt_sha256": "7f09144863b5e4e67c1bc482331c137b0f44870acdaab8f38073d0130b64d748", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "a9612a0f9e626a61de85150ba83e37feaf8589a64d6b7d2107102a525d6c4b8e", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 1890, "pfs": 14.3}, "effective_revision": "REVISION_2", "source_at": "2026-11-20T03:16:45.328402+00:00", "source_receipt_sha256": "bcb719890e62661c505a898762a4aa9bbde7871a641c0588790dc7a73bc86d4b", "signed_final_at": "2026-11-20T03:16:53.405783+00:00", "delivered_ticket_sha256": "9865b4397fd5611b0d4f6e5f2f04339ed2423df636b7635a7c90c3eb83136b23", "settled_ticket_sha256": "c37ccb2d8f4d5b9949a10d95a94471e7b73122ad8a7625ee561e3b6c523f192b"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 2, "HPI-L": 1}, "ruled_neutral_share": 0.11} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 2, "third_pre_rank": 6, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [7, 10, 4], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_cov |
| CAPITAL | ISSUE | {"pfs": 31.5, "profit_loss": -4110, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 31.5, "tickets": 60, "payout": 1890} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `af9f6d42e14840ab`／Learning State `b9306cac6e43`</sub>
