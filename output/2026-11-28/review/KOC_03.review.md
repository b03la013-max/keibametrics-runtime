# 2026-11-28 KOC_03 詳細反省（自動・実購入なし）

- 公式着順：10-7-6-2-3（上位3頭 [10, 7, 6]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 3／2着 7／3着 4；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "KOC_03.r2", "ticket_sha256": "eb3b71b04f0d16e9a39f2328270eb90fd8a1a841e706de709f44540549f0a23e", "frozen_at": "2026-11-28T15:20:02.749648+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 5／3着 4；W True・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 25690／損益 19690／PFS 428.2%
- 参照：{"final_receipt_sha256": "c3a4b281269a87a64a09918a077643ac595a53a7000fa15824dae379505749ce", "result_receipt_sha256": "e2a467213ed59227ddcb9a2c94f69aacb72049d7a0728dbef9ab6a4b82623f3d", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "8a71ec70141eacc0792453a356cf8b444c7e8422d1f045919c6609cade682ec4", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 25690, "pfs": 194.6}, "effective_revision": "REVISION_2", "source_at": "2026-11-28T06:55:03.882168+00:00", "source_receipt_sha256": "ad229cca3c57a9538a8e6be6ad3e1445a60daaf0d12d6206e1d59c7028782448", "signed_final_at": "2026-11-28T06:55:15.523837+00:00", "delivered_ticket_sha256": "beb0cbe3b7f3ce5049b1993bd47405950f8d7f694aa88470ec2fdd5a76caf893", "settled_ticket_sha256": "c3a4b281269a87a64a09918a077643ac595a53a7000fa15824dae379505749ce"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 3, "SRI-L": 1, "T3I-L": 3, "HPI-L": 3}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 5, "third_pre_rank": 4, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [10, 7, 6], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P3_ROLE |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_cov |
| CAPITAL | OK | {"pfs": 428.2, "profit_loss": 19690, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `315f94b0133ce9eb`／Learning State `746502fa72f6`</sub>
