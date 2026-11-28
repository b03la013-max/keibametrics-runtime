# 2026-11-28 SAG_04 詳細反省（自動・実購入なし）

- 公式着順：11-7-5-3-9（上位3頭 [11, 7, 5]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 1／2着 3／3着 10；W True・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 1600／返還 0／払戻 1310／損益 -290／PFS 81.9%
- 参照：{"revision": "SAG_04.r2", "ticket_sha256": "5582c46b9c379d6ae82e365016f5bebb5e756fdea489fb8b877ab7c73a79fb23", "frozen_at": "2026-11-28T15:45:14.296727+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 5／3着 7；W True・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 1310／損益 -4690／PFS 21.8%
- 参照：{"final_receipt_sha256": "aecce357a0d07883eefaa250b17d3865b251b846a05d078a69727c2c91377685", "result_receipt_sha256": "72147a29fc616650b757b9bbe984a9431b7cfdf6cf959b6fbfa7a361c1d7b1f2", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "dfade1f9c9a17b9689399bccc797df907ad019694d2f8110bb9af7993b1f12ec", "signed_final_ticket_count": 144, "signed_final_total_investment": 14400, "signed_final_settlement": {"invest": 14400, "refund": 0, "effective_invest": 14400, "payout": 22250, "pfs": 154.5}, "effective_revision": "REVISION_2", "source_at": "2026-11-28T07:20:17.382844+00:00", "source_receipt_sha256": "4bae4714474cc8ecb3bc8aacb5e81622c646a9866b3c488504a1dfc2852f3d97", "signed_final_at": "2026-11-28T07:20:30.452910+00:00", "delivered_ticket_sha256": "ddb8b4d276d0bb9f3893874318ac9c79895aaa1dcb76e0eff04e2559bc42afe4", "settled_ticket_sha256": "aecce357a0d07883eefaa250b17d3865b251b846a05d078a69727c2c91377685"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 5, "HPI-L": 1}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 5, "third_pre_rank": 7, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [11, 7, 5], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P3_ROLE |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 21.8, "profit_loss": -4690, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 21.8, "tickets": 60, "payout": 1310} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `ea6b6a89c13c286e`／Learning State `e1da51012f65`</sub>
