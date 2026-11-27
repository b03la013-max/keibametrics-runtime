# 2026-11-27 SON_06 詳細反省（自動・実購入なし）

- 公式着順：1-2-10-7-8（上位3頭 [1, 2, 10]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2

## PAPER

- 1着の事前順位 7／2着 4／3着 3；W False・P2 False・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "SON_06.r2", "ticket_sha256": "eaa1039f65583b753bbe6ef6c1c5520df133d094ad6354720aa0e22038b70bcf", "frozen_at": "2026-11-27T12:35:13.162702+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 4／2着 5／3着 3；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "8b8d7887edd5169d147dda922872e491afb9c5b0cc26ad70e7818552ede7cf51", "result_receipt_sha256": "dbffe0427fe51d31be564cc514447014cff79d3c23961307f8e4bd2f3773e300", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "3bb9e9860dff103270ebed677cdb962be5cb8097bff3baa86f6326ab4a493b98", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-27T04:10:07.717160+00:00", "source_receipt_sha256": "c3896743e329df111beda0750ca950e396e6e230e1da167c0ad61d42c64eac6b", "signed_final_at": "2026-11-27T04:10:20.313513+00:00", "delivered_ticket_sha256": "856f22401ed7e17e6539a59be7ab30f8a3d49c27db0be42e5d575cf957c92579", "settled_ticket_sha256": "8b8d7887edd5169d147dda922872e491afb9c5b0cc26ad70e7818552ede7cf51"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 1, "HPI-L": 1}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 4, "second_pre_rank": 5, "third_pre_rank": 3, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [1, 2, 10], "rescues": ["WINNER_ROLE_RESCUE", "ORDERED_PAIR_RESCUE"], "su |
| TICKET | ISSUE | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 4, "alternative_signals_that_had_winner_top": ["F3S-L ranked the winner #1", "TPI-L ranked the winne | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `6f629b004b13de3f`／Learning State `7cd800a6a90d`</sub>
