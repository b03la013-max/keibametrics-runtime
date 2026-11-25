# 2026-11-25 NGY_06 詳細反省（自動・実購入なし）

- 公式着順：12-6-3-5-7（上位3頭 [12, 6, 3]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：third_in_P3

## PAPER

- 1着の事前順位 9／2着 10／3着 2；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "NGY_06.r2", "ticket_sha256": "39bbdb6eb403b67d34b8774d1ee7dff958a9ff8389de1fbc1005cb3a7e3a113c", "frozen_at": "2026-11-25T16:45:12.269341+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 11／2着 10／3着 3；W False・P2 False・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "26e6a418c2b8fbecefc5bb955e489c5848c2be65d47b2137aa72b160ef43f8b4", "result_receipt_sha256": "27dfdc3a983c476c9228aa5cbc1a35b2859e929bdf7dee8a19ed89baad8d4b18", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "e6122fcb556c2b298bee9c13d3ded4de8ef61e6cf8b7d5fe56b4c4bb9dc17e60", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-25T08:22:11.705648+00:00", "source_receipt_sha256": "3595b97a995e0578b923f1ff38a1b34401c7197e122cb2ea52dc48edb5f96b24", "signed_final_at": "2026-11-25T08:22:24.419341+00:00", "delivered_ticket_sha256": "c8e1878402f9b7cb89d489163531bffa3c97b01c6ff6a875a07846d75e2b8f4a", "settled_ticket_sha256": "26e6a418c2b8fbecefc5bb955e489c5848c2be65d47b2137aa72b160ef43f8b4"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 8, "TPI-L": 7, "SRI-L": 11, "T3I-L": 12, "HPI-L": 4}, "ruled_neutral_share": 0.072} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補6頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 11, "second_pre_rank": 10, "third_pre_rank": 3, "winner_in_W": false, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [12, 6, 3], "rescues": [], "supports": ["P3_ROLE_CONFIRMED"], "misses": [ |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 11, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `c2c53cf5ed6e402f`／Learning State `fb2620408ec1`</sub>
