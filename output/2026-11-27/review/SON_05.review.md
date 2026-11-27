# 2026-11-27 SON_05 詳細反省（自動・実購入なし）

- 公式着順：5-9-10-4-7（上位3頭 [5, 9, 10]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 2／2着 3／3着 7；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "SON_05.r2", "ticket_sha256": "461199bfc8176a375011b30935eb0f25554130073e4633e69f65c421c3f021a8", "frozen_at": "2026-11-27T12:00:13.862415+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 5／2着 2／3着 7；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 2720／損益 -3280／PFS 45.3%
- 参照：{"final_receipt_sha256": "72ed6031037b363bd845d4687dccaaa54e9bce4ccf475b53e7660391b5d92bcd", "result_receipt_sha256": "9e5efd51e3e5e04d1f6c7ee35e009cfc57e6ba5b866c5c9acb994678c04b9eed", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "f5efa876a0984936f04ad70a470105b645c0e54295a3c843f0a37f0c361af950", "signed_final_ticket_count": 144, "signed_final_total_investment": 14400, "signed_final_settlement": {"invest": 14400, "refund": 0, "effective_invest": 14400, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_1", "source_at": "2026-11-27T03:03:17.283671+00:00", "source_receipt_sha256": "151ef1eea23b47bbf33cf270abc26aa1baf833372496eaa6e75071a068560d38", "signed_final_at": "2026-11-27T03:03:29.137809+00:00", "delivered_ticket_sha256": "7e775ffa0ec34b8f44dc046cfee319a766c5267da3903e2677f2d83427bcbc4c", "settled_ticket_sha256": "72ed6031037b363bd845d4687dccaaa54e9bce4ccf475b53e7660391b5d92bcd"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 3, "SRI-L": 3, "T3I-L": 3, "HPI-L": 2}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 5, "second_pre_rank": 2, "third_pre_rank": 7, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [5, 9, 10], "rescues": ["WINNER_ROLE_RESCUE", "ORDERED_PAIR_RESCUE"], "su |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 45.3, "profit_loss": -3280, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 5, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P1:HIT_BUT_LOSS | P1 | {"pfs": 45.3, "tickets": 60, "payout": 2720} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `854ab36993487c85`／Learning State `9f78c209d793`</sub>
