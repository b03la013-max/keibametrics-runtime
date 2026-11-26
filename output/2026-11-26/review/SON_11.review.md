# 2026-11-26 SON_11 詳細反省（自動・実購入なし）

- 公式着順：7-3-6-12-1（上位3頭 [7, 3, 6]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：third_in_P3

## PAPER

- 1着の事前順位 3／2着 4／3着 9；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "SON_11.r2", "ticket_sha256": "28f843111d52ca8e672a04a09ca8a5542c9fc3e7f4fec1a829c9d63d951e5031", "frozen_at": "2026-11-26T15:30:01.500967+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 9／2着 8／3着 5；W False・P2 False・P3 True
- Top3捕捉 0／Top4捕捉 0；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "607d1a5257c3f6ef676cbbda9d09b59065dee9726620bc45163aeadd168c1649", "result_receipt_sha256": "0688e92d47b0e6df3e1f83203774646f698eeced48d176fdd989bfb53c8d6bae", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "e456133ff66a7e5edf4bb7a30a990b7e78cbcabc708f6f6025a7f800b70c1bcf", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-26T07:05:11.334312+00:00", "source_receipt_sha256": "dc271f0abd8e7f0b5f4400876431fe3a3879162098719299aba470eb23699f2f", "signed_final_at": "2026-11-26T07:05:24.266152+00:00", "delivered_ticket_sha256": "06793fc7224a53492a2b86c59b18b394c733362644321e7394a33ce380aa121d", "settled_ticket_sha256": "607d1a5257c3f6ef676cbbda9d09b59065dee9726620bc45163aeadd168c1649"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 7, "TPI-L": 6, "SRI-L": 9, "T3I-L": 9, "HPI-L": 4}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補4頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 9, "second_pre_rank": 8, "third_pre_rank": 5, "winner_in_W": false, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [7, 3, 6], "rescues": ["P2_ROLE_RESCUE"], "supports": [], "misses": ["WIN |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 9, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `3886c546511e0e52`／Learning State `6b892d07d7d4`</sub>
