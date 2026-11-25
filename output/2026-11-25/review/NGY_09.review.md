# 2026-11-25 NGY_09 詳細反省（自動・実購入なし）

- 公式着順：12-4-9-5-8（上位3頭 [12, 4, 9]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 5／2着 6／3着 2；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "NGY_09.r2", "ticket_sha256": "cb1ead15b6f6d6ae065fbb49afeef89991d42a0fc228c0c41daa17c85bc7a7cc", "frozen_at": "2026-11-25T18:20:16.042598+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 3／3着 1；W True・P2 True・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 6270／損益 270／PFS 104.5%
- 参照：{"final_receipt_sha256": "423013c93666e451452d826862b6a19e1318a500e44e164d16430c4e6d8fa8fc", "result_receipt_sha256": "0bd44f9d4283a19540b368cf7b29c4c80c74bfd34f970764b43dd6beaafa4598", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "b685ee8c55425f09e4a0bb863cb82931af2e5721a424272eb3e088dbb6b693bd", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 5860, "pfs": 37.6}, "effective_revision": "REVISION_2", "source_at": "2026-11-25T09:57:17.569690+00:00", "source_receipt_sha256": "92b8985c81ae89636433d0e546e51291c68257a35e0be9a9de98986cba7a581b", "signed_final_at": "2026-11-25T09:57:30.836332+00:00", "delivered_ticket_sha256": "9b1f7d5adc1606476991379bf161f762fab12cb42778086930d8346f71eafb61", "settled_ticket_sha256": "423013c93666e451452d826862b6a19e1318a500e44e164d16430c4e6d8fa8fc"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 5, "TPI-L": 5, "SRI-L": 6, "T3I-L": 8, "HPI-L": 4}, "ruled_neutral_share": 0.072} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補4頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 3, "third_pre_rank": 1, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [12, 4, 9], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CON |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | OK | {"pfs": 104.5, "profit_loss": 270, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `5200006fbb693065`／Learning State `af720fb1b539`</sub>
