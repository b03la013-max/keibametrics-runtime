# 2026-11-26 KNZ_11 詳細反省（自動・実購入なし）

- 公式着順：3-1-7-2-6（上位3頭 [3, 1, 7]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 1／2着 5／3着 6；W True・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 False；Pair条件付き3着 None
- 投資 1600／返還 0／払戻 0／損益 -1600／PFS 0.0%
- 参照：{"revision": "KNZ_11.r2", "ticket_sha256": "ece7f5f3ac5e3947d273402686106f973ca1a720cfeabcf04259112219c35a45", "frozen_at": "2026-11-26T19:15:16.063188+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 4／3着 6；W True・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 18760／損益 12760／PFS 312.7%
- 参照：{"final_receipt_sha256": "f78d22d40f95c47b151ad84be48f9029e5159f0afa6173b9b4bfdb016fa2dd8d", "result_receipt_sha256": "c7d163c14e1820dc93766e1b1336a3c5159b2bf4652c6de581e5920674e3a425", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "06c2547d52e030ee86eb4520e4d4e5c0048cfd220eedfac722d635173121bba0", "signed_final_ticket_count": 120, "signed_final_total_investment": 12000, "signed_final_settlement": {"invest": 12000, "refund": 0, "effective_invest": 12000, "payout": 12620, "pfs": 105.2}, "effective_revision": "REVISION_2", "source_at": "2026-11-26T10:52:15.800382+00:00", "source_receipt_sha256": "f0faf3662d77efda588dcf1f208f5fbf16d1c2f45a8bdb6f71f46ebf4d9636f7", "signed_final_at": "2026-11-26T10:52:27.983310+00:00", "delivered_ticket_sha256": "65223e3e48b749f823e9a3c0f5ca952fcc339033516f351f09feca71d638a32b", "settled_ticket_sha256": "f78d22d40f95c47b151ad84be48f9029e5159f0afa6173b9b4bfdb016fa2dd8d"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 4, "HPI-L": 1}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 4, "third_pre_rank": 6, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [3, 1, 7], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P3_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | OK | {"pfs": 312.7, "profit_loss": 12760, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `64eabf4f3bc131d4`／Learning State `4fad2206dec6`</sub>
