# 2026-11-20 OHI_05 詳細反省（自動・実購入なし）

- 公式着順：11-5-10-2-9（上位3頭 [11, 5, 10]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 3／2着 2／3着 5；W False・P2 True・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "OHI_05.r2", "ticket_sha256": "dcf086666a3ea9ec676db721807807559cca59c8b4fb64883879786d93cbead1", "frozen_at": "2026-11-20T15:56:00.136531+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 7／2着 1／3着 5；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "128b7b063366ee89938c82ef05e334f8287f3063edcc3e27275fa2a29e5d0e7f", "result_receipt_sha256": "bf1d0cc398c9cb6df4fddf04cbd07987f01f2cfde3f733801bf57033b8594e1d", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "81619d1d272d2b0ee40da86e594bec2a2446acdc3ace4be1ca34445dfa651e64", "signed_final_ticket_count": 180, "signed_final_total_investment": 18000, "signed_final_settlement": {"invest": 18000, "refund": 0, "effective_invest": 18000, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-20T07:32:11.951681+00:00", "source_receipt_sha256": "19aff75d4f00a150f771bb1f6e9b0486e14f53984a6f9b6b7202ee9a594f8940", "signed_final_at": "2026-11-20T07:32:22.991942+00:00", "delivered_ticket_sha256": "42f4220ade79da3c7f111f867f9eafd8da43b2e60778bad870aefe5a0ff7ed60", "settled_ticket_sha256": "128b7b063366ee89938c82ef05e334f8287f3063edcc3e27275fa2a29e5d0e7f"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 5, "TPI-L": 5, "SRI-L": 7, "T3I-L": 1, "HPI-L": 6}, "ruled_neutral_share": 0.106} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補4頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 7, "second_pre_rank": 1, "third_pre_rank": 5, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [11, 5, 10], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CO |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 7, "alternative_signals_that_had_winner_top": ["T3I-L ranked the winner #1"]} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `910f74ab5aa50607`／Learning State `4e5aac67a7f3`</sub>
