# 2026-11-28 SAG_01 詳細反省（自動・実購入なし）

- 公式着順：5-1-3-6-8（上位3頭 [5, 1, 3]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 7／2着 1／3着 3；W False・P2 False・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 800／返還 0／払戻 0／損益 -800／PFS 0.0%
- 参照：{"revision": "SAG_01.r2", "ticket_sha256": "346ea4168f467bb66a43fde001d534a087ebb55188c9dfc5397985c9f5f0b052", "frozen_at": "2026-11-28T14:00:20.707969+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 9／2着 1／3着 3；W False・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 820／損益 -5180／PFS 13.7%
- 参照：{"final_receipt_sha256": "3daadc6898310ede76586f37ded00209d7eea5dd40b7f116f63555fe7589c786", "result_receipt_sha256": "23dd943e9ffaae38f5f3c7863ffaa23ecea0260c09ccca31d03c1bd1daf3e781", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "81d3a2713552ed088f3d11e770f1b6bc85a1fe71e6f1131ce10e71bc681a02b8", "signed_final_ticket_count": 144, "signed_final_total_investment": 14400, "signed_final_settlement": {"invest": 14400, "refund": 0, "effective_invest": 14400, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-28T05:37:14.775668+00:00", "source_receipt_sha256": "3a2cabbb2cfa9790fc45ef60fd9ab2a67e4fe6a2cfb20bd7fc477a80f6768156", "signed_final_at": "2026-11-28T05:37:27.719999+00:00", "delivered_ticket_sha256": "3b69d25d7f8503f3086edcbf1b577ada9366bc09710c99e8d41ae49d28377484", "settled_ticket_sha256": "3daadc6898310ede76586f37ded00209d7eea5dd40b7f116f63555fe7589c786"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 2, "SRI-L": 6, "T3I-L": 3, "HPI-L": 2}, "ruled_neutral_share": 0.094} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（タルボステソーロ）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 9, "second_pre_rank": 1, "third_pre_rank": 3, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [5, 1, 3], "rescues": ["WINNER_ROLE_RESCUE", "ORDERED_PAIR_RESCUE", "PAIR |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_cov |
| CAPITAL | ISSUE | {"pfs": 13.7, "profit_loss": -5180, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 9, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P1:HIT_BUT_LOSS | P1 | {"pfs": 13.7, "tickets": 60, "payout": 820} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `e16420c3101c99a4`／Learning State `114a62c0254e`</sub>
