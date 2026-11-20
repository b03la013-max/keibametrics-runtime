# 2026-11-20 OHI_08 詳細反省（自動・実購入なし）

- 公式着順：4-11-5-12-1（上位3頭 [4, 11, 5]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 2／2着 8／3着 5；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "OHI_08.r2", "ticket_sha256": "a5307a930abbccb0594d42bc403cbe5bd10cf90bc8cec879203b95cb629817bf", "frozen_at": "2026-11-20T17:35:48.256384+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 4／2着 5／3着 7；W False・P2 True・P3 True
- Top3捕捉 0／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "9ef2cff532ae0e30ee0aadb6ae1c6772f0eabc73f1fa12e7a4970dcff74a06ef", "result_receipt_sha256": "f63505dfc3842838f1232b6b10bd8d2e46f672214c3fe218142db7175da6ba57", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "478ebb52f968277b56497979a41b37ebe7006cc0fa1a587564279f793e72d6f0", "signed_final_ticket_count": 168, "signed_final_total_investment": 16800, "signed_final_settlement": {"invest": 16800, "refund": 0, "effective_invest": 16800, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-20T09:13:27.373388+00:00", "source_receipt_sha256": "e47b15adc9dc5079b3f7945bdf450d368c7467afb8879e4a38406cfb661654d1", "signed_final_at": "2026-11-20T09:13:38.317555+00:00", "delivered_ticket_sha256": "c30cdc55a759aa64db050e66e6391a59785eaf15868a4ba6cd715186b6a01318", "settled_ticket_sha256": "9ef2cff532ae0e30ee0aadb6ae1c6772f0eabc73f1fa12e7a4970dcff74a06ef"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 6, "SRI-L": 3, "T3I-L": 5, "HPI-L": 3}, "ruled_neutral_share": 0.119} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 4, "second_pre_rank": 5, "third_pre_rank": 7, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [4, 11, 5], "rescues": ["WINNER_ROLE_RESCUE"], "supports": ["P2_ROLE_CONF |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 4, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `34254880681cd979`／Learning State `6697a0d91bd7`</sub>
