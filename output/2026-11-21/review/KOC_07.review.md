# 2026-11-21 KOC_07 詳細反省（自動・実購入なし）

- 公式着順：8-9-2-1-6（上位3頭 [8, 9, 2]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 1／2着 3／3着 7；W True・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "KOC_07.r2", "ticket_sha256": "3e81da2ccc32f1bdb43d7abf84d54ae97851f9114a4044bfa24e48beba7b4131", "frozen_at": "2026-11-21T17:30:16.669307+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 3／2着 4／3着 8；W True・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 440／損益 -5560／PFS 7.3%
- 参照：{"final_receipt_sha256": "71583e3c553dda9bcefff1b3e887c1205c1eabb0917790631456a2c5ab6cb7c1", "result_receipt_sha256": "4b9373defed569e8e25773e502687356a1da9b374061decb10c1acc4ef4e47ef", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "b92f1c0a1350006a9f7f76004afdd64f046881bbbe50b2aa862d0019d8a15402", "signed_final_ticket_count": 120, "signed_final_total_investment": 12000, "signed_final_settlement": {"invest": 12000, "refund": 0, "effective_invest": 12000, "payout": 2220, "pfs": 18.5}, "effective_revision": "REVISION_2", "source_at": "2026-11-21T09:06:11.333027+00:00", "source_receipt_sha256": "44fd404289706218ba6a51817f608f12213f23e5ee4e0d897fc5b5ab5a10c1c5", "signed_final_at": "2026-11-21T09:06:19.456888+00:00", "delivered_ticket_sha256": "3064319f840b6a6a01569d71510f65b87ba0eac9f5501076f0ab30edb6e76595", "settled_ticket_sha256": "71583e3c553dda9bcefff1b3e887c1205c1eabb0917790631456a2c5ab6cb7c1"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 2, "T3I-L": 3, "HPI-L": 2}, "ruled_neutral_share": 0.111} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 3, "second_pre_rank": 4, "third_pre_rank": 8, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [8, 9, 2], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "ORDERED_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 7.3, "profit_loss": -5560, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 7.3, "tickets": 60, "payout": 440} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `3580d72557a1a7e6`／Learning State `41fee9fbcb2e`</sub>
