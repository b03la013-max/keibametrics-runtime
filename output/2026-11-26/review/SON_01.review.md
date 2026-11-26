# 2026-11-26 SON_01 詳細反省（自動・実購入なし）

- 公式着順：8-2-9-5-4（上位3頭 [8, 2, 9]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 1／2着 5／3着 9；W True・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 4040／損益 3340／PFS 577.1%
- 参照：{"revision": "SON_01.r2", "ticket_sha256": "22a02a52dcb3d29a20fc43b907138792121d749f4083364d8664ac5784d6768a", "frozen_at": "2026-11-26T09:56:22.622747+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 5／3着 11；W True・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 800／損益 -5200／PFS 13.3%
- 参照：{"final_receipt_sha256": "751d48d89e777c2c084ba178ee298c36d3dd42aa6ac19bd54fb605928208e463", "result_receipt_sha256": "c890b73c55e2111092dff42e661a594ad851dcd6584e79e0879ab5966e314a8a", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "98e5736475ab3f36268a46918fae8622670867251c4fd7efacc538acab606183", "signed_final_ticket_count": 144, "signed_final_total_investment": 14400, "signed_final_settlement": {"invest": 14400, "refund": 0, "effective_invest": 14400, "payout": 29980, "pfs": 208.2}, "effective_revision": "REVISION_2", "source_at": "2026-11-26T01:30:19.479990+00:00", "source_receipt_sha256": "f1dd45c02d424a5d9a0c50fdfb0d004757fabe5ed81556a99bde33c1c0c24047", "signed_final_at": "2026-11-26T01:30:31.867365+00:00", "delivered_ticket_sha256": "78e676741fc20e62f0a5aedaf61f2b0e51273bbad5530b3f4a99920072d557af", "settled_ticket_sha256": "751d48d89e777c2c084ba178ee298c36d3dd42aa6ac19bd54fb605928208e463"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 2, "HPI-L": 1}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 5, "third_pre_rank": 11, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [8, 2, 9], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 13.3, "profit_loss": -5200, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 13.3, "tickets": 60, "payout": 800} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `636f0f7b3053d358`／Learning State `a0ae90f25325`</sub>
