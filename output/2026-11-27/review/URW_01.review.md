# 2026-11-27 URW_01 詳細反省（自動・実購入なし）

- 公式着順：3-1-7-8-5（上位3頭 [3, 1, 7]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2

## PAPER

- 1着の事前順位 2／2着 5／3着 7；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "URW_01.r2", "ticket_sha256": "ccea136bf20bbe75229d6ef9d2268da7f9b11787fa7ea87d0b1c1b797bdab1d4", "frozen_at": "2026-11-27T11:35:15.435088+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 4／2着 5／3着 3；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "3c3050181ffa1bdccf06035f1d1bd3b855583e5ffba90a8f03da138149b90cb8", "result_receipt_sha256": "5b5aa42cca79afdde0dab40ea8b87e9a95df83b4fb4c53df7ada161ecc9b27b9", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "fcc4ab213d4931ffcbfecfb30731ea226073c6d91b440804ceede520ff4a7239", "signed_final_ticket_count": 105, "signed_final_total_investment": 10500, "signed_final_settlement": {"invest": 10500, "refund": 0, "effective_invest": 10500, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_1", "source_at": "2026-11-27T02:38:25.156256+00:00", "source_receipt_sha256": "3d064fcdf28aada77951c1fcc36247bea5a95e026ef00049466a0d2f01a812cd", "signed_final_at": "2026-11-27T02:38:35.338719+00:00", "delivered_ticket_sha256": "5dd871ced041357554409596786496273f2e086f4ec54edc32a2160117f82e41", "settled_ticket_sha256": "3c3050181ffa1bdccf06035f1d1bd3b855583e5ffba90a8f03da138149b90cb8"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 4, "TPI-L": 4, "SRI-L": 4, "T3I-L": 5, "HPI-L": 5}, "ruled_neutral_share": 0.078} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 4, "second_pre_rank": 5, "third_pre_rank": 3, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [3, 1, 7], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CONFIRMED"], "mi |
| TICKET | ISSUE | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 4, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `6d62a4df7f84f2e8`／Learning State `51c56672c3de`</sub>
