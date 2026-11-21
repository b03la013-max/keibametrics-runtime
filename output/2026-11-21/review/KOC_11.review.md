# 2026-11-21 KOC_11 詳細反省（自動・実購入なし）

- 公式着順：8-7-2-9-6（上位3頭 [8, 7, 2]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 10／2着 6／3着 5；W False・P2 False・P3 False
- Top3捕捉 0／Top4捕捉 0；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "KOC_11.r2", "ticket_sha256": "b4008db1199e3a28add726d968d31c4cb76518f2b1d23a1ff1058017880a48a3", "frozen_at": "2026-11-21T19:35:11.691990+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 11／2着 3／3着 6；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "6acc0053c86cf329a435f371c71cbfa92e365c0c05e9a9125b07505b83103361", "result_receipt_sha256": "4890ff5014b070a99f2d6238b881d183560cf38416ced98964d4e5e6dca03d87", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "a9f5c3e4993d6f256a8f18e5799a168febfd0aaf86d15af0f8cfba19cf1e1902", "signed_final_ticket_count": 144, "signed_final_total_investment": 14400, "signed_final_settlement": {"invest": 14400, "refund": 0, "effective_invest": 14400, "payout": 16090, "pfs": 111.7}, "effective_revision": "REVISION_2", "source_at": "2026-11-21T11:10:02.718777+00:00", "source_receipt_sha256": "d77784b3dc69d6e330a90aa1ac3f92e4ac43e3e52ed8389dc2696c583c640269", "signed_final_at": "2026-11-21T11:10:12.152045+00:00", "delivered_ticket_sha256": "2986d212a3ea7dea4fcb841454225508555b76ef34e264efd0577bbede083675", "settled_ticket_sha256": "6acc0053c86cf329a435f371c71cbfa92e365c0c05e9a9125b07505b83103361"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 11, "TPI-L": 11, "SRI-L": 11, "T3I-L": 11, "HPI-L": 9}, "ruled_neutral_share": 0.116} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補4頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 11, "second_pre_rank": 3, "third_pre_rank": 6, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [8, 7, 2], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CONF |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 11, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `5db7b62c20fddb2e`／Learning State `a2c98652cf1f`</sub>
