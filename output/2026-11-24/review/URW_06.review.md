# 2026-11-24 URW_06 詳細反省（自動・実購入なし）

- 公式着順：4-1-5-9-6（上位3頭 [4, 1, 5]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 2／2着 4／3着 1；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 590／損益 -110／PFS 84.3%
- 参照：{"revision": "URW_06.r2", "ticket_sha256": "11e92c14e8b3d883334098403d584a2d484c669e80f9b87a33d27b5031652963", "frozen_at": "2026-11-24T14:06:39.082573+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 4／3着 3；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 5320／損益 -680／PFS 88.7%
- 参照：{"final_receipt_sha256": "ad4d66c286d548f32084ad5ef242b4e3f759d7a4770df1194155e43f0f5d0fbf", "result_receipt_sha256": "1865d87d434380f452c41633dd0062e0ff51e3ea6d487633e0671304139b54b2", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "b3106b8d35160fa1e9299f1cfba60693892154b1aba699eb24cffa2e2a321612", "signed_final_ticket_count": 168, "signed_final_total_investment": 16800, "signed_final_settlement": {"invest": 16800, "refund": 0, "effective_invest": 16800, "payout": 4870, "pfs": 29.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-24T05:42:57.176408+00:00", "source_receipt_sha256": "7e301c5750cc47b47f9dd0f0caebe39e29a8f10a272dfc2c04b900e86df38e9c", "signed_final_at": "2026-11-24T05:43:10.748335+00:00", "delivered_ticket_sha256": "26ed78ccf824e089457a5bc1dc38ecf2d698d9e5428752ec64c4a1663d07639f", "settled_ticket_sha256": "ad4d66c286d548f32084ad5ef242b4e3f759d7a4770df1194155e43f0f5d0fbf"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 1, "HPI-L": 1}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補4頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 4, "third_pre_rank": 3, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [4, 1, 5], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 88.7, "profit_loss": -680, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 88.7, "tickets": 60, "payout": 5320} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `30311133528829c6`／Learning State `46f478167172`</sub>
